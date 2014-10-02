# -*- coding: utf-8 -*-

import sys
import os

from fabric.api import local, env, run, cd, lcd
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

def _backup_file(file_path):
    with warn_only():
        local('cp %s %s.bak 2> /dev/null || :' % (file_path, file_path))

def _jinja_render(template, template_dir=root_dir, context={}):
    """Render a template. Expects path relative to root_dir."""
    from jinja2 import Environment, FileSystemLoader
    environment = Environment(loader=FileSystemLoader(template_dir))

    template = environment.get_template(template)
    return template.render(context)


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


def _no_file_or_backed_up(target_file):
    if files.exists(target_file):
        print yellow("Already exists: %s" % target_file)
        if not console.confirm("Generate a new one? (the old one will be backed up)", False):
            return True
        return False
    return True


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

def _common_settings():
    package = _read_package()
    env.app_name = package['name']
    env.repo_url = package['repository']
    env.django_settings_module = 'dsechat.settings.production'


def production():
    """Prepare to connect to the production server"""
    _common_settings()

    env.machine_target = 'production'

    denv = _read_env()

    env.host_string = denv['PRODUCTION_HOST']
    env.user = denv['PRODUCTION_USER']

    env.target_directory = denv.get('PRODUCTION_APPDIR', '~/' + env.app_name)
    env.pip_requirements = ('requirements/PRODUCTION',)

    if env.target_directory == "~/":
        print yellow("You must have 'name' in your package.json file or set PRODUCTION_APPDIR in your .env file")
        exit(1)


def vagrant():
    """Prepare to connect to a local vagrant VM"""
    _common_settings()

    env.machine_target = 'vagrant'

    env.host_string = '127.0.0.1:2222'
    env.user = 'vagrant'
    env.key_filename = _read_vagrant_keyfile()
    env.disable_known_hosts = True

    env.target_directory = '~/' + env.app_name
    env.pip_requirements = ('requirements/DEVELOPMENT', 'requirements/PRODUCTION')

    if env.target_directory == "~/":
        print yellow("You must have 'name' in your package.json file")
        exit(1)


def _install_dependencies():
    """Installs local packages"""
    print green("Installing python requirements...")
    for req in env.pip_requirements:
        run('pip install -r %s' % req)

    print green("Installing node.js requirements...")
    run('npm install --no-bin-link')

    print green("Installing bower requirements...")
    run('bower install --config.interactive=false')


def install():
    """Checks some system requirements and checks out the project code"""

    if 'target_directory' not in env:
        print yellow("Run 'fab production install' to load remote configuration")
        exit(1)

    print green("Checking system requirements...")
    _require_command('git')
    _require_command('pip', 'mkvirtualenv', 'rmvirtualenv')
    _require_command('npm', 'bower')
    print green("All good.")

    print green("Making sure we haven't already done this...")

    skip_proj_dir = False
    if files.exists(env.target_directory):
        print yellow("The app target directory already exists." % env)
        if console.confirm("Would you like to clean %(target_directory)s?" % env, False):
            with hide('everything'):
                run('rm -rf %(target_directory)s/* %(target_directory)s/.*' % env, warn_only=True)
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

    _install_dependencies()

    dot_env_file = env.target_directory + '/.env'
    if _no_file_or_backed_up(dot_env_file):
        gen_dot_env(dot_env_file)

    print green('----------- .env file -------------')

    run('cat %s' % dot_env_file)

    print green('-----------------------------------')
    print
    print yellow("Things you still need to do:")
    print yellow("  - Make sure your database is ready for access")
    print yellow("  - Make sure your %s file contains the proper database settings." % dot_env_file)
    print yellow("  - Check your webserver configuration (use 'fab nginx_conf')")
    print yellow("  - Install an upstart service (use 'fab upstart_conf')")
    print yellow("  - Finish setting up the application with the 'fab %s staging'" % env.machine_target)
    print green("Initial install complete.")


def staging():
    """Update the code and project requirements"""
    with prefix('workon %(app_name)s' % env):

        print green("Pulling master from GitHub...")
        run('git pull origin master')

        _install_dependencies()

        print green("Running migrations...")
        run('python manage.py migrate')

        print green("Gathering and preprocessing static files...")
        run('python manage.py collectstatic --noinput')
        run('python manage.py compress')

        print green("Restarting the web process...")


def gen_nginx_conf(nginx_conf_file='nginx.conf'):
    """Generate a sample nginx conf file"""
    _common_settings()

    import os
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", env.django_settings_module)

    sys.path.append(root_dir)
    from django.conf import settings
    from datetime import datetime
    nginx_context = {
        'app_name': env.get('app_name', 'my_special_app'),
        'generated_time': datetime.now(),
        'settings': settings,
    }

    newconf = _jinja_render('nginx.conf', template_dir='setup/templates', context=nginx_context)

    # Back up first
    _backup_file(nginx_conf_file)

    with open(nginx_conf_file, 'w') as outfile:
        outfile.write(newconf)

    print green("Created a sample nginx conf file at %s" % nginx_conf_file)


def gen_upstart_conf(upstart_conf_file='upstart.conf'):
    """Generate a sample upstart conf file"""
    _common_settings()

    import os
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', env.django_settings_module)

    sys.path.append(root_dir)
    from django.conf import settings
    from datetime import datetime
    upstart_context = {
        'upstart_log': '/var/log/%s.upstart.log' % env.app_name,
        'username': os.environ.get('USER'),
        'venv_dir': os.environ.get('VIRTUAL_ENV'),
        'generated_time': datetime.now(),
        'settings': settings,
    }

    newconf = _jinja_render('upstart.conf', template_dir='setup/templates', context=upstart_context)

    # Back up first
    _backup_file(upstart_conf_file)

    with open(upstart_conf_file, 'w') as outfile:
        outfile.write(newconf)

    print green("Created a sample upstart init file at %s" % upstart_conf_file)

def gen_dot_env(dot_env_file='.env'):
    """Generates a .env file"""
    import base64
    from datetime import datetime
    env_context = {
        'django_settings_module': env.get('django_settings_module', 'dsechat.settings.development'),
        'app_name': env.get('app_name', 'something'),
        'secret_key': base64.b64encode(os.urandom(24)),
        'generated_time': datetime.now(),
    }

    files.upload_template('dot_env.txt', dot_env_file,
                          context=env_context, use_jinja=True, template_dir='setup/templates',
                          mode=0600) # make it secret

    print green("Created a starter environment file at %s" % dot_env_file)


def gen_supervisor_conf(conf_file='supervisord.conf.tmp'):
    """Generates a supervisord conf file based on the django template supervisord.conf"""
    # Back up first
    _backup_file(conf_file)

    local('python manage.py supervisor getconfig > %s' % conf_file)
    print green("Wrote supervisor conf file to %s" % conf_file)

def _web_pid():
    """Get the pid of the web process"""
    with quiet():
        local('python manage.py supervisor getconfig > .tmpsupervisord.conf')
        pid = local('supervisorctl -c .tmpsupervisord.conf pid web', capture=True)
        local('rm .tmpsupervisord.conf')
        return pid

def status():
    """Get the status of supervisor processes"""
    with hide('running'):
        local('python manage.py supervisor getconfig > .tmpsupervisord.conf')
        local('supervisorctl -c .tmpsupervisord.conf status')
        local('rm .tmpsupervisord.conf')

def web_refresh():
    """Trigger Gunicorn's 'hot refresh' feature."""
    with lcd(root_dir):
        pid = _web_pid()
        local('kill -HUP %s' % pid)

def web_restart():
    """Hard restart Gunicorn"""
    local('python manage.py supervisor restart web')

def web_count():
    """Get the current gunicorn web worker count"""
    with lcd(root_dir):
        with hide('running'):
            count = int(local('ps -C gunicorn --no-headers | wc -l', capture=True))

        if count > 0:
            count -= 1

        if count == 1:
            print ("There is %d gunicorn worker running" % count)
        else:
            print ("There are %d gunicorn workers running" % count)

        return count


def web_scale(direction='up'):
    """Scale up or down the gunicorn web workers"""
    with lcd(root_dir):

        before = web_count()

        with hide('running'):
            pid = _web_pid()

            if direction == 'up':
                print ("Scaling up gunicorn workers for master pid %s..." % pid)
                local('kill -TTIN %s' % pid)
            elif direction == 'down':
                if before > 1:
                    print ("Scaling down gunicorn workers for master pid %s..." % pid)
                    local('kill -TTOU %s' % pid)
                else:
                    print ("There is only one web worker running. Use fab stop:web to kill gunicorn.")
                    return
            else:
                raise Exception("Direction argument must be 'up' or 'down'")
        import time
        time.sleep(1)
        count = web_count()
        if count == before:
            print ("Changes may not be immediately reflected. Check 'fab web_count' in a moment.")
