from setuptools import setup


setup(
    name='redscraper',
    version='0.1',
    author='SkyGate',
    packages=['redscraper'],
    scripts=['redscraper/redscraper.py'],
    package_data={'redscraper': ['config_schema.yml',
                                 'sample_new_project.py.sample'
                                 ]},
    include_package_data=True,
    install_requires=[
        'aioredis',
        'aiohttp',
        'beautifulsoup4',
        'pyyaml',
        'lxml',
    ]
)