from django.contrib import admin

from .models import Transcript, Tag
from ..colloquialisms.admin import BaseTranscriptAdmin


class TagInline(admin.TabularInline):
    model = Tag
    extra = 0


@admin.register(Transcript)
class TranscriptAdmin(BaseTranscriptAdmin):
    list_display = ('__unicode__', 'transcript_file', 'created', 'updated',
                    'links', )
    list_filter = ('created', )
    search_fields = ('value', 'meaning')
    inlines = (TagInline, )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('transcript', 'colloquialism', 'start', )
    search_fields = ('transcript__title', 'colloquialism__value')
