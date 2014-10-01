#!/bin/sh

# Die on errors
set -e

# Node.js packages from an external repo
# This script also runs apt-get update
apt-get install -y curl
curl -sL https://deb.nodesource.com/setup | bash -

apt-get install -y git build-essential \
                   python python-pip python-dev libmysqlclient-dev \
                   nodejs

# Global python packages
pip install virtualenv virtualenvwrapper

# Global node.js packages
npm install -g bower

BASHPROFILE=/etc/profile
if grep -q "virtualenvwrapper.sh" "$BASHPROFILE"; then
    echo "virtualenvwrapper already exists in $BASHPROFILE"
else
    cat <<EOF >> "$BASHPROFILE"

# Set up virtualenv and virtualenvwrapper
export VIRTUALENVWRAPPER_PYTHON=\$(command -v python2.7)
export WORKON_HOME=\$HOME/.virtualenvs
export PIP_DOWNLOAD_CACHE=\$HOME/.pip_download_cache
source \$(which virtualenvwrapper.sh)

EOF
    echo "virtualenvwrapper installed in $BASHPROFILE"
fi
