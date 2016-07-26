from setuptools import setup
with open('README.md') as f:
    readme = f.read()

requires = ['pyserial']

setup(
    name='pyenttec',
    install_requires=requires,
    version='1.0',
    author='Chris Macklin',
    author_email='chris@imaginaryphotons.com',
    license='GPL3',
    description='Control an Enttec Pro DMX from python.',
    long_description=readme,
    py_modules=['pyenttec'])