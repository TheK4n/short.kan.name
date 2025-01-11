import logging
import logging.config
import re
from environs import Env
from marshmallow.validate import OneOf


env = Env()
env.read_env()


API_HOST = env.str("API_HOST", default="0.0.0.0")
API_PORT = env.int("API_PORT", default=8080)

REDIS_HOST = env.str("REDIS_HOST", default="127.0.0.1")
REDIS_PORT = env.int("REDIS_PORT", default=6379)

MIN_URL_TTL_SECONDS = env.int("MIN_URL_TTL_SECONDS", default=60 * 60 * 24)
MAX_URL_TTL_SECONDS = env.int("MAX_URL_TTL_SECONDS", default=60 * 60 * 24 * 3)
MIN_URL_ALIAS_LEN = env.int("MIN_URL_ALIAS_LEN", default=7)
MAX_URL_ALIAS_LEN = env.int("MAX_URL_ALIAS_LEN", default=7*2)


class SensitiveDataFilter(logging.Filter):
    pattern = re.compile(r'https?://\S+')

    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = self.mask_sensitive_data(record.msg)
        return True

    def mask_sensitive_data(self, message: str) -> str:
        message = self.pattern.sub("[REDACTED]", message)
        return message


class DebugFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno == logging.DEBUG


LOG_LEVEL = env.str(
    "LOG_LEVEL",
    validate=OneOf(
        [
            "DEBUG",
            "INFO",
            "WARNING",
            "ERROR",
            "CRITICAL",
        ],
        error="LOG_LEVEL must be one of {choices}"
    ),
    default="INFO"
)

logger_config = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '{asctime} {levelname} {name} {message}',
            "datefmt": "%Y-%m-%dT%H:%M:%S",
            'style': '{'
        },
        'debug': {
            'format': '{asctime} {levelname} {name} {module}:{funcName}:{lineno} {message}',
            "datefmt": "%Y-%m-%dT%H:%M:%S",
            'style': '{'
        }

    },
    'handlers': {
        'default': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'default',
            'filters': ['sensitive_data_filter']
        },
        'debug': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'debug',
            'filters': ['debug']
        }
    },
    'loggers': {
        'api_logger': {
            'level': LOG_LEVEL,
            'handlers': ['default', 'debug'],
            'propagate': False
        }
    },
    'filters': {
        'debug': {
            '()': DebugFilter
        },
        'sensitive_data_filter': {
            '()': SensitiveDataFilter
        }
    }
}
logging.config.dictConfig(logger_config)
