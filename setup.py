import setuptools
with open('README.md') as f:
    readme = f.read()

requires = ['pyserial']
tests_require = ['nose']

setuptools.setup(
    name='pyenttec',
    install_requires=requires,
    tests_require=tests_require,
    test_suite="nose.collector",
    version='1.4',
    author='Chris Macklin',
    author_email='chris.macklin@gmail.com',
    license='MIT',
    description='Control an Enttec Pro DMX from python.',
    long_description=readme,
    long_description_content_type='text/markdown',
    packages=setuptools.find_packages(),
)
