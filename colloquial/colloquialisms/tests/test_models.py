# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase, override_settings

from ..models import Colloquialism


TEST_SETTINGS = {
    'COLLOQUIAL_TYPES': (
        ('type_1', 'Type 1', True),
        ('type_2', 'Type 2', True),
        ('type_no_auto', 'Type no auto', False),
    ),
    'DEFAULT_LANGUAGE': 'en',
    # 'LANGUAGES': (
    #     ('en', 'English'),
    # ),
}


@override_settings(**TEST_SETTINGS)
class ParserTestCase(TestCase):
    def setUp(self):
        self.col_1 = Colloquialism.objects.create(
            pk=1,
            type='type_1',
            value='Colloquialism 1',
            language='en')
        self.col_2 = Colloquialism.objects.create(
            pk=2,
            type='type_2',
            value='Colloquialism 2')

        self.duplicate_1 = Colloquialism.objects.create(
            pk=3,
            type='type_1',
            value='Duplicate')
        self.duplicate_2 = Colloquialism.objects.create(
            pk=4,
            type='type_2',
            value='duplicate')  # note case-insensitive

        self.no_tag = Colloquialism.objects.create(
            pk=5,
            type='type_no_tag',
            value='Duplicate')

    def test_auto_filter(self):
        auto = Colloquialism.objects.filter_auto().order_by('pk')
        self.assertEqual(list(auto), [self.col_1, self.col_2])

    def test_normalisation(self):
        col = Colloquialism.objects.create(type='type_1', value='Test Title')
        self.assertEqual(col.normalised_value, 'test title')
