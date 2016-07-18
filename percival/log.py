#import logging.config

percival_log_config = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(name)26s [%(filename)18s:%(lineno)4d]  %(levelname)7s -  %(message)s'
        },
        'simple': {
            'format': '%(levelname)6s - %(message)s'
        },
    },
    'handlers': {
        'console':{
                   
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'percival': {
            'handlers':['console'],
            'propagate': False,
            'level':'DEBUG',
        },
        'percival.carrier': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'percival.carrier.buffer': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'percival.carrier.buffer.BufferCommand': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'percival.carrier.channels': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'percival.carrier.channels.ControlChannel': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'percival.carrier.channels.MonitoringChannel': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'percival.carrier.devices': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'percival.carrier.encoding': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'percival.carrier.txrx': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'percival.carrier.txrx.TxRx': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'percival.control': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'percival.detector': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'percival.detector.ipc_reactor.IpcReactor': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'BoardSettings': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'percival.configuration.ChannelParameters': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    }
}


#logging.config.dictConfig(percival_log_config)

import logging
import logging.config
logging.config.dictConfig(percival_log_config)
log = logging.getLogger("percival")


def logger(name):
    return logging.getLogger(name)
