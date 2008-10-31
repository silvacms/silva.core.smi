from setuptools import setup, find_packages
import os

version = '2.2'

setup(name='silva.core.smi',
      version=version,
      description="Silva Management Interface",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='silva zope2 smi',
      author='Infrae',
      author_email='info@infrae.com',
      url='http://infrae.com/products/silva',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['silva', 'silva.core'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'silva.core.views',
          'silva.core.smi',
          ],
      )
