import logging.config


logging_config = {
    'version': 1,
    'loggers': {
        'service': {
            'handlers': ['console', 'file'],
            'propagate': False,
            'level': 'DEBUG',
        }
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'formatter': 'verbose',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 30 * 1024 * 1024,
            'backupCount': 5,
            'filename': 'logs/log.log'
        },
        'console': {
            'level': 'DEBUG',
            'formatter': 'verbose',
            'class': 'logging.StreamHandler'
        }
    },
    'formatters': {
        'verbose': {
            'format': '%(asctime)s - %(name)s: %(message)s'
        },
        'simple': {
            'format': '%(message)s'
        }
    }
}
