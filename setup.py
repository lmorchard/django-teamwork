#!/usr/bin/env python
from setuptools import setup
try:
    import multiprocessing
except ImportError:
    pass


setup(
    name='django-teamwork',
    version='0.0.2',
    description='Django app that offers an authorization backend with support for per-object permissions based on combinations of Teams, Roles, and Policies.',
    long_description=open('README.rst').read(),
    author='Les Orchard',
    author_email='me@lmorchard.com',
    url='http://github.com/lmorchard/django-teamwork',
    license='BSD',
    packages=['teamwork'],
    package_data={},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=[
        'django>=1.4',
    ],
    tests_require=[
        'nose',
        'django-nose',
        'pyquery',
        'feedparser',
    ],
    test_suite='manage.nose_collector',
)
