from core.abstracts.card import Card
from core.comps import (
    Comp_CLIPTextEncode,
    Comp_ClipLoader,
    Comp_SaveAnimatedWEBP,
    Comp_UNETLoader,
    Comp_VAELoader,
    Comp_EmptyMochiLatentVideo,
    Comp_KSampler,
)
from core.funcs import Func_VAEDecode


class MochiT2VCard(Card):
    name = 'MochiT2v'
    meta_data = {
        'name': name,
        'display_name': "Mochi T2V",
        'describe': "Mochi Text to Video",

        "pre_models": [
            {

            }
        ],

        "cover_image": "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/6a26dedb-a6e1-43b3-bc7e-c940f17a4d8d/original=true,quality=90/00142-44796101.jpeg"
    }

    def __init__(self):
        super().__init__()

        load_checkpoint = Comp_UNETLoader(
            name='unet_loader',
            default_unet_id='mochi_preview_bf16.safetensors',
        )
        model = self.register_func(load_checkpoint)

        clip_loader = Comp_ClipLoader(
            name='Clip',
            display_name='Clip',
            default_clip_id='t5xxl_fp16.safetensors',
            default_model_type='mochi',
        )
        clip = self.register_func(clip_loader)

        vae_loader = Comp_VAELoader(default_vae_id='mochi_vae.safetensors')
        vae = self.register_func(vae_loader)

        positive_prompt = Comp_CLIPTextEncode(
            name='positive_prompt',
            default_value="a fox moving quickly in a beautiful winter scenery nature trees sunset tracking camera"
        )
        positive_prompt.change_param_name_and_display_name('text', 'positive_prompt', 'Prompt')
        self.link(clip, positive_prompt.inputs.clip)
        positive_cond = self.register_func(positive_prompt)

        negative_prompt = Comp_CLIPTextEncode(
            name='negative_prompt',
            default_value=''
        )
        negative_prompt.change_param_name_and_display_name('text', 'negative_prompt', 'Negative Prompt')
        self.link(clip, negative_prompt.inputs.clip)
        negative_cond = self.register_func(negative_prompt)

        empty_mochi_latent_video = Comp_EmptyMochiLatentVideo(name='empty_mochi_latent_video')
        latent = self.register_func(empty_mochi_latent_video)

        k_sampler = Comp_KSampler(name='ksampler')
        self.link(model, k_sampler.inputs.model)
        self.link(positive_cond, k_sampler.inputs.positive)
        self.link(negative_cond, k_sampler.inputs.negative)
        self.link(latent, k_sampler.inputs.latent_image)
        latent = self.register_func(k_sampler)

        vae_decode = Func_VAEDecode('vae_decoder')
        self.link(latent, vae_decode.inputs.samples)
        self.link(vae, vae_decode.inputs.vae)
        pixel_samples = self.register_func(vae_decode)

        save_animated_webp = Comp_SaveAnimatedWEBP(
            name='save_animated_webp',
            fps=24.0,
            lossless=False,
            quality=80,
            method='default',
        )
        self.link(pixel_samples, save_animated_webp.inputs.images)
        _ = self.register_func(save_animated_webp)
