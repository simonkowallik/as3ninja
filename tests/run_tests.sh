#!/usr/bin/env bash

set -v -e

COVERAGE=""
if [[ "$REPORT" == "true" ]]
then
    COVERAGE="--cov=as3ninja --cov-report=xml"
fi

function docker_pytest() {
    py.test $COVERAGE \
        tests/test_api.py
}

if [[ "$DOCKER_TESTING" == "true" ]]
then
    # docker build & run
    docker build -t as3ninja:buildtest .
    docker run -d --rm \
        --name as3ninja_build \
        -p 127.0.0.1:8000:8000 \
        as3ninja:buildtest

    # run docker tests
    docker_pytest

    # stop container after tests
    docker container stop as3ninja_build

    # travis cron docker tests
    if [[ "$TRAVIS_EVENT_TYPE" == "cron" ]]
    then
        for tag in latest edge
        do
            docker run -d --rm \
                --name as3ninja_dockerhub \
                -p 127.0.0.1:8000:8000 \
                docker.io/simonkowallik/as3ninja:${tag}

            docker_pytest

            docker container stop as3ninja_dockerhub
        done
    fi
else
    set -v
    # run py.test
    py.test $COVERAGE \
        tests
fi
