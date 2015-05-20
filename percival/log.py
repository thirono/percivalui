#import logging.config

percival_log_config = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(name)40s  [%(filename)16s:%(lineno)d]  %(levelname)6s -  %(message)s'
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
            'level': 'DEBUG',
            'propagate': False,
        },
        'percival.detector': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        }
    }
}


#logging.config.dictConfig(percival_log_config)

import logging
import logging.config
log = logging.getLogger("percival")
logging.config.dictConfig(percival_log_config)

