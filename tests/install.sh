#!/usr/bin/env bash
set -v -e

# set pip
pip=$(type -p pip3 || type -p pip)

# remove old python, avoid interferances
sudo apt-get remove python2.7

# install required tooling
$pip install codecov poetry

# install dependencies including dev
poetry export --dev -f requirements.txt -o requirements.txt
$pip install -r requirements.txt

# add docker when docker testing is requested
if [[ "$DOCKER_TESTING" == "true" ]]
then
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
    sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
    sudo apt-get update
    sudo apt-get -y -o Dpkg::Options::="--force-confnew" install docker-ce
fi
