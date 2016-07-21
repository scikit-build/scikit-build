#!/usr/bin/env bash

set -ex

CMAKE_VERSION=3.5

if [[ "$TRAVIS_OS_NAME" == "osx" ]]; then
  CMAKE_OS="Darwin"
  PIP_EXTRA_ARGS="--user"
else
  CMAKE_OS="Linux"
  PIP_EXTRA_ARGS=""
fi

CMAKE_NAME="cmake-$CMAKE_VERSION.0-$CMAKE_OS-x86_64"
CMAKE_PACKAGE="$CMAKE_NAME.tar.gz"

echo "Downloading $CMAKE_PACKAGE"
wget --no-check-certificate --progress=dot \
      "https://cmake.org/files/v$CMAKE_VERSION/$CMAKE_PACKAGE"

echo "Extracting $CMAKE_PACKAGE.tar.gz"
tar xzf "$CMAKE_PACKAGE"

echo "Copying $CMAKE_NAME/* to /usr/local"
sudo rsync -avz "$CMAKE_NAME/" /usr/local

pip install -r requirements.txt ${PIP_EXTRA_ARGS}

pip install -r requirements-dev.txt ${PIP_EXTRA_ARGS}
