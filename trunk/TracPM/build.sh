#! /bin/bash
python setup.py bdist_egg

cp -v dist/*.egg /web/trac/trac1.0/plugins/


