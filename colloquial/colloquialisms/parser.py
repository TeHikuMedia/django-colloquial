# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re
from datetime import timedelta
import codecs

from pyvtt import WebVTTFile

# match accented vowels as well. Must be contained in a []
EXTRA_WORD = u'āēīōū'
MATCH_WORD = u'\w%s' % EXTRA_WORD

# TODO write a proper parser, or use BeautifulSoup, instead of regexes
# NOTE nested tags are not supported, but they shouldn't be nested anyway

# regular voice spans <v NAME>...</v>
VOICE_SPAN_RE = re.compile(
    u'<v ([%s]+)>(.+)</v>?' % MATCH_WORD, flags=re.IGNORECASE)

# special-case voice span where it's at the start and not closed
INITIAL_VOICE_SPAN_RE = re.compile(
    u'^<v ([%s]+)>\s*' % MATCH_WORD, flags=re.IGNORECASE)

# tags - <c.TYPE>...</c>
TAG_RE = re.compile(
    '<c\.(\w+)>([%s\s]+)</c>' % MATCH_WORD, flags=re.IGNORECASE)

# same as above but capture the whole thing
TAG_RE_FULL = re.compile(
    '(<c\.\w+>[%s\s]+</c>)' % MATCH_WORD, flags=re.IGNORECASE)


def strip_voice_spans(text):
    return INITIAL_VOICE_SPAN_RE.sub(
        '', VOICE_SPAN_RE.sub(lambda m: m.groups()[1].strip(), text))


def strip_tags(text):
    return TAG_RE.sub(lambda m: m.groups()[1].strip(), text)


def parse_tags(text):
    """Yield (type, value, pos) tuples for a string of text containing tags,
       i.e.

       <c.tagtype>tag value</c>

       pos is a value between 0 and 1 giving the position of the tag in the
       text with tags stripped, rounded to 5 decimal places
    """

    text = strip_voice_spans(text)

    stripped_len = len(strip_tags(text))

    for match in TAG_RE.finditer(text):
        # estimate position within the (stripped) string
        previous_text = strip_tags(text[:match.start()])
        pos = round(float(len(previous_text)) / stripped_len, 5)

        tag_type, value = match.groups()
        yield tag_type, value, pos


def get_webvttfile(file_obj):
    """Get a WebVTTFile instance from a file-like object. """

    file_obj.seek(0)
    contents = file_obj.read()

    # convert to unicode if it's a plain str
    if not isinstance(contents, unicode):  # NOQA ignore F821
        contents = codecs.decode(contents, 'utf-8')

    return WebVTTFile.from_string(contents)


def parse_transcript(transcript_file, language, valid_types, get_tag,
                     get_colloquialism):
    """Process a transcript file, creating Colloquialism instances as needed,
       and returning a list of Tag instances for review.
       returns a tuple: (tags, errors)

       get_colloquialism should return Colloquialism instance
       get_tag should return a Tag instance
    """

    webvttfile = get_webvttfile(transcript_file)

    errors = []
    tags = []
    for entry in webvttfile:
        # convert WebVTTTime to timedelta
        start = timedelta(milliseconds=entry.start.ordinal)
        length = entry.end.ordinal - entry.start.ordinal

        for tag_type, value, pos in parse_tags(entry.text):
            if tag_type not in valid_types:
                # TODO - log error
                errors.append('Invalid tag type at %s - %s' % (
                    entry.start, tag_type))
                continue

            # create the colloquialism entry if it doesn't exist.
            colloquialism = get_colloquialism(
                value=value, language=language, type=tag_type)

            start_exact = start + timedelta(milliseconds=int(length * pos))
            tag = get_tag(
                start=start, start_exact=start_exact,
                colloquialism=colloquialism)
            tags.append(tag)

    return tags, errors


def wrap_tag(text, tag_value, tag_type):
    """Wrap instances of tag_value in text with <c.tag_type>tag_value</c> """

    # split out existing tags
    parts = TAG_RE_FULL.split(text)

    for i in range(len(parts)):
        # if it's already a tag, ignore
        if TAG_RE.match(parts[i]):
            continue

        # otherwise substitute for the tag
        # word boundaries (\b) don't work with macrons, because they're not
        # considered part of a word, but using lookaround is really slow.
        # We use word boundaries to make the match, but also capture the
        # previous and next characters and check they are not macron characters

        regex = r'(.?)\b(%s)\b(.?)' % tag_value
        # regex = r'(?<![%s])%s(?![%s])' % (MATCH_WORD, tag_value, MATCH_WORD)

        def sub(match):
            before, value, after = match.groups()

            # check the characters around it aren't vowels with macrons
            # return unchanged if so
            if before in EXTRA_WORD or value in EXTRA_WORD:
                return match.group()

            return '%s<c.%s>%s</c>%s' % (before, tag_type, value, after)

        parts[i] = re.sub(
            regex,
            sub,
            parts[i])

    return ''.join(parts)


def auto_tag_text(text, tags):
    """Find instances of tags in text, and wrap them in
        <c.tagtype>tag value</c>.

       tags should be an iterable of dicts with 'type' and 'value' keys:

       [
           {'type': '...', 'value': '...'},
           {'type': '...', 'value': '...'},
       ]
    """

    for info in tags:
        text = wrap_tag(text, info['value'], info['type'])

    return text


def auto_tag_file(file_obj, tags, output):
    """Find instances of tags in the content of a WebVTT file, and wrap them in
        <c.tagtype>tag value</c>.

       tags should be an iterable of dicts as in auto_tag_text

       Writes content to output, which should be a file-like object"""

    webvtt = get_webvttfile(file_obj)

    for item in webvtt:
        item.text = auto_tag_text(item.text, tags)

    webvtt.write_into(output, include_indexes=True)
    return output
