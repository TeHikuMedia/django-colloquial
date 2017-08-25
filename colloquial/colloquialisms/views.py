# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import math

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404


def render_json(data):
    json_dumps_params = {}
    if settings.DEBUG:
        json_dumps_params['indent'] = 2

    return JsonResponse(data, json_dumps_params=json_dumps_params)


def tags(request, item_cls, item_pk):
    """Get tag data, with related items based on common colloquialisms.
       item_cls should be a Transcript model class or queryset, with item_pk
       the primary key of an instance of that class.

       https://3.basecamp.com/3685530/buckets/3803543/messages/578905579
    """
    item = get_object_or_404(item_cls, pk=item_pk)
    return tags_data(item)


def tags_data(item):
    """Get tag data, with related items based on common colloquialisms, for an
       item instance. """

    # loop through tags, building up a nested dict of information as
    # we go. Note, using select_related like this means only one query,
    # but returns lots of redundant data. If performance is a problem,
    # consider separate queries for colloquialism and transcript details

    data = {}

    # add info on each tag that appears in the transcript
    tags = item.get_tags()

    # get tag count by colloquialism id
    tag_counts = tags.get_counts()

    # get ordered list of occurrence times with colloquialism type and value
    occ_times = list(
        tags.values('colloquialism__type', 'colloquialism__pk', 'start_exact')
            .order_by('start_exact'))

    def get_prev_time(time, c_type=None, c_pk=None):
        """Get previous time before the given time matching the type/id. """

        # TODO if efficiency is an issue here, make occ_times a generator and
        # keep a queue (collections.deque) of the relevant times; this should
        # work because we're moving through them in sequence so could safely
        # discard those before the current time as we go

        if c_pk:
            def filter_func(obj):
                return obj['colloquialism__pk'] == c_pk
        elif c_type:
            def filter_func(obj):
                return obj['colloquialism__type'] == c_type
        else:
            def filter_func(obj):
                return True

        # filter out relevant times
        filtered = filter(
            lambda obj: filter_func(obj) and obj['start_exact'] < time,
            occ_times)

        if not len(filtered):
            return None

        # return last filtered time since they are in order
        return filtered[-1]['start_exact']

    def get_uniqueness(time, colloquialism):
        # tau_value = time difference between occurrence of same tag.type.value
        # tau_tag = time difference between self and previous tag.
        # x = (tau_value - tau_tag) / tau_tag
        # uniqueness = 1/count(tag.type.value) * (1 - 1/exp(x/10))

        count = tag_counts[colloquialism.pk]

        if count <= 1:
            return 1

        value_time = get_prev_time(time, c_pk=colloquialism.pk)
        if value_time is None:
            return 1.0 / count
        else:
            # assume a previous tag exists, because it's a superset of t_value
            tag_time = get_prev_time(time)

            tau_tag = (time - tag_time).total_seconds()
            tau_value = (time - value_time).total_seconds()

            x = (tau_value - tau_tag) / tau_tag

        coefficient = 10
        uniqueness = 1.0 / count * (1 - 1 / math.exp(x / coefficient))
        return uniqueness

    for tag in tags.with_colloquialism():
        colloquialism = tag.colloquialism

        # add type details the first time the type is encountered
        if colloquialism.type not in data:
            data[colloquialism.type] = {
                'displayName': colloquialism.get_type_display(),
                'items': {},
            }
        items = data[colloquialism.type]['items']

        colloquialism_key = colloquialism.normalised_value

        # add colloquialism details the first time it appears
        if colloquialism_key not in items:
            items[colloquialism_key] = {
                'meaning': colloquialism.meaning,
                'occurrences': [],
                'related': {},
            }

        occ_data = tag.to_json(True)
        occ_data['uniqueness'] = get_uniqueness(tag.start_exact, colloquialism)
        items[colloquialism_key]['occurrences'].append(occ_data)

    # add in related tag info. Assume that the tag info is already in the data,
    # this code just adds the related information
    related = item.related_tags()

    for tag in related.with_colloquialism().with_transcript():
        colloquialism = tag.colloquialism
        transcript = tag.get_transcript()
        items = data[colloquialism.type]['items']
        related = items[colloquialism.normalised_value]['related']

        # add transcript details the first time it appears
        if transcript.pk not in related:
            related[transcript.pk] = transcript.to_json()
            related[transcript.pk]['occurrences'] = []

        # append tag details
        related[transcript.pk]['occurrences'].append(tag.to_json())

    return render_json(data)


"""
{
tag: {
  displayName: display name for tag
  items:       dictionary of tags used in the transcript with
               tag.value as key.
  {
    tag.value: dictionary with meaning and related items
    {
      meaning: meaning of tag.value
      related: list of publication objects that use the tag.value
      [
        {
          headline:  publication.headline,
          url:       link to publication with tag in query
          thumbnail: link to thumbnail,
	        times:     list of time points where tag is used
          urls:      list of urls for those time points where
                     tag is used
        }
      ]
    }
  }
}
}
"""
