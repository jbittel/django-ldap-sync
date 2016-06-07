#!/usr/bin/env python

from setuptools import find_packages
from setuptools import setup

from ldap_sync import __version__ as version


with open('README.rst') as f:
    readme = f.read()

setup(
    name='django-ldap-sync',
    version=version,
    description='A Django application for synchronizing LDAP users and groups',
    long_description=readme,
    license='BSD',
    author='Jason Bittel',
    author_email='jason.bittel@gmail.com',
    url='https://github.com/jbittel/django-ldap-sync',
    download_url='https://github.com/jbittel/django-ldap-sync',
    packages=find_packages(),
    include_package_data=True,
    install_requires=['python-ldap>=2.4.13'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Programming Language :: Python',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Systems Administration :: Authentication/Directory',
    ],
    keywords=['django', 'ldap', 'active directory', 'synchronize', 'sync'],
)
