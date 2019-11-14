#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

requirements = [
    'python-dateutil==2.7.2',
    'requests==2.21.0',
    'songtext==0.1.9',
    'profanity',
    'bs4'
]

setup_args = {
    'python_requires': '>3.5.2',
    'name': 'lastfm-cli-tools',
    'version': '0.1.0',

    'packages': find_packages(),
    'package_dir': {'lastfm-cli-tools': 'lastfm-cli-tools'},
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
