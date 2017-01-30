#import logging.config

percival_log_config = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(name)48s [%(filename)22s:%(lineno)4d]  %(levelname)7s -  %(message)s'
        },
        'simple': {
            'format': '%(levelname)6s - %(message)s'
        },
    },
    'handlers': {
        'console':{
                   
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'percival': {
            'handlers': ['console'],
            'propagate': False,
            'level': 'DEBUG',
        },
        'percival.carrier': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'percival.carrier.simulator': {
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
        'percival.detector.standalone.PercivalStandalone': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'percival.detector.detector.PercivalParameters': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'percival.detector.detector.PercivalDetector': {
            'handlers': ['console'],
            'level': 'DEBUG',
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
        }
    }
}


# logging.config.dictConfig(percival_log_config)

import logging
import logging.config
logging.config.dictConfig(percival_log_config)
log = logging.getLogger("percival")


def logger(name):
    return logging.getLogger(name)


def get_exclusive_file_logger(filename):
    """Return a percival logger with a file handler

    Creates a file handler and removes the existing console handler from the standard percival logger instance. This can
    be used in console-gui applications where writing log messages to stdout/stderr would corrupt the display.

        :param filename: Name of file to write log messages to
        :type filename:  str
        :returns: A logger object with an attached file handler
        :rtype logging.logger:
    """
    ch = logging.FileHandler(str(filename), )
    ch.setLevel(log.getEffectiveLevel())
    fmt = logging.Formatter(percival_log_config['formatters']['verbose']['format'])
    ch.setFormatter(fmt)
    log.addHandler(ch)

    # Remove console handlers
    console_handlers = [hndlr for hndlr in log.handlers if hndlr.name == 'console']
    for hndlr in console_handlers:
        log.removeHandler(hndlr)
    return log
