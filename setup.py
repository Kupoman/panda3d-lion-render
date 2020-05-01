from setuptools import setup

__version__ = ''
#pylint: disable=exec-used
exec(open('panda3d-lion-render/version.py').read())

setup(
    version=__version__,
    keywords='panda3d',
    packages=['panda3d-lion-render'],
    install_requires=[
        'panda3d',
    ],
    setup_requires=[
    ],
    tests_require=[
        'pytest',
        'pylint',
    ],
)
