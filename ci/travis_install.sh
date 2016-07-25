#!/usr/bin/env bash

set -ex

CMAKE_VERSION=3.5

if [[ "$TRAVIS_OS_NAME" == "osx" ]]; then
  CMAKE_OS="Darwin"
  PIP_EXTRA_ARGS="--user"

  install_cmake () {
    local prefix="/usr/local/bin"
    echo "Removing any existing CMake in $prefix"
    sudo rm -f \
      "$prefix/cmake" \
      "$prefix/cpack" \
      "$prefix/cmake-gui" \
      "$prefix/ccmake" \
      "$prefix/ctest"
    echo "Installing CMake in $prefix"
    sudo "$1/CMake.app/Contents/bin/cmake-gui" --install
  }

else
  CMAKE_OS="Linux"
  PIP_EXTRA_ARGS=""

  install_cmake () {
    echo "Copying $1/* to /usr/local"
    sudo rsync -avz "$1/" /usr/local
  }

fi

CMAKE_NAME="cmake-$CMAKE_VERSION.0-$CMAKE_OS-x86_64"
CMAKE_PACKAGE="$CMAKE_NAME.tar.gz"

echo "Downloading $CMAKE_PACKAGE"
wget --no-check-certificate --progress=dot \
      "https://cmake.org/files/v$CMAKE_VERSION/$CMAKE_PACKAGE"

echo "Extracting $CMAKE_PACKAGE.tar.gz"
tar xzf "$CMAKE_PACKAGE"

install_cmake $CMAKE_NAME

pip install -r requirements.txt ${PIP_EXTRA_ARGS}

pip install -r requirements-dev.txt ${PIP_EXTRA_ARGS}
