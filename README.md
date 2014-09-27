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
