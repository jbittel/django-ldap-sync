DEBUG = False
TEMPLATE_DEBUG = DEBUG

TIME_ZONE = 'UTC'
USE_TZ = True

SECRET_KEY = '2w#)1o5poc5+b0zj&^1-3(^dzxap6h)3z2u3t0_jmv6ns8s_kz'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'ldap_sync',
)

LDAP_SYNC_URI = 'ldap://localhost'
LDAP_SYNC_BASE_USER = 'cn=alice,ou=example,o=test'
LDAP_SYNC_BASE_PASS = 'alicepw'
LDAP_SYNC_BASE = 'o=test'

LDAP_SYNC_USER_FILTER = 'objectCategory=person'

LDAP_SYNC_USER_ATTRIBUTES = {
    'mailNickname': 'username',
    'givenName': 'first_name',
    'sn': 'last_name',
    'mail': 'email',
}
