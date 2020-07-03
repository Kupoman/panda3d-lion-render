from setuptools import setup

__version__ = ''
#pylint: disable=exec-used
exec(open('lionrender/version.py').read())

setup(
    version=__version__,
    keywords='panda3d',
    packages=['lionrender'],
    install_requires=[
        'panda3d',
    ]
)
