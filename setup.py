#!/usr/bin/env python

from distutils.core import setup

setup(name='Sphinx-Julia',
      version='0.2',
      description='Sphinx extensions for Julia',
      author='Sebastian Kraemer',
      author_email='basti.kr@gmail.com',
      url='https://github.com/bastikr/sphinx-julia',
      license='MIT',
      packages=['sphinxjulia'],
      package_data={'sphinxjulia': ['parsetools/*/*.jl']},
     )
