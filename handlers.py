import time


def throttle_client_server(duration):
    def handler(data):
        print('Throttling network for {} seconds'.format(duration))
        time.sleep(duration)
        return data
    return handler
