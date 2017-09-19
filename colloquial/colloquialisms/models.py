# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from StringIO import StringIO

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible
from django.conf import settings

from .querysets import ColloquialismQuerySet, TagQuerySet


DEFAULT_LANGUAGE = settings.LANGUAGES[0][0]
OCCURRENCE_RELATED_NAME = "tags"
TYPE_CHOICES = [t[:2] for t in settings.COLLOQUIAL_TYPES]


@python_2_unicode_compatible
class Colloquialism(models.Model):
    type = models.CharField(
        max_length=20, choices=TYPE_CHOICES, db_index=True,
        verbose_name=_('type'))
    language = models.CharField(
        max_length=30, choices=settings.LANGUAGES, db_index=True,
        verbose_name=_('language'), default=DEFAULT_LANGUAGE)
    allow_auto_tag = models.BooleanField(default=True)

    # TODO consider using django.contrib.postgre.fields.CIText once on django
    # 1.11. Should also think about a custom case-insensitive unique index for
    # this field rather than a separate normalised field
    # Also: https://stackoverflow.com/a/7773515/136010
    value = models.CharField(max_length=200, verbose_name=_('value'))
    normalised_value = models.CharField(max_length=200, editable=False,
                                        db_index=True)

    meaning = models.TextField(
        blank=True, default='', verbose_name=_('meaning'))

    created = models.DateTimeField(
        auto_now_add=True, verbose_name=_('created'))
    updated = models.DateTimeField(auto_now=True, verbose_name=_('updated'))

    objects = ColloquialismQuerySet.as_manager()

    @classmethod
    def normalise_value(cls, value, type):
        """Normalise value string - currently just lowercase it so that all are
           case-insensitive; in future some types may be case-sensitive. """

        return value.lower()

    def save(self, *args, **kwargs):
        self.normalised_value = self.normalise_value(self.value, self.type)
        return super(Colloquialism, self).save(*args, **kwargs)

    class Meta:
        unique_together = ('type', 'language', 'normalised_value', )

    def __str__(self):
        return '%s: %s' % (self.get_type_display(), self.value)


class AbstractTranscript(object):
    """Assumes one-to-many relationship with an AbstractTag subclass.
       Subclasses must define class method get_tag_cls, and instance
       methods get_transcript_file, get_language and to_json
    """

    # TODO deduce this programmatically
    tag_rel = 'tags'

    def related_colloquialisms(self):
        """Return a queryset of colloquialisms occurring in this transcript.
        """

        transcript_rel = self.get_tag_cls().transcript_rel
        related_name = '%s_%s_%s' % (
            self.get_tag_cls()._meta.app_label,
            self.get_tag_cls()._meta.model_name,
            OCCURRENCE_RELATED_NAME)
        filter_arg = '%s__%s' % (related_name, transcript_rel)

        return Colloquialism.objects.filter(**{
            filter_arg: self
        })

    def get_tags(self):
        """Return a queryset of tags occurring in this transcript. """

        return self.get_tag_cls().objects.filter(**{
            self.get_tag_cls().transcript_rel: self
        })

    def related_tags(self):
        """Return a queryset of tags related to this transcript by
           colloquialism.  """

        # exclude own tags
        qs = self.get_tag_cls().objects.exclude(**{
            self.get_tag_cls().transcript_rel: self
        })
        # qs = self.get_tag_cls().objects.all()

        # find related tags
        # TODO verify that this is querying sanely - might need to use
        # values_list
        colloquialisms = self.related_colloquialisms()
        return qs.filter(colloquialism__in=colloquialisms)

    def get_tagged_transcript(self, output=None):
        """Write the transcript content with tags automatically added to
           output. """

        assert self.get_transcript_file(), 'No transcript file'

        from .parser import auto_tag_file

        tags = Colloquialism.objects.filter_auto().values('type', 'value')

        if output is None:
            output = StringIO()

        return auto_tag_file(self.get_transcript_file(), tags, output)

    def parse(self, save=False):
        """Parse existing tags from a transcript file. Return

           (tags, errors)

           where tags is a list of Tag instances, and errors a list of strings
        """

        assert self.get_transcript_file(), 'No transcript file'

        from .parser import parse_transcript

        def get_colloquialism(value, language, type):
            """Get colloquialism by normalised value. """

            return Colloquialism.objects.get_or_create(
                language=language,
                type=type,
                normalised_value=Colloquialism.normalise_value(value, type),
                defaults={
                    'value': value
                }
            )[0]

        valid_types = [t[0] for t in settings.COLLOQUIAL_TYPES]

        tagged_transcript = self.get_tagged_transcript()

        tags, errors = parse_transcript(
            tagged_transcript, self.get_language(),
            valid_types=valid_types,
            get_tag=self.get_tag_cls(),
            get_colloquialism=get_colloquialism)

        if save:
            for occ in tags:
                setattr(occ, occ.transcript_rel, self)
                occ.save()

        return tags, errors

    # subclasses to implement the following methods

    @classmethod
    def get_tag_cls(cls):
        raise NotImplementedError

    def get_transcript_file(self):
        raise NotImplementedError

    def get_language(self):
        raise NotImplementedError

    def to_json(self):
        raise NotImplementedError

    # subclasses may also implement the following methods

    def colloquialism_json(self, colloquialism):
        return {}

    # @classmethod
    # def get_tag_relation(cls):
    #     """Get the tag relation for this class - use the first if
    #        there's more than one. """
    #
    #     # get all related tag fields
    #     relations = [rel for rel in cls._meta.get_fields()
    #                  if isinstance(rel, models.ManyToOneRel) and
    #                  issubclass(rel.related_model, BaseTag)]
    #
    #     # assume there's only one
    #     return relations[0]
    #
    # @classmethod
    # def tag_filter_prefix(cls):
    #     rel = cls.get_tag_relation()
    #     return rel.name
    #
    # def get_related_tags(self):
    #     rel = self.get_tag_relation()
    #     return getattr(self, rel.get_accessor_name()).all()


@python_2_unicode_compatible
class AbstractTag(models.Model):
    """Abstract model class. Subclasses must define a ForeignKey to an
       model subclassing AbstractTranscript.
    """

    # TODO deduce this programmatically
    transcript_rel = 'transcript'

    # just in case... :)
    id = models.BigAutoField(primary_key=True)

    colloquialism = models.ForeignKey(
        Colloquialism, on_delete=models.PROTECT,
        verbose_name=_('colloquialism'),
        related_name='%(app_label)s_%(class)s_' + OCCURRENCE_RELATED_NAME)
    start = models.DurationField(verbose_name=_('start'), db_index=True)
    start_exact = models.DurationField(verbose_name=_('start exact'))

    objects = TagQuerySet.as_manager()

    class Meta:
        ordering = ('start', )
        abstract = True

    def __str__(self):
        return '%s at %s' % (self.colloquialism, self.start_exact)

    def get_transcript(self):
        return getattr(self, self.transcript_rel)

    def to_json(self):
        return {
            'time': self.start_exact.total_seconds(),
        }
