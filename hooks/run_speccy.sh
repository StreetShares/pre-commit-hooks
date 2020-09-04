#!/usr/bin/env bash

#
# speccy_lint.sh
#

#
# This runs speccy linter, an OpenAPI
# linter. speccy must be installed for
# this to work.
#

set -euo pipefail

if ! command which speccy &>/dev/null; then
    >&2 echo 'speccy not found'
    exit 1
fi

speccy lint "$@" --rules=strict
