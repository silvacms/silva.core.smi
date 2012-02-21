# -*- coding: utf-8 -*-
# Copyright (c) 2002-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from setuptools import setup, find_packages
import os

version = '2.3.6'

tests_require = [
    'BeautifulSoup',
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
      url='http://infrae.com/products/silva',
      license='BSD',
      package_dir={'': 'src'},
      packages=find_packages('src'),
      namespace_packages=['silva', 'silva.core'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'Products.Silva',
        'Zope2',
        'five.grok',
        'grokcore.view',
        'infrae.layout',
        'infrae.rest',
        'megrok.chameleon',
        'megrok.pagetemplate',
        'setuptools',
        'silva.core.cache',
        'silva.core.conf',
        'silva.core.interfaces',
        'silva.core.layout',
        'silva.core.messages',
        'silva.core.references',
        'silva.core.services',
        'silva.core.views',
        'silva.translations',
        'z3c.schema',
        'zeam.form.base',
        'zeam.form.silva',
        'zope.cachedescriptors',
        'zope.component',
        'zope.contentprovider',
        'zope.i18n',
        'zope.interface',
        'zope.intid',
        'zope.publisher',
        'zope.schema',
        'zope.traversing',
        ],
      tests_require=tests_require,
      extras_require={'test': tests_require},
      )
