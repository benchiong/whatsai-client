
env = 'prod'
host = '127.0.0.1'
port = 8172

log_sink_to_file = False if env == 'dev' else True
""" loguru sink config, setting True will save logs into file. """