#!/usr/bin/env/python

"""
Setup script for ginf-redis
"""

try:
    from setuptools import setup, Extension
except ImportError:
    from distutils.core import setup, Extension

setup(
	name='ginf',
	author='Ben Johnson',
	author_email='ben@gophronesis.com',
	classifiers=[],
	description='Redis implementation of HRL geoinference',
	keywords=['ginf'],
	license='ALV2',
	packages=['ginf'],
    intall_requires=['Flask==0.10.1', 'Flask-RESTful==0.3.5', 'tornado==4.1',
                         'redis==2.10.5', 'redis-py-cluster==1.2.0'],
	version="0.2"
)