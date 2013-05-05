from distutils.core import setup
import os

from ldap_sync import __version__ as version


def split_relative_path(path):
    """
    Given a path, return the path as a string with the
    first path component removed (e.g. 'foo/bar/baz' would
    be returned as 'bar/baz').
    """
    parts = []
    while True:
        head, tail = os.path.split(path)
        if head == path:
            if path:
                parts.append(path)
            break
        parts.append(tail)
        path = head
    parts.reverse()
    if len(parts) > 1:
        return os.path.join(*parts[1:])
    else:
        return ''

def get_readme(filename):
    """
    Utility function to print the README file, used for the long_description
    setup argument below.
    """
    return open(os.path.join(os.path.dirname(__file__), filename)).read()

packages, package_data = [], []
root_dir = os.path.dirname(__file__)
if root_dir:
    os.chdir(root_dir)

# Collect the lists of packages and package files, starting
# from the base project directory (adapted from the Django setup script)
for dirpath, dirnames, filenames in os.walk('ldap_sync'):
    # Collect packages
    if '__init__.py' in filenames:
        pkg_path = os.path.normpath(dirpath)
        pkg = pkg_path.replace(os.sep, '.')
        if os.altsep:
            pkg = pkg.replace(os.altsep, '.')
        packages.append(pkg)
    # Collect ancillary package files
    elif filenames:
        relative_path = split_relative_path(dirpath)
        for f in filenames:
            package_data.append(os.path.join(relative_path, f))

setup(
    name='django-ldap-sync',
    version=version,
    description='A Django application for synchronizing LDAP users and groups',
    long_description=get_readme('README'),
    author='Jason Bittel',
    author_email='jason.bittel@gmail.com',
    url='https://github.com/jbittel/django-ldap-sync',
    download_url='https://github.com/jbittel/django-ldap-sync/downloads',
    package_dir={ 'ldap-sync': 'ldap-sync' },
    packages=packages,
    package_data={ 'ldap-sync': package_data },
    license='BSD',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
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
)
