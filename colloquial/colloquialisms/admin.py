# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.conf.urls import url
from django.core.urlresolvers import reverse

from .models import Colloquialism
from . import admin_views


@admin.register(Colloquialism)
class ColloquialismAdmin(admin.ModelAdmin):
    list_display = ('value', 'type', 'language', 'created', 'updated', )
    list_filter = ('type', 'language', 'created', )
    search_fields = ('value', 'meaning')


class BaseTranscriptAdmin(admin.ModelAdmin):
    def get_process_url_name(self):
        return '%s_process_%s' % (
            self.model._meta.app_label, self.model._meta.model_name)

    def links(self, obj):
        if not obj.get_transcript_file():
            return ''

        process_url = reverse('admin:%s' % self.get_process_url_name(),
                              args=(obj.pk, ))
        return '<a href="%s">Process</a>' % (process_url)
    links.allow_tags = True

    def get_urls(self):
        urls = super(BaseTranscriptAdmin, self).get_urls()

        view = self.admin_site.admin_view(admin_views.process_transcript)

        return [
            url(r'^(?P<pk>\d+)/process/$', view, {'item_cls': self.model},
                self.get_process_url_name())
        ] + urls
