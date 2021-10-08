import os



MODE = os.environ.get('APP_MODE')
DEBUG = MODE not in ['PROD', 'STAGE']

if DEBUG:
    import config.secrets_local as secrets
else:
    import config.secrets as secrets


DATABASE_URI = 'sqlite:///db/prod.db'

if DEBUG:
    DATABASE_URI = 'sqlite:///db/local.db'
