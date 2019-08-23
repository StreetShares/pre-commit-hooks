#!/usr/bin/env python

"""StreetShares Dynamic Pylint Wrapper
Runs pylint based on the PYTHON_VERSION of the repo.  If within the
service.config, PYTHON_VERSION is set, then the appropriate version of pylint
will be executed against the code base, else fall back to the current python in
the PATH.

Return Codes:
    0 - Perfect Linting! 10/10 Gold Stars!
    3 - k8s/service.config not in repo.
    4 - pylint linting error.
"""

from __future__ import print_function

import argparse
import re
import subprocess

def _get_python_major_version(service_config_file):
    regex = re.compile(r"^PYTHON_VERSION\s*=\s*([^.]).*$")
    try:
        with open(service_config_file) as file:
            for line in file:
                result_match = re.search(regex, line)
                if result_match:
                    result = result_match.group(1)
                else:
                    result = None
    except IOError:
        print("Unable to open file: {}".format(service_config_file))
        result = None

    return result

def _run_cmd(cmd):
    """Executed shell command
    Returns:
          STDOUT of successful command execution
    """
    proc = subprocess.Popen(
        cmd,
        shell=True
    )
    proc.communicate()
    return proc.returncode


def main(argv=None):
    """Runs appropriate pylint.
    Returns:
        STDOUT of pylint or pylint not found.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'filenames', nargs='*',
        help='Filenames pre-commit believes are changed.',
    )
    service_config_file = 'k8s/service.config'
    python_major_version = _get_python_major_version(service_config_file)
    args = parser.parse_args(argv)

    python3_pylint = 'python3 -mpylint {}'.format(' '.join(args.filenames))
    python_pylint = 'python -mpylint {}'.format(' '.join(args.filenames))

    if python_major_version == '3':
        return_code = _run_cmd(python3_pylint)
    elif python_major_version == '2':
        return_code = _run_cmd(python_pylint)
    else:
        print('PYTHON_VERSION not set correctly in your {}'.format)
        return_code = 3

    return return_code

if __name__ == '__main__':
    exit(main())
