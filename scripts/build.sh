#!/usr/bin/env bash

set -e

pushd ui
yarn build
popd

poetry build --format=sdist
