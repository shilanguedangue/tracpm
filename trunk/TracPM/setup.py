#!/usr/bin/env python

from setuptools import setup

'''
    setup_requires:
    1.) Json Support
        Throw an error if Json support is not available 
        Note: json support is included in python version 2.7.1
    setup_requires = [
        'json',
    ],
    install_requires = [
        'json>=1.9',
    ],
'''

setup(
    name='TracPM',
    version='0.2.0',
    packages=['tracpm'],
    author='Kevin Fox',
    description='Project Planning / scheduling / charting....',
    url='http://code.google.com/p/trac-sqa/',
    license='MIT',
    entry_points = {
        'trac.plugins': [
            'tracpm.web_ui = tracpm.web_ui',
            'tracpm.db = tracpm.db',
            
        ]
    },

    
    package_data = {
        'tracpm' : [
            'htdocs/css/*.css',
            'htdocs/js/*.js',
            'templates/pm/*.html',
        ],

    }
)
 
