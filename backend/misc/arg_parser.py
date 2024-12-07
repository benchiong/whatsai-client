import argparse

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument("--prod", action='store_true')
parser.add_argument("--port", type=int, default=8172)
parser.add_argument("--host", type=str, default='127.0.0.1')

args = parser.parse_args()

port = args.port
is_prod = args.prod
host = args.host

log_sink_to_file = True if is_prod else False
""" loguru sink config, setting True will save logs into file. """

