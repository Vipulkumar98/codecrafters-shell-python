#!/bin/sh
#
# This script is used to run your program on CodeCrafters
# 
# This runs after .codecrafters/compile.sh
#
# Learn more: https://codecrafters.io/program-interface

# Exit early if any commands fail
set -e
export PIPENV_VERBOSITY=-1
exec pipenv run python3 -u -m app.main "$@"
