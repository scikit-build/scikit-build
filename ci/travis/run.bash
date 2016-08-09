#!/usr/bin/env bash

set -ex

if [ "$TRAVIS_OS_NAME" = "osx" ]; then
  eval "$( pyenv init - )"
  pyenv local $PYTHONVERSION
fi

eval "$@"

