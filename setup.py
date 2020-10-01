#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='wagtail-experiments',
    version='0.21',
    description="A/B testing for Wagtail",
    author='Matthew Westcott',
    author_email='matthew.westcott@torchbox.com',
    url='https://github.com/torchbox/wagtail-experiments',
    packages=find_packages(),
    include_package_data=True,
    license='BSD',
    long_description=open('README.rst').read(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Framework :: Django',
        'Framework :: Wagtail',
        'Framework :: Wagtail :: 1',
        'Framework :: Wagtail :: 2',
    ],
)
