from setuptools import setup

setup(
    name='zephony',
    packages=['zephony', 'zephony.models'],
    description='Helpers for Python web development',
    version='0.6',
    url='https://github.com/Zephony/zephony-pypi',
    author='Kevin Isaac',
    author_email='kevin@zephony.com',
    keywords=['zephony', 'helpers', 'web'],
    install_requires=[
        'voluptuous',
        'twilio',
    ],
)

