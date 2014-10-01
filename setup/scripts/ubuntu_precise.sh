#!/bin/sh

# Die on errors
set -e

apt-get update -y

# Python system packages
apt-get install -y python python-pip

# Node.js packages
apt-get install -y nodejs npm

# Global python packages
pip install virtualenv virtualenvwrapper
