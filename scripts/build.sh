#!/usr/bin/env bash

set -e

pushd ui
yarn build
popd

uvx hatch build -t sdist
