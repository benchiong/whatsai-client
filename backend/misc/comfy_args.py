from comfy.cli_args import args as comfy_args
import platform

# set them manually to solve black image problem
# https://www.reddit.com/r/comfyui/comments/1cx123b/comfyui_generating_black_images/
comfy_args.force_upcast_attention = False

if platform.system() == "Darwin":
    comfy_args.use_split_cross_attention = False
else:
    comfy_args.use_split_cross_attention = True
    
# comfy_args.lowvram = True
