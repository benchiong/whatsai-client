
supported_pt_extensions: set[str] = {'.ckpt', '.pt', '.bin', '.pth', '.safetensors', '.pkl', '.sft'}
""" Model file extension whatsai supported, same as ComfyUI. """

comfyui_model_dirs_map = {
    'checkpoint': 'models/checkpoints',
    'clip': 'models/clip',
    'clip_vision': 'models/clip_vision',
    'controlnet': 'models/controlnet',
    'embedding': 'models/embeddings',
    'gligen': 'models/gligen',
    'hypernet': 'models/hypernetworks',
    'upscaler': 'models/upscale_models',
    'lora': 'models/loras',
    'vae': 'models/vae',
    'vae-approx': 'models/vae_approx',
}

webui_model_dirs_map = {
    'checkpoint': 'models/Stable-diffusion',
    'clip': 'models/clip',
    'clip_vision': 'models/clip_vision',
    'controlnet': 'models/ControlNet',
    'embedding': 'embeddings',
    'upscaler': ['models/upscale_models', 'models/ESRGAN', 'models/RealESRGAN', 'models/SwinIR'],
    'hypernet': 'models/hypernetworks',
    'lora': 'models/Lora',
    'vae': 'models/VAE',
    'vae-approx': 'models/VAE-approx',
    'gligen': 'models/gligen'
}



