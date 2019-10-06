#!/usr/bin/env python

import setuptools

setuptools.setup(name='orwell::admin',
      version='1.0',
      description='Orwell admin interface, server part. Depends on client part.',
      author='Orwell',
      url='https://github.com/orwell-int/messages',
      packages=['orwell', 'orwell.admin'],
      install_requires=[
            "aniso8601==7.0.0",
            "graphene==2.1.8",
            "graphene-tornado==2.5.0",
            "graphql-core==2.2.1",
            "graphql-relay==2.0.0",
            "Jinja2==2.10.1",
            "MarkupSafe==1.1.1",
            "promise==2.2.1",
            "protobuf==3.8.0",
            "pyzmq==18.1.0",
            "Rx==1.6.1",
            "six==1.12.0",
            "tornado==6.0.3",
            "Werkzeug==0.12.2",
      ],
     )