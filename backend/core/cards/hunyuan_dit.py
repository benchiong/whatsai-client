from core.abstracts.card import Card
from core.comps import (
    Comp_CheckpointLoader,
    Comp_CLIPTextEncode,
    Comp_KSampler,
    Comp_EmptyLatentImage,
    Comp_CLIPSetLastLayer,
)
from core.funcs import Func_VAEDecode, Func_SaveImage


class HunyuanDitCard(Card):
    name = "HunyuanDit"
    meta_data = {
        'name': name,
        'display_name': "Hunyuan Dit Text-to-Image",
        'describe': "Hunyuan Dit Text-to-Image",
        "pre_models": [
            {

            }
        ],
        "cover_image": "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/335f763c-7ff6-4493-9e89-f1f7dc1fffb4/width=600,quality=90.jpeg"
    }

    def __init__(self):
        super().__init__()

        load_checkpoint = Comp_CheckpointLoader(
            name='checkpoint',
            default_model='hunyuan_dit_1.2.safetensors'
        )
        model, clip, vae = self.register_func(load_checkpoint)

        clip_skip = Comp_CLIPSetLastLayer(name='clip_skip')
        self.link(clip, clip_skip.inputs.clip)
        clip = self.register_func(clip_skip)

        positive_prompt = Comp_CLIPTextEncode(
            name='positive_prompt',
            default_value='a bottle with a 彩虹星系 inside it on top of a wooden table on a snowy mountain top with the ocean and clouds in the background',
        )
        positive_prompt.change_param_name_and_display_name('text', 'positive_prompt', 'Prompt')
        self.link(clip, positive_prompt.inputs.clip)
        positive_cond = self.register_func(positive_prompt)

        negative_prompt = Comp_CLIPTextEncode(
            name='negative_prompt',
            default_value='',
        )
        negative_prompt.change_param_name_and_display_name('text', 'negative_prompt', 'Negative Prompt')
        self.link(clip, negative_prompt.inputs.clip)
        negative_cond = self.register_func(negative_prompt)

        empty_latent_image = Comp_EmptyLatentImage(name='latent image', width=1024, height=1024)
        latent = self.register_func(empty_latent_image)

        k_sampler = Comp_KSampler(
            name='ksampler',
            seed=137656229034231,
            steps=30,
            cfg_scale=6.0,
            denoise=1.0,
            sampler_name='euler',
            scheduler_name='sgm_uniform',
            grouped_widgets=True,
            preview_steps=3
        )
        self.link(model, k_sampler.inputs.model)
        self.link(positive_cond, k_sampler.inputs.positive)
        self.link(negative_cond, k_sampler.inputs.negative)
        self.link(latent, k_sampler.inputs.latent_image)
        latent = self.register_func(k_sampler)

        vae_decode = Func_VAEDecode('vae decoder')
        self.link(latent, vae_decode.inputs.samples)
        self.link(vae, vae_decode.inputs.vae)
        pixel_samples = self.register_func(vae_decode)

        save_image = Func_SaveImage('save image')
        self.link(pixel_samples, save_image.inputs.images)
        _ = self.register_func(save_image)
