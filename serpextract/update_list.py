#! /usr/bin/python
# -*- coding: utf-8 -*-

"""Update the search_engines.pickle list contained within the package.
Use this before deploying an update"""
from collections import OrderedDict
import os
from urllib2 import urlopen
from subprocess import Popen, PIPE, STDOUT
try:
    import cPickle as pickle
except ImportError:
    import pickle
try:
    import simplejson as json
except ImportError:
    import json

import serpextract

_here = lambda *paths: os.path.join(
    os.path.dirname(
        os.path.dirname(os.path.abspath(serpextract.__file__))
    ), *paths
)


def main():

    pickle_filename = _here('serpextract', 'search_engines.pickle')
    php_file = 'SearchEngines.php'

    with open(php_file) as f:
        php_script = f.read()
        process = Popen(['php'], stdout=PIPE, stdin=PIPE, stderr=PIPE)
        json_string = process.communicate(input=php_script)[0]

    piwik_engines = json.loads(json_string, object_pairs_hook=OrderedDict)

    result = {}
    for engine, items in piwik_engines.items():
        result[engine] = items

    with open(pickle_filename, 'w') as f:
        pickle.dump(result, f)

    print('Saved {} search engine parser definitions to {}.'.format(len(piwik_engines), pickle_filename))


if __name__ == '__main__':
    main()


