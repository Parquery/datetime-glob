"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""
import os

from setuptools import setup, find_packages

# pylint: disable=redefined-builtin

here = os.path.abspath(os.path.dirname(__file__))  # pylint: disable=invalid-name

with open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()  # pylint: disable=invalid-name

setup(
    name='datetime-glob',
    version='1.0.6',
    description='Parses date/time from paths using glob wildcard pattern intertwined with date/time format',
    long_description=long_description,
    url='https://bitbucket.org/parqueryopen/datetime-glob',
    author='Marko Ristin',
    author_email='marko@parquery.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='date time datetime parse glob pattern strptime wildcards',
    python_requires='>=3.5',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    install_requires=['lexery>=1.0.0'],
    extras_require={'dev': ['mypy==0.560', 'pylint==1.8.2', 'yapf==0.20.2']},
    py_modules=['datetime_glob'])
