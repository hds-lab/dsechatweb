# -*- coding: utf-8 -*-

import sys
import os

from fabric.api import local, env, run, cd, lcd
from fabric.contrib import files, console
from fabric.colors import red, green, yellow
from fabric.context_managers import warn_only, quiet, prefix, hide
from contextlib import contextmanager as _contextmanager
from path import path

root_dir = path(__file__).abspath().realpath().dirname()
sys.path.append(root_dir)

def _is_local():
    return env.run == local

@_contextmanager
def _virtualenv():
    if _is_local():
        # Nothing to do
        yield
    else:
        with prefix('workon %s' % env.app_name):
            yield

def _remote(*args, **kwargs):
    if 'capture' in kwargs:
        del kwargs['capture']
    return run(*args, **kwargs)

_env_already_read = None


def _is_git_dirty():
    """Checks if the local repo has uncommitted changes"""

def _contains(string, options):
    """Check if the string contains any of the options"""
    for opt in options:
        if opt in string:
            return True

def _git_status():
    """Checks if the local git repo is ahead of the remote"""
    with quiet():
        result = local("git status", capture=True).lower()

        if _contains(result, ("untracked files:", "nothing added to commit but untracked files")):
            print yellow("Your git repo has untracked files that are being ignored.")

        if _contains(result, ("deleted:", "added:", "modified:", "renamed:")):
            print red("Your git repo has uncommitted changes.")
            return "dirty"

        if _contains(result, ("changes not staged for commit",)):
            print red("Your git repo has uncommitted changes.")
            return "dirty"

        if _contains(result, ("your branch is ahead",)):
            print red("Your git repo is ahead of the remote.")
            return "ahead"

        if _contains(result, ("nothing to commit",)):
            print green("Your git repo seems to be syncronized.")
            return "clean"

def _read_env():
    global _env_already_read

    if not _env_already_read:
        from dsechat.libs import env_file

        _env_already_read = env_file.read()

    return _env_already_read


_package_already_read = None


def _read_package():
    """Parse the package.json file"""
    global _package_already_read

    if not _package_already_read:
        import json

        with open(root_dir / 'package.json') as packfile:
            _package_already_read = json.load(packfile)
    return _package_already_read


def _check_exists(command):
    with quiet():
        return env.run('command -v %s' % command).succeeded


def _backup_file(file_path):
    with warn_only():
        env.run('cp %s %s.bak 2> /dev/null || :' % (file_path, file_path))


def _jinja_render(template, template_dir=root_dir, context=None):
    """Render a template. Expects path relative to root_dir."""
    from jinja2 import Environment, FileSystemLoader
    environment = Environment(loader=FileSystemLoader(template_dir))

    template = environment.get_template(template)
    return template.render(context)


def _get_settings():
    denv = _read_env()

    env.django_settings_module = denv.get('DJANGO_SETTINGS_MODULE', 'dsechat.settings.production')
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', env.django_settings_module)

    from django.conf import settings
    return settings


def _require_command(*commands):
    for command in commands:
        if not _check_exists(command):
            print red("Command '") + yellow(command) + red("' does not exist on the host!")
            exit(1)


def _command_succeeds(command):
    with quiet():
        return env.run(command).succeeded


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
        return env.run(*args, **kwargs)


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

    env.run(command)


def target_production():
    """Prepare to connect to the production server"""

    env.machine_target = 'production'
    env.run = _remote

    denv = _read_env()

    env.host_string = denv['PRODUCTION_HOST']
    env.user = denv['PRODUCTION_USER']

    env.target_directory = denv.get('PRODUCTION_APPDIR', '~/' + env.app_name)
    env.pip_requirements = ('requirements/PRODUCTION',)

    env.django_settings_module = 'dsechat.settings.production'
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', env.django_settings_module)

    if env.target_directory == "~/":
        print yellow("You must have 'name' in your package.json file or set PRODUCTION_APPDIR in your .env file")
        exit(1)

    print green("Running on %s" % env.host_string)


def target_vagrant():
    """Prepare to connect to a local vagrant VM"""

    env.machine_target = 'vagrant'
    env.run = _remote

    env.host_string = '127.0.0.1:2222'
    env.user = 'vagrant'
    env.key_filename = _read_vagrant_keyfile()
    env.disable_known_hosts = True

    env.target_directory = '~/' + env.app_name
    env.pip_requirements = ('requirements/DEVELOPMENT', 'requirements/PRODUCTION')

    if env.target_directory == "~/":
        print yellow("You must have 'name' in your package.json file")
        exit(1)

    print green("Running on %s" % env.host_string)

def depends():
    """Installs local packages"""

    with _virtualenv():

        print green("Installing python requirements...")
        for req in env.pip_requirements:
            env.run('pip install -r %s' % req)

        print green("Installing node.js requirements...")
        if env.machine_target == 'vagrant' or os.name == 'nt':
            env.run('npm install --no-bin-link')
        else:
            env.run('npm install')

        print green("Installing bower requirements...")
        env.run('bower install --config.interactive=false')
        env.run('bower prune --config.interactive=false')


def remote_install():
    """Checks some system requirements and checks out the project code"""

    if _is_local():
        print red("This command cannot be run locally. Use 'fab target_vagrant install', for example.")

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
                env.run('rm -rf %(target_directory)s/* %(target_directory)s/.*' % env, warn_only=True)
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
        env.run('mkdir -p %(target_directory)s' % env)

    if not skip_virtualenv:
        print green("Creating the %(app_name)s virtualenv" % env)
        env.run('mkvirtualenv -a %(target_directory)s %(app_name)s' % env)

    if files.exists(env.target_directory + '/.git'):
        print yellow("The target directory already contains a git repo. Skipping git clone.")
    else:
        print green("Cloning the repository from GitHub...")
        with hide('output'):
            env.run('git clone %(repo_url)s %(target_directory)s' % env)

    depends()

    dot_env_file = env.target_directory + '/local/.env'
    if _no_file_or_backed_up(dot_env_file):
        gen_dot_env(dot_env_file)

    print green('----------- .env file -------------')

    env.run('cat %s' % dot_env_file)

    print green('-----------------------------------')
    print
    print yellow("Things you still need to do:")
    print yellow("  - Make sure your database is ready for access")
    print yellow("  - Make sure your %s file contains the proper settings." % dot_env_file)
    print yellow("    and copy it to the project directory.")
    print yellow("  - Check your webserver configuration (use 'fab gen_nginx_conf')")
    print yellow("  - Install an upstart service (use 'fab gen_upstart_conf')")
    print yellow("  - Finish setting up the application with the 'fab %s staging'" % env.machine_target)
    print green("Initial install complete.")


def update_app():
    """Updates the code, database, and static files"""

    with _virtualenv():
        print green("Running migrations...")
        env.run('python manage.py migrate')

        print green("Gathering and preprocessing static files...")
        env.run('python manage.py collectstatic --noinput')
        env.run('python manage.py compress')


def git_pull():
    """Update the git repo"""
    with _virtualenv():
        print green("Pulling master from GitHub...")
        env.run('git pull origin master')


def staging():
    """Update the code and project requirements"""

    if not _is_local():
        gitstatus = _git_status()
        if gitstatus != "clean":
            if not console.confirm("Do you want to do remote staging anyway?", False):
                print yellow("Cancelled.")
                exit(1)

    git_pull()
    depends()
    update_app()

    print green("Staging complete! Run 'fab web_refresh' or 'web_restart' to restart the server.")

def deploy_prod():
    """Shortcut for 'target_production staging web_refresh'"""
    target_production()
    staging()
    web_refresh()

def _jinja_render_to(template, context, output):

    if not _is_local():
        print red("You can't render templates remotely due to path issues. Sorry!")
        exit(1)

    if not os.path.isabs(output):
        output = root_dir / output

    # Local rendering
    newconf = _jinja_render(template, template_dir='setup/templates', context=context)

    # Back up first
    _backup_file(output)

    with open(output, 'w') as outfile:
        outfile.write(newconf)

    print green("Created %s" % output)


def gen_nginx_conf(nginx_conf_file='local/nginx.conf'):
    """Generate a sample nginx conf file"""

    settings = _get_settings()

    from datetime import datetime
    nginx_context = {
        'app_name': env.get('app_name', 'my_special_app'),
        'generated_time': datetime.now(),
        'settings': settings,
    }

    _jinja_render_to('nginx.conf', context=nginx_context, output=nginx_conf_file)


def gen_upstart_conf(upstart_conf_file='local/upstart.conf'):
    """Generate a sample upstart conf file"""
    settings = _get_settings()

    from datetime import datetime
    upstart_context = {
        'upstart_log': '/var/log/%s.upstart.log' % env.app_name,
        'username': os.environ.get('USER'),
        'venv_dir': os.environ.get('VIRTUAL_ENV'),
        'generated_time': datetime.now(),
        'settings': settings,
    }
    _jinja_render_to('upstart.conf', context=upstart_context, output=upstart_conf_file)


def gen_dot_env(dot_env_file='local/.env'):
    """Generates a .env file"""
    import base64
    from datetime import datetime
    env_context = {
        'django_settings_module': env.get('django_settings_module', 'dsechat.settings.production'),
        'app_name': env.get('app_name', 'dsechatweb'),
        'secret_key': base64.b64encode(os.urandom(24)),
        'generated_time': datetime.now(),
    }

    _jinja_render_to('upstart.conf', context=upstart_context, output=upstart_conf_file)

    files.upload_template('dot_env.txt', dot_env_file,
                          context=env_context, use_jinja=True, template_dir='setup/templates',
                          mode=0600) # make it secret

    print green("Created a starter environment file at %s" % dot_env_file)


def gen_supervisor_conf(conf_file='local/supervisord.conf.tmp'):
    """Generates a supervisord conf file based on the django template supervisord.conf"""
    # Back up first
    _backup_file(conf_file)

    env.run('python manage.py supervisor getconfig > %s' % conf_file)
    print green("Wrote supervisor conf file to %s" % conf_file)

def _web_pid():
    """Get the pid of the web process"""
    with quiet():
        with _virtualenv():
            env.run('python manage.py supervisor getconfig > local/.tmpsupervisord.conf')
            pid = env.run('supervisorctl -c local/.tmpsupervisord.conf pid web', capture=True)
            env.run('rm local/.tmpsupervisord.conf')
            return pid

def status():
    """Get the status of supervisor processes"""
    with hide('running'):
        with _virtualenv():
            env.run('python manage.py supervisor getconfig > local/.tmpsupervisord.conf')
            env.run('supervisorctl -c local/.tmpsupervisord.conf status')
            env.run('rm local/.tmpsupervisord.conf')

def web_refresh():
    """Trigger Gunicorn's 'hot refresh' feature."""
    with _virtualenv():
        if _check_exists('gunicorn'):
            print green("Refreshing the web server...")
            pid = _web_pid()
            env.run('kill -HUP %s' % pid)
        else:
            print yellow("Gunicorn not present. Restart your web server yourself.")

def web_restart():
    """Hard restart Gunicorn"""
    env.run('python manage.py supervisor restart web')

def web_count():
    """Get the current gunicorn web worker count"""

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

    before = web_count()
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

def _target_local():
    package = _read_package()
    settings = _get_settings()

    env.app_name = package['name']
    env.repo_url = package['repository']

    env.run = local
    env.machine_target = 'local'

    if env.django_settings_module == 'dsechat.settings.production':
        env.pip_requirements = ('requirements/PRODUCTION',)
    else:
        env.pip_requirements = ('requirements/DEVELOPMENT',)

# default to local run
_target_local()
