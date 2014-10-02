chat.data.uw.edu
================
----------------

## Installation and configuration

1.  Install Python, virtualenv and npm.

2.  Make, enter and activate a virtualenv.

        $ virtualenv dsechat --no-site-packages
        New python executable in dsechat/bin/python
        Installing setuptools............done.
        $ cd dsechat/
        $ . bin/activate

3.  Clone this repo:

        $ cd ~
        $ git clone https://github.com/scclab/dsechatweb.git
        $ cd dsechatweb/

4.  Install the basic project requirements:

        $ pip install -r requirements/DEVELOPMENT
        $ pip install -r requirements/TESTING
        $ npm install
        $ bower install

5.  Generate an environment file and edit manually as needed:
        
        $ fab envfile:development

6.  Run the development webserver:
        
        $ ./manage.py serve


## Testing with Vagrant

Create a vagrant box and install some stuff:
    
    # A folder that will sync the project files on the guest vm
    $ mkdir vagrant_deploy
    $ vagrant up
    $ fab vagrant install
    $ fab vagrant staging

Next, SSH into the VM (or open the synced folder `vagrant_deploy`)
and set up the .env file:
    
    # ssh'ed into the VM
    $ workon dsechatweb
    $ cp conf/.env .env

Check that everything looks ok.

Now, generate a sample nginx conf on the remote machine and customize it:

    # on the remote machine
    $ fab nginx_conf:conf/nginx_site.conf
    $ sudo cp conf/nginx_site.conf /etc/nginx/sites-available/dsechatweb.conf
    $ sudo ln -s /etc/nginx/sites-available/dsechatweb.conf /etc/nginx/sites-enabled/dsechatweb.conf
    $ sudo nginx -s reload
move the nginx configuration into /etc/nginx/sites-available
