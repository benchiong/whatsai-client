from comfy.cli_args import args as comfy_args

# set them manually to solve black image problem
# https://www.reddit.com/r/comfyui/comments/1cx123b/comfyui_generating_black_images/
comfy_args.force_upcast_attention = False
comfy_args.use_split_cross_attention = False
comfy_args.lowvram = True
