#!/bin/sh

# Die on errors
set -e

# Node.js packages from an external repo
# This script also runs apt-get update
apt-get install -y curl
curl -sL https://deb.nodesource.com/setup | bash -

# Prevent prompts from packages
export DEBIAN_FRONTEND=noninteractive

echo "Installing system packages..."
apt-get install -y git build-essential \
                   mysql-server \
                   nginx \
                   python python-pip python-dev libmysqlclient-dev \
                   nodejs \
                   emacs23-nox

# Global python packages
echo "Installing global python packages..."
pip install virtualenv virtualenvwrapper

# Global node.js packages
echo "Installing Bower..."
npm install -g bower

# Disable the default nginx config
rm -f /etc/nginx/sites-enabled/default
echo "Disabled /etc/nginx/sites-enabled/default"

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



# Make sure services are started
service mysql start || true
service nginx start || true

DBNAME=dsechatweb
DBUSER=dsechatweb
DBPASS=password
echo "Creating project database $DBNAME with access for $DBUSER@localhost and password=$DBPASS"

# Create a database just for kicks
cat <<EOF | mysql -u root
CREATE DATABASE IF NOT EXISTS $DBNAME CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
GRANT ALL PRIVILEGES ON $DBNAME.* TO '$DBUSER'@'localhost' IDENTIFIED BY '$DBPASS';
GRANT USAGE ON *.* TO '$DBUSER'@'localhost';
EOF

