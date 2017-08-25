
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME':  '/Users/greg/Desktop/test.sqlite',
        'TEST_NAME': 'test.sqlite',
    }
}

SECRET_KEY = '1'

INSTALLED_APPS = [
    'colloquial.colloquialisms',
    'colloquial.transcripts',
]

COLLOQUIAL_TYPES = (
    ('type_1', 'Type 1', True),
    ('type_2', 'Type 2', True),
    ('type_no_auto', 'Type no auto', False),
)
