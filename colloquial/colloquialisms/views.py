# -*- coding: utf-8 -*-
from __future__ import unicode_literals

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
    for tag in tags.with_colloquialism():
        colloquialism = tag.colloquialism

        # add type details the first time the type is encountered
        if colloquialism.type not in data:
            data[colloquialism.type] = {
                'displayName': colloquialism.get_type_display(),
                'items': {},
            }
        items = data[colloquialism.type]['items']

        # add colloquialism details the first time it appears
        if colloquialism.normalised_value not in items:
            items[colloquialism.normalised_value] = {
                'meaning': colloquialism.meaning,
                'related': {},
            }

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
