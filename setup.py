#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

requirements = [
    'python-dateutil==2.7.2',
    'requests==2.11.1',
    'songtext==0.1.5',
    'profanity'
]

setup_args = {
    'name': 'fortunelyrics',
    'version': '0.0.2',

    'packages': find_packages(),
    'package_dir': {'fortunelyrics': 'fortunelyrics'},
    'package_data': {},
    'install_requires': requirements,

    'entry_points': {
        'console_scripts': [
            'sing=fortunelyrics.fortunelyrics:go',
            'singthis=fortunelyrics.singthis:go',
            'getsongs=fortunelyrics.getsongs:go',
            'musicstats=lasthop.lasthop:go'
        ],
    }
}

setup(**setup_args)
