from setuptools import setup

setup(
    name='schmittie-chess',
    version='0.1.0',
    description='Small Chess GUI and rudimentary engine that destroys me. ',
    url='',
    author='Sebastian Schmitt',
    author_email='s.schmitt@cern.ch',
    license='MIT',
    packages=['schmittie_chess'],
    install_requirements=['chess', 
                          'pygame',
                          'numpy'],
    classifiers=['Programming Language :: Python :: 3.10',
                 'Programming Language :: Python :: 3.11',
                 'Programming Language :: Python :: 3.12'],
)