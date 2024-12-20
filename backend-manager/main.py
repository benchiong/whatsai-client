import argparse

import uvicorn
from server import app


parser = argparse.ArgumentParser(add_help=False)
parser.add_argument("--prod", action='store_true')
parser.add_argument("--port", type=int, default=8820)
parser.add_argument("--host", type=str, default='127.0.0.1')

args, _ = parser.parse_known_args()

port = args.port
is_prod = args.prod
host = args.host


if __name__ == '__main__':
    if is_prod:
        uvicorn.run(app, host=host, port=port)
    else:
        uvicorn.run("server:app", host=host, port=port, reload=True)

