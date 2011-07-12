#!/usr/bin/env python2

from distutils.core import setup

setup(name='postured',
      version='1.0',
      description='cron-like reminder daemon to sit up straight, take breaks, etc.',
      author='(cdep) illabout',
      author_email='cdep.illabout@gmail.com',
      #url='http://www.python.org/sigs/distutils-sig/',
      packages=['postured'],
      package_dir={'postured': 'src/postured'},
      package_data={'postured': ['sounds/bell17.wav']},
      scripts=['scripts/postured'],
     )

