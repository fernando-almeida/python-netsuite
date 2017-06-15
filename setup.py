# -*- encoding: utf-8 -*-
from setuptools import setup, find_packages
import netsuite as app

setup(
    name="netsuite",
    version=app.__version__,
    description='Netsuite Python Toolkit for SuiteTalk SOAP API',
    long_description=open('README.rst').read(),
    license='BSD License',
    platforms=['OS Independent'],
    keywords='Netsuite,Python,SuiteTalk,SOAP,API',
    author='Fernando Almeida',
    author_email='nanditu@gmail.com',
    url="https://github.com/fernando-almeida/python-netsuite.git",
    packages=find_packages(),
    include_package_data=True,
    install_requires=['zeep'],
)
