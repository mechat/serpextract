"""Update the search_engines.pickle list contained within the package.
Use this before deploying an update"""
from __future__ import absolute_import, division, print_function

import argparse
import os
import sys
from collections import OrderedDict
from subprocess import Popen, PIPE

try:
    import cPickle as pickle
except ImportError:
    import pickle
try:
    import simplejson as json
except ImportError:
    import json
from six.moves.urllib.request import urlopen


_here = lambda *paths: os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    *paths)

def array(*args, **kwargs):
    if args:
        return list(args)
    if kwargs:
        return OrderedDict(kwargs)

piwik_search_engines = []
null = None


def parse_php(php_script):
    if_index = php_script.find('if ')

    start_index = php_script.find('array(', if_index) + 6
    end_index = php_script.rfind(');')

    json_body = php_script[start_index:end_index]

    for line in json_body.split('\n'):
        line = line.strip()

        # comments
        line = line.replace('//', '#')
        if (line.startswith('#')
            or line.startswith('/*')
            or line.startswith('*')
            or line.startswith('*/')
            or line == ''):
            continue
            
        k, v = line.split('=>', 1)
        k = k.strip().strip("'")
        v = eval(v)[0]
        piwik_search_engines.append((k, v))

    return OrderedDict(piwik_search_engines)


def main():
    parser = argparse.ArgumentParser(description='Update SearchEngines.php or search_engines.*.pickle')
    parser.add_argument('target',
                        choices=['php', 'pickle'],
                        help='php: SearchEngines.php, pickle: search_engines.*.pickle')
    args = parser.parse_args()

    local_filename = _here('SearchEngines.php')

    if args.target == 'php':
        print('Updating search engine parser definitions from piwik (requires PHP).')

        # load from piwik
        piwik_url = 'https://raw.githubusercontent.com/piwik/piwik/2.14.3/core/DataFiles/SearchEngines.php'
        piwik_f = urlopen(piwik_url)
        php_script = piwik_f.read()

        # save into local SearchEngines.php
        with open(local_filename, 'w') as local_f:
            local_f.write(php_script)

        print('Saved piwik search engine parser definitions into %s' % local_filename)
    elif args.target == 'pickle':
        with open(local_filename) as local_f:
            php_script = local_f.read()

        piwik_engines = parse_php(php_script)
        py_version = sys.version_info[0]
        filename = _here('serpextract', 'search_engines.py{}.pickle'.format(py_version))
        with open(filename, 'wb') as pickle_file:
            pickle.dump(piwik_engines, pickle_file)

        print('Saved {} search engine parser definitions into {}.'
              .format(len(piwik_engines), filename))


if __name__ == '__main__':
    main()
