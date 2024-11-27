import argparse

from comfy.cli_args import args as comfy_args

# set them manually to solve black image problem
# https://www.reddit.com/r/comfyui/comments/1cx123b/comfyui_generating_black_images/
comfy_args.force_upcast_attention = True
comfy_args.use_split_cross_attention = True
comfy_args.lowvram = True

parser = argparse.ArgumentParser()

parser.add_argument("--env", type=str, default='dev')
parser.add_argument("--host", type=str, default="127.0.0.1")
parser.add_argument("--port", type=int, default=8172)

args = parser.parse_args()

