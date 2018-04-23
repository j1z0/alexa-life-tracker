import os
from setuptools import setup

# variables used in buildout
here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()

requires = [
    'pytest-runner',
    'boto3',
]

tests_require = [
    'pytest',
    'pytest-mock',
    'pytest-cov',
]

setup(
    name='life_tracker',
    version=open("sample/_version.py").readlines()[-1].split()[-1].strip("\"'"),
    description='alexa interface to track habbits and todos with fun integrations',
    long_description=README,
    packages=['life_tracker'],
    include_package_data=True,
    zip_safe=False,
    author='jeremy johnson',
    author_email='johnsonjp@gmaicom',
    url='https://j1z0.org',
    license='MIT',
    install_requires=requires,
    setup_requires=requires,
    tests_require=tests_require,
    extras_require={
        'test': tests_require,
    },
)
