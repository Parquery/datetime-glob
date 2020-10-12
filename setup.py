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
    version='1.0.7',
    description='Parse date/time from paths using glob wildcard pattern intertwined with date/time format',
    long_description=long_description,
    url='https://github.com/Parquery/datetime-glob',
    author='Marko Ristin',
    author_email='marko.ristin@gmail.com',
    # yapf: disable
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    # yapf: enable
    keywords='date time datetime parse glob pattern strptime wildcards',
    python_requires='>=3.5',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    install_requires=['lexery>=1.0.0'],
    # yapf: disable
    extras_require={
        'dev': ['coverage>=5,<6', 'mypy==0.790', 'pylint==2.6.0', 'yapf==0.20.2', 'pydocstyle>=5.0.0,<6', 'twine']
    },
    # yapf: enable
    py_modules=['datetime_glob'],
    package_data={"datetime_glob": ["py.typed"]})
