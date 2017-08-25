Django-colloquial is an application designed to manage media files and their associated webvtt transcripts, using a custom tag format to cross-link tagged phrases ("colloquialisms") in the text. Features:

- Parse existing transcripts for tagged colloquialisms
- Automatically tag known colloquialisms in untagged transcripts
- Filter related transcripts by common colloquialisms

## Requirements & Installation

Currently requires python 2.7 and django 1.10. Wider support coming soon. To install:

	pip install django-colloquial

Then add to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = (
	 ...
	 'colloquial.colloquialisms',
	 'colloquial.transcripts',
)
```

`COLLOQUIAL_TYPES` defines the different types of colloqiualisms supported and whether or not they may automatically tag:

```
COLLOQUIAL_TYPES = (
    ('idiom', 'Idiom', True),
    ('proper_name', 'Proper Name', False),
)
```
 
## Transcript format

Transcripts should be in the [webvtt](https://w3c.github.io/webvtt/) format. Colloquialisms should be tagged using the format `<c.TYPE>colloquialism text</c>` where `TYPE` comes from the `COLLOQUIAL_TYPES` setting. For example:

```
1
00:00:00.092 --> 00:00:10.681
<v Rukuwai> Ko <c.tangata>Hohepa Tipene</c> te kaikorero e whai ake nei.
He kaumatua no roto o <c.iwihapu>Te Rārawa</c>. I tupu ake i te reo o
te kainga.
```

## Running tests

Use tox (<https://pypi.python.org/pypi/tox>):

    > pip install tox
    > cd path-to/django-colloquial
    > tox
