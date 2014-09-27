from django.conf import settings

OPENFIRE_SETTINGS = getattr(settings, 'OPENFIRE_SETTINGS', {
    'USER_SERVICE': 'plugins/userService/userservice',
    'SECRET': 'bigsecret',
    'DEFAULT_GROUPS': ()
})

USER_SERVICE = OPENFIRE_SETTINGS.get('USER_SERVICE', 'plugins/userService/userservice')
SECRET = OPENFIRE_SETTINGS.get('SECRET', 'bigsecret')
DEFAULT_GROUPS = OPENFIRE_SETTINGS.get('DEFAULT_GROUPS', ())
