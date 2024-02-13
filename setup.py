#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='wagtail-experiments',
    version='0.4',
    description="A/B testing for Wagtail",
    author='Matthew Westcott',
    author_email='matthew.westcott@torchbox.com',
    url='https://github.com/torchbox/wagtail-experiments',
    packages=find_packages(),
    include_package_data=True,
    license='BSD',
    long_description=open('README.rst').read(),
    python_requires=">=3.8",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Framework :: Django',
        'Framework :: Django :: 4.2',
        'Framework :: Django :: 5.0',
        'Framework :: Wagtail',
        'Framework :: Wagtail :: 5',
        'Framework :: Wagtail :: 6',
    ],
)

