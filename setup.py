#!/usr/bin/env python

from setuptools import setup

setup(name='tap-simpleanalytics',
    version='0.0.1',
    description='Singer.io tap for extracting data from the Simple Analytics API',
    author='Ideavate Limited',
    url='https://github.com/ideavateltd/tap-simpleanalytics',
    classifiers=['Programming Language :: Python :: 3 :: Only'],
    py_modules=['tap_simpleanalytics'],
    install_requires=[
        'requests>=2.13.0',
        'singer-python>=3.6.3',
        'tzlocal>=1.3',
    ],
    entry_points='''
        [console_scripts]
        tap-simpleanalytics=tap_simpleanalytics:main
    ''',
    packages=['tap_simpleanalytics'],
    package_data = {
        'tap_simpleanalytics/schemas': [
            "visits.json",
        ],
    },
    include_package_data=True,
)
