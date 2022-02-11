#!/usr/bin/env python

import setuptools

setuptools.setup(name='orwell::admin',
      version='1.0',
      description='Orwell admin interface, server part. Depends on client part.',
      author='Orwell',
      url='https://github.com/orwell-int/messages',
      packages=['orwell', 'orwell.admin'],
      install_requires=[
            "aiohttp==3.6.2",
            "aniso8601==7.0.0",
            "async-timeout==3.0.1",
            "attrs==19.2.0",
            "chardet==3.0.4",
            "graphene==2.1.8",
            "graphql-core==2.2.1",
            "graphql-relay==2.0.0",
            "graphql-ws==0.3.0",
            "idna==2.8",
            "multidict==4.5.2",
            "netifaces==0.10.9",
            "promise==2.2.1",
            "protobuf==3.15.0",
            "pyzmq==18.1.0",
            "Rx==1.6.1",
            "six==1.12.0",
            "yarl==1.3.0",
      ],
     )