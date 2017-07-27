#!/usr/bin/env python
# coding: utf8

import os

from setuptools import setup, find_packages


# avoid importing the module
__version__ = None
exec(open('colloquial/_version.py').read())

# if there's a converted readme, use it, otherwise fall back to markdown
if os.path.exists('README.rst'):
    readme_path = 'README.rst'
else:
    readme_path = 'README.md'

setup(
    name='django-colloquial',
    version=__version__,
    description='',
    long_description=open(readme_path).read(),
    author='Greg Brown',
    author_email='greg@gregbrown.co.nz',
    url='',
    license='BSD License',
    zip_safe=False,
    platforms='any',
    install_requires=['Django>=1.8', 'pyvtt==0.0.1'],
    include_package_data=True,
    package_data={},
    packages=find_packages(exclude=('tests', )),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Framework :: Django',
    ],
)
