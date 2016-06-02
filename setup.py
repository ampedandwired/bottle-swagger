#!/usr/bin/env python
import os
from setuptools import setup

def _read(fname):
    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()
    except IOError:
        return ''

REQUIREMENTS = [l for l in _read('requirements.txt').split('\n') if l and not l.startswith('#')]
VERSION = '1.0.2'

setup(
        name='bottle-swagger',
        version=VERSION,
        url='https://github.com/ampedandwired/bottle-swagger',
        download_url='https://github.com/ampedandwired/bottle-swagger/archive/v{}.tar.gz'.format(VERSION),
        description='Swagger integration for Bottle',
        author='Charles Blaxland',
        author_email='charles.blaxland@gmail.com',
        license='MIT',
        platforms='any',
        py_modules=['bottle_swagger'],
        install_requires=REQUIREMENTS,
        classifiers=[
            'Environment :: Web Environment',
            'Environment :: Plugins',
            'Framework :: Bottle',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
            'Topic :: Software Development :: Libraries :: Python Modules'
        ],
)
