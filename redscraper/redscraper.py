#!/bin/env python
import argparse
import os


parser = argparse.ArgumentParser(description='Redscrapper project creating helper')
parser.add_argument('-n', dest='name', help="New project's name", required=True)


parsed = parser.parse_args()
package = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
schema_path = os.path.join(package, 'redscraper', 'config_schema.yml')
sample_path = os.path.join(package, 'redscraper', 'sample_new_project.py.sample')
write_schema_path = os.path.join(parsed.name, parsed.name+'.py')
write_config_path = os.path.join(parsed.name, 'config.yml')

if not os.path.isdir(parsed.name):
    os.mkdir(parsed.name)
else:
    print('New project is going to be deployed in existing directory')

if not os.path.exists(write_schema_path):
    open(write_schema_path, 'w').write(open(sample_path, 'r').read())
else:
    print('File {} already exists'.format(os.path.split(write_schema_path)[1]))

if not os.path.exists(write_config_path):
    open(write_config_path, 'w').write(open(schema_path, 'r').read())
else:
    print('File {} already exists'.format(os.path.split(write_config_path)[1]))