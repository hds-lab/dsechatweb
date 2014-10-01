# -*- coding: utf-8 -*-

import sys
import os

from fabric.api import local, env, run, cd
from fabric.contrib import files, console
from fabric.colors import red, green, yellow
from fabric.context_managers import warn_only, quiet, prefix, hide

root_dir = os.path.dirname(os.path.realpath(__file__))

_env_already_read = None


def _read_env():
    global _env_already_read

    if not _env_already_read:
        sys.path.append(root_dir)
        from dsechat.libs import env_file

        _env_already_read = env_file.read()

    return _env_already_read


_package_already_read = None


def _read_package():
    """Parse the package.json file"""
    global _package_already_read

    if not _package_already_read:
        import json

        with open(os.path.join(root_dir, 'package.json')) as packfile:
            _package_already_read = json.load(packfile)
    return _package_already_read

def _check_exists(command):
    with quiet():
        return run('command -v %s' % command).succeeded

def _require_command(*commands):
    for command in commands:
        if not _check_exists(command):
            print red("Command '") + yellow(command) + red("' does not exist on the host!")
            exit(1)

def _command_succeeds(command):
    with quiet():
        return run(command).succeeded

def _read_vagrant_keyfile():
    """Get the private key file for connecting to the vagrant box"""
    with hide('running'):
        result = local('vagrant ssh-config', capture=True)
        for line in result.splitlines():
            line = line.strip()
            if line.startswith('IdentityFile '):
                return line[len('IdentityFile '):]


def _run_softly(*args, **kwargs):
    with hide('running', 'output'):
        return run(*args, **kwargs)


def test(integration=1):
    """
    Execute the tests suite with the correct settings. Accept one
    argument that indicates when execute unit tests or not.

    Usage:
        $ fab test
        $ fab test:integration=0
    """
    command = 'python manage.py test -v 2 --settings=dsechat.settings.testing'

    if int(integration) == 0:
        command += " --exclude='integration_tests' --exclude='jasmine_tests'"

    local(command)


def production():
    """Prepare to connect to the production server"""
    denv = _read_env()
    package = _read_package()

    env.host_string = denv['PRODUCTION_HOST']
    env.user = denv['PRODUCTION_USER']
    env.target_directory = denv.get('PRODUCTION_APPDIR', '~/' + package['name'])
    env.app_name = package['name']
    env.repo_url = package['repository']
    env.pip_requirements = 'requirements/PRODUCTION'
    env.django_settings_module = 'dsechat.settings.production'

    if env.target_directory == "~/":
        print yellow("You must have 'name' in your package.json file or set PRODUCTION_APPDIR in your .env file")
        exit(1)


def vagrant():
    denv = _read_env()
    package = _read_package()

    env.host_string = '127.0.0.1:2222'
    env.user = 'vagrant'
    env.key_filename = _read_vagrant_keyfile()
    env.disable_known_hosts = True

    env.target_directory = '~/' + package['name']

    env.app_name = package['name']
    env.repo_url = package['repository']
    env.pip_requirements = 'requirements/DEVELOPMENT requirements/PRODUCTION'
    env.django_settings_module = 'dsechat.settings.production'

    if env.target_directory == "~/":
        print yellow("You must have 'name' in your package.json file")
        exit(1)


def install():
    if 'target_directory' not in env:
        print yellow("Run 'fab production install' to load remote configuration")
        exit(1)

    print green("Checking system requirements...")
    _require_command('pip', 'mkvirtualenv', 'rmvirtualenv')
    _require_command('npm')
    print green("All good.")

    print green("Making sure we haven't already done this...")

    skip_proj_dir = False
    if files.exists(env.target_directory):
        print yellow("The app target directory already exists." % env)
        if console.confirm("Would you like to delete %(target_directory)s?" % env, False):
            _run_softly('rm -rf %(target_directory)s' % env)
        else:
            skip_proj_dir = True

    skip_virtualenv = False
    if _command_succeeds('workon %(app_name)s' % env):
        print yellow("The virtualenv already exists.")
        if console.confirm("Would you like to delete the %(app_name)s virtualenv?" % env, False):
            _run_softly('rmvirtualenv %(app_name)s' % env, quiet=False)
        else:
            skip_virtualenv = True

    if not skip_proj_dir:
        print green("Creating directory %(target_directory)s" % env)
        run('mkdir -p %(target_directory)s' % env)

    if not skip_virtualenv:
        print green("Creating the %(app_name)s virtualenv" % env)
        run('mkvirtualenv -a %(target_directory)s %(app_name)s' % env)

    if files.exists(env.target_directory + '/.git'):
        print yellow("The target directory already contains a git repo. Skipping git clone.")
    else:
        print green("Cloning the repository from GitHub...")
        with hide('output'):
            run('git clone %(repo_url)s %(target_directory)s' % env)

    dot_env_file = env.target_directory + '/.env'
    skip_env_file = False
    if files.exists(dot_env_file):
        print yellow("There is already an existing .env file.")
        if not console.confirm("Do you want to back it up and continue anyway?", False):
            skip_env_file = True

    if not skip_env_file:
        import base64
        from datetime import datetime
        env_context = {
            'django_settings_module': env.get('django_settings_module', 'dsechat.settings.development'),
            'app_name': env.get('app_name', 'something'),
            'secret_key': base64.b64encode(os.urandom(24)),
            'generated_time': datetime.now()
        }

        files.upload_template('dot_env.txt', dot_env_file,
                              context=env_context, use_jinja=True, template_dir='setup/templates',
                              mode=0600) # make it secret

        print green("Created an incomplete environment file at %s" % dot_env_file)

    print yellow("Don't forget to edit the .env file with your deployment settings.")
    print yellow("You still need to configure:")
    print yellow("  - A MySQL database")
    print yellow("  - Your web server pointing to the django app")
    print yellow("  - The contact info and xmpp details")
    print yellow("  - An upstart job to keep the server running")

    print green("Initial install complete. Ready for staging.")

def staging():
    # path to the directory on the server where your vhost is set up
    path = "/home/ubuntu/www/dev.yaconiello.com"
    # name of the application process
    process = "staging"

    with prefix('workon %(app_name)s' % env):
        print green("Installing python requirements...")
        run('pip install -r %(pip_requirements)s' % env)

    print(red("Beginning Deploy:"))
    with cd("%s/app" % path):
        run("pwd")
        print green("Pulling master from GitHub...")
        run("git pull origin master")
        print green("Installing npm and bower requirements...")
        run("npm install && bower install")
        print(green("Installing python requirements..."))
        run("source %s/venv/bin/activate && pip install -r requirements.txt" % path)
        print(green("Collecting static files..."))
        run("source %s/venv/bin/activate && python manage.py collectstatic --noinput" % path)
        print(green("Syncing the database..."))
        run("source %s/venv/bin/activate && python manage.py syncdb" % path)
        print(green("Migrating the database..."))
        run("source %s/venv/bin/activate && python manage.py migrate" % path)
        print(green("Restart the uwsgi process"))
        run("sudo service %s restart" % process)
    print(red("DONE!"))
