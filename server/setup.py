#!/usr/bin/env python

import setuptools

setuptools.setup(name='orwell::admin',
      version='1.0',
      description='Orwell admin interface, server part. Depends on client part.',
      author='Orwell',
      url='https://github.com/orwell-int/messages',
      packages=['orwell', 'orwell.admin'],
      install_requires=[
            "protobuf==3.8.0",
            "six==1.12.0",
            "tornado==6.0.3",
            "pyzmq==18.1.0",
            "graphene-tornado==2.5.0",
      ],
     )