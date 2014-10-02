chat.data.uw.edu
================
----------------

## Installation and configuration

1.  Install system-level packages that we need:
    - Python 2.7 with pip and virtualenv
    - Node.js v0.10
    - MySQL 5.5 
    - Nginx or some other web server

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

Next, assuming your database has already been created, make sure 
it is properly entered into the newly-created `.env` file on the VM.

If that looks ok, you can run the staging command:

    $ fab vagrant staging

Now, generate a sample nginx conf on the remote machine and customize it:

    # On the VM...
    $ fab gen_nginx_conf
    # Take a look and make sure it has everything right
    $ sudo mv nginx.conf /etc/nginx/sites-available/dsechatweb.conf
    $ sudo ln -s /etc/nginx/sites-available/dsechatweb.conf /etc/nginx/sites-enabled/dsechatweb.conf
    $ sudo nginx -s reload

You may also want to generate an upstart conf file:

    # On the VM...
    $ fab upstart_conf
    # Check that it looks right
    $ sudo mv upstart.conf /etc/init/dsechatweb.conf
    $ sudo start dsechatweb
        
