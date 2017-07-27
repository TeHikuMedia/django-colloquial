# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible
from django.conf import settings

from ..colloquialisms.querysets import TranscriptQuerySet
from ..colloquialisms.models import AbstractTranscript, \
    AbstractTag, DEFAULT_LANGUAGE


# TODO make this a function hook as per the other media files
UPLOAD_PATH = getattr(settings, 'COLLOQUIAL_UPLOAD_PATH', 'transcripts')


@python_2_unicode_compatible
class Transcript(AbstractTranscript, models.Model):
    title = models.CharField(
        max_length=100, blank=True, default='', verbose_name=_('title'))
    transcript_file = models.FileField(
        blank=True, default='', upload_to=UPLOAD_PATH,
        help_text='WebVTT format')
    language = models.CharField(
        max_length=10, choices=settings.LANGUAGES, db_index=True,
        verbose_name=_('language'), default=DEFAULT_LANGUAGE)

    created = models.DateTimeField(
        auto_now_add=True, verbose_name=_('created'))
    updated = models.DateTimeField(auto_now=True, verbose_name=_('updated'))

    objects = TranscriptQuerySet.as_manager()

    def __str__(self):
        if self.title:
            return self.title
        return '%s %s' % (_('Transcript'), self.pk)

    @classmethod
    def get_tag_cls(cls):
        return Tag

    def get_transcript_file(self):
        return self.transcript_file

    def get_language(self):
        return self.language

    def to_json(self):
        return {
            'title': self.title,
        }


class Tag(AbstractTag):
    transcript = models.ForeignKey(
        Transcript, on_delete=models.CASCADE, verbose_name=_('transcript'),
        related_name='tags')
