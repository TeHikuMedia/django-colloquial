from django.conf.urls import url

from .models import Transcript
from ..colloquialisms.views import tags


urlpatterns = [
    url(r'^tags/(?P<item_pk>\d+)', tags, {'item_cls': Transcript}, 'tags'),
]
