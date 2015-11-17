#!/bin/bash python3
import argparse
import os


parser = argparse.ArgumentParser(description='Redscrapper project creating helper')
parser.add_argument('-n', dest='name', help="New project's name")


parsed = parser.parse_args()
package = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
schema_path = os.path.join(package, 'redscraper', 'config_schema.yml')
sample_path = os.path.join(package, 'redscraper', 'sample_new_project.py.sample')

if not os.path.isdir(parsed.name):
    os.mkdir(parsed.name)
else:
    print('New project is going to be deployed in existing directory')

open(os.path.join(parsed.name, parsed.name+'.py'), 'w').write(open(sample_path, 'r').read())
open(os.path.join(parsed.name, 'config.yml'), 'w').write(open(schema_path, 'r').read())
