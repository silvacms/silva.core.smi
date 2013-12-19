# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from setuptools import setup, find_packages
import os

version = '3.0.3'

tests_require = [
    'Products.Silva [test]',
    ]

setup(name='silva.core.smi',
      version=version,
      description="Silva Management Interface",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Zope2",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='silva zope2 smi',
      author='Infrae',
      author_email='info@infrae.com',
      url='https://github.com/silvacms/silva.core.smi',
      license='BSD',
      package_dir={'': 'src'},
      packages=find_packages('src'),
      namespace_packages=['silva', 'silva.core'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'AccessControl',
        'five.grok',
        'infrae.comethods',
        'lxml',
        'grokcore.chameleon',
        'setuptools',
        'silva.core.cache',
        'silva.core.conf',
        'silva.core.interfaces',
        'silva.core.layout',
        'silva.core.messages',
        'silva.core.references',
        'silva.core.services',
        'silva.core.views',
        'silva.fanstatic',
        'silva.translations',
        'silva.ui',
        'z3c.schema',
        'zeam.form.autofields',
        'zeam.form.silva',
        'zeam.form.ztk',
        'zope.cachedescriptors',
        'zope.component',
        'zope.interface',
        'zope.intid',
        'zope.schema',
        'zope.traversing',
        'zope.publisher',
        ],
      tests_require=tests_require,
      extras_require={'test': tests_require},
      )
