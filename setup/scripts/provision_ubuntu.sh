#!/bin/sh

# Die on errors
set -e

# Node.js packages from an external repo
# This script also runs apt-get update
apt-get install -y curl
curl -sL https://deb.nodesource.com/setup | bash -

apt-get install -y git build-essential \
                   mysql-server \
                   nginx \
                   python python-pip python-dev libmysqlclient-dev \
                   nodejs

# Global python packages
pip install virtualenv virtualenvwrapper

# Global node.js packages
npm install -g bower

# Finish installing virtualenvwrapper
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

# Disable the default nginx config
rm /etc/nginx/sites-enabled/default
#sudo ln -s /etc/nginx/sites-available/dsechat.conf sites-enabled/dsechat.conf

# Make sure services are started
service mysql start
service nginx start

# Create a database just for kicks
cat <<EOF | mysql -u root
CREATE DATABASE IF NOT EXISTS dsechatweb CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
GRANT ALL PRIVILEGES ON dsechatweb.* TO 'dsechatweb'@'localhost' IDENTIFIED BY 'password';
GRANT USAGE ON *.* TO 'dsechatweb'@'localhost';
EOF

