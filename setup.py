from setuptools import setup

setup(
    name='zephony',
    packages=['zephony'],
    description='Helper functions for Python web development',
    version='0.3',
    url='https://github.com/Zephony/zephony-pypi',
    author='Kevin Isaac',
    author_email='kevin@zephony.com',
    keywords=['zephony', 'helpers', 'web'],
    install_requires=[
        'voluptuous',
        'twilio',
    ],
)

