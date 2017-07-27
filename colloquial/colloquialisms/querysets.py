# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class ColloquialismQuerySet(models.QuerySet):
    """QuerySet for Colloquialism models.  """

    pass


class TranscriptQuerySet(models.QuerySet):
    """QuerySet for Transcript models. Assumed to have a one-to-many
       relationship with an AbstractTag model. """

    pass


class TagQuerySet(models.QuerySet):
    """QuerySet for Tag models. Assumed to have a foreign key to
       a transcript model. """

    def with_colloquialism(self):
        return self.select_related('colloquialism')

    def with_transcript(self):
        return self.select_related(self.model.transcript_rel)
