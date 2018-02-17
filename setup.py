import os
import sys
from distutils.core import setup

with open(os.path.join(os.path.dirname(__file__), 'requirements.txt')) as f:
    if sys.version_info[0] == 2:
        required = f.read().splitlines()
    else:
        required = []
        for package in f.read().splitlines():
            if 'futures' not in package:
                required.append(package)

setup(
    name='factscraper',
    version='0.5.3',
    packages=['factscraper'],
    install_requires=required,
    license='GNU General Public License v3.0',
)

