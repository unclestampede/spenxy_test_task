import logging

from dotenv import load_dotenv
from dynaconf import LazySettings

load_dotenv('.env')
logging.info('loaded .env')
settings = LazySettings(ENVVAR_PREFIX_FOR_DYNACONF=False)
logging.info('loaded .env')
