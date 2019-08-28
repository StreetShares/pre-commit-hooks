#!/usr/bin/env python

"""StreetShares Dynamic Pylint Wrapper
Runs pylint within a docker container.  If within the service.config
PYTHON_VERSION is set, then the appropriate version of pylint will be executed
against the code base, else skip for now.

Return Codes:
    0 - Perfect Linting! 10/10 Gold Stars!
    3 - k8s/service.config not in repo.
    4 - pylint linting error.
"""

from __future__ import print_function

import argparse
import re
import subprocess
import os

def _get_python_major_version(service_config_file):
    regex = re.compile(r"^PYTHON_VERSION\s*=\s*([^.]).*$")
    try:
        with open(service_config_file) as file:
            for line in file:
                result_match = re.search(regex, line)
                if result_match:
                    result = result_match.group(1)
                    break
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
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    output = proc.communicate()[0]
    proc.wait()

    return(proc.returncode, output.decode("utf-8"))


def main(argv=None):
    """Runs appropriate pylint from docker container.
    Returns:
        STDOUT of pylint or pylint not found.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'filenames', nargs='*',
        help='Filenames pre-commit believes are changed.',
        default='.'
    )
    service_config_file = 'k8s/service.config'
    python_major_version = _get_python_major_version(service_config_file)
    args = parser.parse_args(argv)

    # Determine which docker image to use based on the major version of python
    # for the repo.
    if python_major_version == '2':
        tag = '1.9.5'
        image_name = 'pylint-pre-commit:' + tag
    elif python_major_version == '3':
        tag = '2.3.1'
        image_name = 'pylint-pre-commit:' + tag
    else:
        print('PYTHON_VERSION not set in {}.  Skipping...'.format(
            service_config_file
        ))
        # For now we are going to skip. PYTHON_VERSION  needs to be set
        # everywhere, but that will not happen immediatly.  Switch this over
        # after some time out in the wild.
        return_code = 0
        return return_code

    if len(args.filenames) > 1:
        python_files = ''
        for file in args.filenames:
            python_files += file + ' '
    else:
        python_files = args.filenames

    _, image_available = _run_cmd('docker images --format "{{.Repository}}:{{.Tag}}"')
    if image_name not in image_available:
        print('{} docker image not found.  Building...'.format(image_name))
        _run_cmd('docker build -t {image_name} {dockerfile_location}'.format(
            image_name=image_name,
            dockerfile_location=os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                '../docker/pylint/{}'.format(tag)
            )
        ))

    docker_cmd = ('docker run --rm -v {mount_origin}:/data {image} {files}'.format(
        mount_origin=os.getcwd(),
        image=image_name,
        files=python_files
    ))

    return_code, output = _run_cmd(docker_cmd)

    print(output)

    return return_code

if __name__ == '__main__':
    exit(main())
