from setuptools import setup
with open('README.md') as f:
    readme = f.read()

requires = ['pyserial']
tests_require = ['nose']

setup(
    name='pyenttec',
    install_requires=requires,
    tests_require=tests_require,
    test_suite="nose.collector",
    version='1.1',
    author='Chris Macklin',
    author_email='chris@imaginaryphotons.com',
    license='GPL3',
    description='Control an Enttec Pro DMX from python.',
    long_description=readme,
    long_description_content_type='text/markdown',
    packages=setuptools.find_packages(),
)
