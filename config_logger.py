CONFIG_LOGGER = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'default': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        }
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'formatter': 'default',
            'class': 'logging.StreamHandler'
        }
    },
    'loggers': {
        '': {
            'formatter': 'default',
            'handlers': ['default'],
            'level': 'DEBUG',
            'propagate': True
        },
        '__main__': {
            'formatter': 'default',
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': False
        },
        'handlers': {
            'formatter': 'default',
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': False
        },
        'functions': {
            'formatter': 'default',
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': False
        }
    }
}
