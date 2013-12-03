#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from ldap_sync import __version__ as version


packages = [
    'ldap_sync',
    'ldap_sync.management',
    'ldap_sync.management.commands',
]

package_data = {
    '': ['LICENSE', 'README.rst'],
}

with open('README.rst') as f:
    readme = f.read()

setup(
    name='django-ldap-sync',
    version=version,
    description='A Django application for synchronizing LDAP users and groups',
    long_description=readme,
    author='Jason Bittel',
    author_email='jason.bittel@gmail.com',
    url='https://github.com/jbittel/django-ldap-sync',
    download_url='https://github.com/jbittel/django-ldap-sync/downloads',
    package_dir={'ldap-sync': 'ldap-sync'},
    packages=packages,
    package_data=package_data,
    license='BSD',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Programming Language :: Python',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Topic :: System :: Systems Administration :: Authentication/Directory',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords=['django', 'ldap', 'active directory', 'synchronize', 'sync'],
    install_requires=['python-ldap >= 2.4.13'],
)
