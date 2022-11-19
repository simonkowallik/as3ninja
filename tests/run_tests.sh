#!/usr/bin/env bash

set -v -e

COVERAGE=""
if [[ "$REPORT" == "true" ]]
then
    COVERAGE="--cov=as3ninja"
fi

function docker_pytest() {
    # give the container time to start
    echo -n "waiting for container to be reachable:"
    cnt=0
    while true
    do
        if [[ $(curl -s http://localhost:8000/api/schema/latest_version | grep latest_version) =~ "latest_version" ]]
        then
            echo "reachable"
            sleep 5
            break
        elif [[ $cnt -eq 120 ]]
        then
            echo
            echo "ERROR: API in docker container unreachable after 120 tries."
            exit 1
        fi
        cnt=$(($cnt+1))
        echo -n "."
        sleep 5
    done
    # run tests
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

    # print container logs
    docker logs as3ninja_build

    # stop container after tests
    docker container stop as3ninja_build

    # travis cron docker tests
    if [[ "$TRAVIS_EVENT_TYPE" == "cron" ]]
    then
        for tag in latest edge
        do
            if [[ "$tag" == "$TRAVIS_BRANCH" ]]
            then
                # run tests for container matching specified branch
                docker run -d --rm \
                    --name as3ninja_dockerhub \
                    -p 127.0.0.1:8000:8000 \
                    docker.io/simonkowallik/as3ninja:${tag}

                # run docker tests
                docker_pytest

                # print container logs
                docker logs as3ninja_dockerhub

                # stop container after tests
                docker container stop as3ninja_dockerhub
            fi
        done
    fi
else
    set -v
    # run py.test
    py.test $COVERAGE \
        tests
fi
