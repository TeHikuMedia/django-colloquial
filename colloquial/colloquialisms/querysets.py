# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.conf import settings


class ColloquialismQuerySet(models.QuerySet):
    """QuerySet for Colloquialism models.  """

    def filter_auto(self):
        """Filter colloquialisms which may be used to auto-tag a file. """

        auto_types = [t[0] for t in settings.COLLOQUIAL_TYPES if t[2]]

        # find duplicates (these can't be auto-tagged due to ambiguity)
        duplicates = self.values('normalised_value') \
            .annotate(count=models.Count('pk')).filter(count__gt=1) \
            .values_list('normalised_value', flat=True)

        return self.filter(type__in=auto_types, allow_auto_tag=True) \
            .exclude(normalised_value__in=duplicates)


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

    def get_counts(self):
        """Get a dict of counts, grouped by colloquialism id. """

        counts = self.values('colloquialism').order_by('colloquialism') \
            .annotate(count=models.Count('colloquialism')) \
            .values_list('colloquialism', 'count')

        return dict(counts)
