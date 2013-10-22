from distutils.core import setup
import glob
import sys
import os


setup(name = "pyboblight",
    version = "1.0",
    description = "Simple Boblight Client library",
    author = "O. Schacher",
    url='https://github.com/gryphius/pyboblight',
    download_url='http://github.com/gryphius/pyboblight/tarball/master',
    author_email = "oli.schacher@gmail.com",
    packages = ['pyboblight'],
    long_description = """Boblight client library""" ,
      classifiers=[
          'Development Status :: 4 - Beta',
          'License :: OSI Approved :: Apache Software License',
          'Programming Language :: Python',
          ],
)


        
        
        