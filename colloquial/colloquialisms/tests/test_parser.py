# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from StringIO import StringIO
from django.test import TestCase, override_settings
from pyvtt import WebVTTFile

from ..parser import strip_tags, parse_tags, strip_voice_spans, \
    get_webvttfile, wrap_tag, auto_tag_text, auto_tag_file, parse_transcript


test_settings = {
    'COLLOQUIAL_TYPES': [
        ('tangata', 'tangata', True),
        ('iwihapu', 'iwihapu', True),
        ('kainga', 'kainga', True),
        ('ingoatupuna', 'ingoatupuna', True),
    ],
}

file_content_plain = """WEBVTT

1
00:00:00.092 --> 00:00:10.681
<v Rukuwai> Ko Hohepa Tipene te kaikorero e whai ake nei.
He kaumatua no roto o Te Rārawa. I tupu ake i te reo o
te kainga.

2
00:00:10.681 --> 00:00:15.975
Nō hea tērā ingoa Panguru?</v>

3
00:00:15.975 --> 00:00:22.012
<v Hohepa>E pēnei pea tāku kōrero ki a koe.
"""

file_content_tagged = """WEBVTT

1
00:00:00.092 --> 00:00:10.681
<v Rukuwai> Ko <c.tangata>Hohepa Tipene</c> te kaikorero e whai ake nei.
He kaumatua no roto o <c.iwihapu>Te Rārawa</c>. I tupu ake i te reo o
te kainga.

2
00:00:10.681 --> 00:00:15.975
Nō hea tērā ingoa <c.kainga>Panguru</c>?</v>

3
00:00:15.975 --> 00:00:22.012
<v Hohepa>E pēnei pea tāku kōrero ki a koe.
"""

first_item_text = """
<v Rukuwai> Ko <c.tangata>Hohepa Tipene</c> te kaikorero e whai ake nei.
He kaumatua no roto o <c.iwihapu>Te Rārawa</c>. I tupu ake i te reo o
te kainga.""".strip()

first_item_stripped = """Ko Hohepa Tipene te kaikorero e whai ake nei.
He kaumatua no roto o Te Rārawa. I tupu ake i te reo o
te kainga."""

first_item_tags = [
    ('tangata', 'Hohepa Tipene', 0.02703, True),
    ('iwihapu', 'Te Rārawa', 0.61261, True),
]

second_item_text = 'Nō hea tērā ingoa <c.kainga>Panguru</c>?</v>'
second_item_stripped = 'Nō hea tērā ingoa Panguru?</v>'
second_item_tags = [
    ('kainga', 'Panguru', 0, True),
]

third_item_text = """<v Hohepa>E pēnei pea tāku kōrero ki a koe."""

file_content_span_cues = """WEBVTT

1
00:00:00.000 --> 00:00:15.123
taua <c.ingoatupuna>Ngārama Te Maru</c> me tana wahine <c.ingoatupuna>Matire

2
00:00:16.000 --> 00:00:20.456
Rapihana</c>, i tuku mai hei tūnga whare mō te <c.ingoatupuna>Ngārama

3
00:00:21.000 --> 00:00:24.000
i tuku <c.kainga>Panguru</c> mai hei tūnga <c.ingoatupuna>Ngārama

4
00:00:24.000 --> 00:00:28.000
Te Maru</c> i tuku <c.iwihapu>Te Rārawa</c>"""

file_content_span_cues_plain = """WEBVTT

1
00:00:00.000 --> 00:00:15.123
taua Panguru, nā ōku Hohepa

2
00:00:16.000 --> 00:00:20.456
Tipene, i tuku mai Te Rārawa ne"""

file_content_span_cues_auto_tagged = """WEBVTT

1
00:00:00.000 --> 00:00:15.123
taua <c.kainga>Panguru</c>, nā ōku <c.tangata>Hohepa

2
00:00:16.000 --> 00:00:20.456
Tipene</c>, i tuku mai <c.iwihapu>Te Rārawa</c> ne"""


# first_item_text = 'taua wāhi rā, nā ōku mātua, ā, ' \
#                   '<c.ingoatupuna>Ngārama Te Maru</c> me tana '\
#                   'wahine <c.ingoatupuna>Matire'
#
# second_item_text = 'Rapihana</c>, i tuku mai hei ' \
#                    'tūnga whare mō te kāinga'
#
# first_item_tags = [
#     ('ingoatupuna', 'Ngārama Te Maru', 0),
#     ('ingoatupuna', 'Matire Rapihana', 0),
# ]
# #  Here the cue that starts the tag owns the tag.
#
# second_item_tags = []
#
# print


def process_tag_list(tags):
    """Convert tag list to format accepted for the auto_tag functions. """

    return list({'type': t[0], 'value': t[1]} for t in tags)


@override_settings(**test_settings)
class ParserTestCase(TestCase):
    # def setUp(self):
    #     pass

    def test_strip_voice_spans(self):

        self.assertEqual(
            strip_voice_spans('<v Rukuwai> Ko <c.tangata>Hohepa Tipene</c>te'),
            'Ko <c.tangata>Hohepa Tipene</c>te')

        self.assertEqual(
            strip_voice_spans(
                '<v Rukuwai> Ko <c.tangata>Hohepa Tipene</c>te </v> kōrero'),
            'Ko <c.tangata>Hohepa Tipene</c>te kōrero')

    def test_strip_tags(self):
        self.assertEqual(strip_tags(strip_voice_spans(first_item_text)),
                         first_item_stripped)

    def test_parse_tags(self):
        self.assertEqual(list(parse_tags(first_item_text)), first_item_tags)

    def test_parse_tags_with_macrons(self):
        self.assertEqual(list(parse_tags(first_item_text)), first_item_tags)

    def test_get_webvttfile(self):
        file_obj = StringIO(file_content_tagged)

        webvtt = get_webvttfile(file_obj)

        self.assertEqual(isinstance(webvtt, WebVTTFile), True)
        self.assertEqual(webvtt[0].text, first_item_text)
        self.assertEqual(webvtt[2].text, third_item_text)

    def test_parse_transcript(self):
        file_obj = StringIO(file_content_tagged)
        valid_types = [t[0] for t in test_settings['COLLOQUIAL_TYPES']]

        # get_tag and get_colloquialism return placeholder values

        def get_tag(start, start_exact, colloquialism):
            return (colloquialism, start.microseconds)

        def get_colloquialism(type, language, value):
            return value

        tags, errors = parse_transcript(file_obj, 'en', valid_types, get_tag,
                                        get_colloquialism)

        self.assertEqual(tags, [
            (u'Hohepa Tipene', 92000),
            (u'Te R\u0101rawa', 92000),
            (u'Panguru', 681000)
        ])

    def test_parse_transcript_span_cues(self):
        file_obj = StringIO(file_content_span_cues)
        valid_types = [t[0] for t in test_settings['COLLOQUIAL_TYPES']]

        # get_tag and get_colloquialism return placeholder values

        def get_tag(start, start_exact, colloquialism):
            return (colloquialism, start.seconds)

        def get_colloquialism(type, language, value):
            return value

        tags, errors = parse_transcript(file_obj, 'en', valid_types, get_tag,
                                        get_colloquialism)

        self.assertEqual(tags, [
            (u'Ng\u0101rama Te Maru', 0),
            (u'Matire Rapihana', 0),
            (u'Panguru', 21),
            (u'Ng\u0101rama Te Maru', 21),
            (u'Te R\u0101rawa', 24),
        ])

    def test_wrap_tag(self):
        text = 'Ko Hohepa tēnei, Hohepa Tipene nei. Hohepa Tipene'
        wrapped = 'Ko Hohepa tēnei, <c.tangata>Hohepa Tipene</c> nei. ' \
            '<c.tangata>Hohepa Tipene</c>'
        self.assertEqual(wrap_tag(text, 'Hohepa Tipene', 'tangata'),
                         wrapped)

    def test_word_boundaries(self):
        """Test that word boundaries are respected by wrap_tag. """

        text = 'mahimahi pukumahi mahia mahi'
        wrapped = 'mahimahi pukumahi mahia <c.korerorero>mahi</c>'
        self.assertEqual(wrap_tag(text, 'mahi', 'korerorero'), wrapped)

        text = 'Kei runga te rākau i te po, kī mai te kau ka awatea'
        wrapped = 'Kei runga te rākau i te po, kī mai te ' \
            '<c.korerorero>kau</c> ka awatea'
        self.assertEqual(wrap_tag(text, 'kau', 'korerorero'), wrapped)

    def test_auto_tag_text(self):
        first_tags = process_tag_list(first_item_tags)

        self.assertEqual(
            auto_tag_text(first_item_stripped, first_tags),
            strip_voice_spans(first_item_text))

        second_tags = process_tag_list(second_item_tags)

        self.assertEqual(
            auto_tag_text(second_item_stripped, second_tags),
            strip_voice_spans(second_item_text))

    def test_word_boundary(self):
        """Check it doesn't auto-tag sub-words. """

        plain = 'te whanga o Hokianga, me tērā hanga'
        tags = process_tag_list((
            ('kirehu', 'hanga'),
            ('ingoaarohe', 'Hokianga'),
        ))
        tagged = 'te whanga o <c.ingoaarohe>Hokianga</c>, me tērā ' \
            '<c.kirehu>hanga</c>'

        self.assertEqual(auto_tag_text(plain, tags), tagged)

        plain = 'takoto nei te kōhatu nei, nē?'
        tags = process_tag_list((
            ('kirehu', 'kō'),
        ))

        self.assertEqual(auto_tag_text(plain, tags), plain)

    def test_word_boundary_macron(self):
        """Check it doesn't auto-tag sub-words where a macron could be
           confused for a word boundary. """

        plain = 'moana kei te hauāuru, nā, he kai, he kai, he kai.'
        tags = process_tag_list((
            ('kirehu', 'hau'),
        ))
        self.assertEqual(auto_tag_text(plain, tags), plain)

    def test_punctuation(self):
        """Check it correctly tags words with adjacent punctuation. """

        plain = 'te "rawa koe e" ne'
        tagged = 'te "<c.kirehu>rawa</c> koe e" ne'
        tags = process_tag_list((
            ('kirehu', 'rawa'),
        ))
        self.assertEqual(auto_tag_text(plain, tags), tagged)

    def test_case_in_text(self):
        """Check it tags words regardless of case in text. """

        plain = 'te Rawa koe e nei'
        tagged = 'te <c.kupuake>Rawa</c> koe e nei'
        tags = process_tag_list((
            ('kupuake', 'rawa'),
        ))
        self.assertEqual(auto_tag_text(plain, tags), tagged)

    def test_case_in_database(self):
        """Check it tags words regardless of case in database. """

        plain = 'te rawa koe e nei'
        tagged = 'te <c.kupuake>rawa</c> koe e nei'
        tags = process_tag_list((
            ('kupuake', 'Rawa'),
        ))
        self.assertEqual(auto_tag_text(plain, tags), tagged)

    def test_auto_tag_no_double(self):
        """Check that existing tags are not rewrapped, and their contents
           is not touched. """

        tags = process_tag_list((
            ('kainga', 'Panguru'),
        ))
        text = 'No hea tera ingoa <c.kainga>Panguru</c>. ' \
            'Panguru. <c.tangata>Hohepa Panguru</c>'
        tagged = 'No hea tera ingoa <c.kainga>Panguru</c>. ' \
            '<c.kainga>Panguru</c>. <c.tangata>Hohepa Panguru</c>'

        self.assertEqual(auto_tag_text(text, tags), tagged)

    def test_auto_tag_file(self):
        file_obj = StringIO(file_content_plain)
        all_tags = process_tag_list(first_item_tags + second_item_tags)
        tagged_file_obj = auto_tag_file(file_obj, all_tags, StringIO())

        tagged_file_obj.seek(0)
        auto_tagged_content = tagged_file_obj.read()

        self.assertEqual(auto_tagged_content.strip(),
                         file_content_tagged.strip())

    def test_auto_tag_file_span_cues(self):
        file_obj = StringIO(file_content_span_cues_plain)
        all_tags = process_tag_list(first_item_tags + second_item_tags)
        tagged_file_obj = auto_tag_file(file_obj, all_tags, StringIO())

        tagged_file_obj.seek(0)
        auto_tagged_content = tagged_file_obj.read()

        self.assertEqual(auto_tagged_content.strip(),
                         file_content_span_cues_auto_tagged.strip())

    def test_tag_with_comma(self):
        text = 'Mēnā e hē ana ahau, <c.korerorero>ko pēnei atu au ki a ' \
            'koutou</c>, <c.korerorero>nā tōku hē, nā tōku hē rawa</c>.'

        tags = [t[1] for t in parse_tags(text)]
        self.assertEqual(tags, ['ko pēnei atu au ki a koutou',
                                'nā tōku hē, nā tōku hē rawa'])
