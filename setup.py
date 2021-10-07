"""
Copyright (C) 2016, 2017, 2020 biqqles.

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
from setuptools import setup, find_namespace_packages
from os.path import expanduser


setup(
    name='wingman',
    version='5.0',

    author='biqqles',
    author_email='biqqles@protonmail.com',
    url='https://discoverygc.com/forums/showthread.php?tid=150721',

    description='A companion for Discovery Freelancer',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',

    packages=find_namespace_packages('src'),
    package_dir={'': 'src'},

    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Development Status :: 4 - Beta',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows',
        'Topic :: Games/Entertainment',
        'Intended Audience :: End Users/Desktop',
        'Environment :: X11 Applications :: Qt',
    ],

    python_requires='>=3.7',
    install_requires=[
        'dataclassy>=0.10.0',
        'fl-flint>=0.9.0',
        'fl-flair>=0.5.0; platform_system=="Windows"',
        'ago==0.0.93',
        'Pillow>=8.1',
        'PyQt5>=5.15.0',
        'PyQtWebEngine>=5.15.0',
    ],

    entry_points={
          'gui_scripts': [
              'wingman = wingman.main:main'
          ]
    },
    data_files=[
        # we want these files to install relative to the package directory
        ('share/applications', ['packaging/linux/eu.biqqles.wingman.desktop']),
        ('share/icons/hicolor/256x256/apps', ['icons/general/wingman.png']),

        # we want these to install as absolute paths
        # create file stubs for deletion of the real things upon uninstallation.
        # sadly there is no way to delete folders...
        (expanduser('~/.local/share/wingman'), ['wingman.log']),
    ],
)
