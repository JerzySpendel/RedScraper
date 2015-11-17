from setuptools import setup


setup(
    name='redscraper',
    version='0.1',
    author='Jerzy Spendel',
    packages=['redscraper'],
    scripts=['redscraper/redscraper.py'],
    package_data={'redscraper': ['config_schema.yml',
                                 'sample_new_project.py.sample'
                                 ]},
    include_package_data=True,
)