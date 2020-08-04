import logging
import binascii
from contextlib import contextmanager
from threading import BoundedSemaphore

events = {
    'client': {
        'lock': BoundedSemaphore(),
        'queue': []
    },
    'server': {
        'lock': BoundedSemaphore(),
        'queue': []
    }
}


def log(*data, raw=False):
    prefixes = ' '.join((i for i in data if isinstance(i, str)))

    if raw:
        logging.info(prefixes + ' ' + str(b' '.join(i for i in data if not isinstance(i, str)))[2:-1])
    else:
        logging.info(prefixes + ' ' + (b' '.join(binascii.hexlify(i) for i in data if not isinstance(i, str))).decode())


@contextmanager
def event_lock(target, pop=False):
    events[target]['lock'].acquire()

    try:
        if pop:
            event = events[target]['queue'].pop(0)
        else:
            event = None

        yield event

    except IndexError:
        yield

    finally:
        events[target]['lock'].release()


def on_client_packet(data):
    with event_lock('client', pop=True) as event:
        if callable(event):
            event(data)

def on_server_packet(data):
    with event_lock('server', pop=True) as event:
        if callable(event):
            event(data)


def add(handler, *, target):
    with event_lock(target):
        events[target]['queue'].append(handler)
