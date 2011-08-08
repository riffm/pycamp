from distutils.core import setup

version = '0.1'

setup(
    name='pycamp',
    version=version,
    description='Centralized virtualenvs manager and command executor',
    long_description=open('README.rst').read()+'\n\n'+open('CHANGELOG').read(),
    py_modules=['pycamp'],
    license='MIT',
    author='Tim Perevezentsev',
    author_email='riffm2005@gmail.com',
    url='http://github.com/riffm/pycamp'
)

