# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages


def process_transcript(request, item_cls, pk):
    transcript = get_object_or_404(item_cls, pk=pk)

    change_view = 'admin:%s_%s_change' % (
        item_cls._meta.app_label, item_cls._meta.model_name)

    if not transcript.get_transcript_file():
        msg = 'No transcript file'
        messages.add_message(request, messages.ERROR, msg)
        return redirect(change_view, transcript.pk)

    tags, errors = transcript.parse()

    if len(tags) and request.method == 'POST':
        delete_count, __ = transcript.tags.all().delete()
        tags, errors = transcript.parse(save=True)

        for error in errors:
            messages.add_message(request, messages.ERROR, error)

        if not(len(errors)):
            msg = '%s tags deleted, %s tags added.' % (
                delete_count, len(tags))
            messages.add_message(request, messages.INFO, msg)

        return redirect(change_view, transcript.pk)

    return render(request, 'admin/colloquial/process_transcript.html', {
        'transcript': transcript,
        'tags': tags,
        'errors': errors,
    })
