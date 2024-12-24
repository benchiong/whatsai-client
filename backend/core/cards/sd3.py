from core.abstracts.addon import AddonOutputToReplace
from core.abstracts.card import Card
from core.addons import Addon_SD3Clip
from core.comps import (
    Comp_CheckpointLoader,
    Comp_CLIPTextEncode,
    Comp_KSampler,
    Comp_EmptyLatentImage, Comp_SD3ClipLoader,
)
from core.funcs import Func_VAEDecode, Func_SaveImage


class SD3Card(Card):
    name = 'SD3-without-clip-loader'
    meta_data = {
        'name': name,
        'display_name': "SD3(without clip loader)",
        'describe': "Very simple version of SD3.",

        "pre_models": [
            {
                # https://civitai.com/models/497255
                "hash": "CC236278D28C8C3ECCB8E21EE0A67EBED7DD6E9CE40AA9DE914FA34E8282F191"
            }
        ],

        "cover_image": "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/0a7b3477-f915-487b-934f-7d84c5ecedcc/width=450/image-90.jpeg"
    }

    def __init__(self):
        super().__init__()

        load_checkpoint = Comp_CheckpointLoader(
            name='checkpoint',
            default_model='sd3_medium_incl_clips_t5xxlfp8.safetensors',
        )
        model, clip, vae = self.register_func(load_checkpoint)

        positive_prompt = Comp_CLIPTextEncode(
            name='positive_prompt',
            default_value='a bottle with a pink and red galaxy inside it on top of a wooden table on a table in the middle of a modern kitchen',
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
            seed=125338548270506,
            steps=30,
            cfg_scale=5.5,
            sampler_name='euler',
            scheduler_name='sgm_uniform'
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

        ### Clip Addon
        addon_clip = Addon_SD3Clip()
        addon_clip.set_outputs_to_replace(
            AddonOutputToReplace(func_name='checkpoint', func_output_name='clip', addon_output_name='clip'),
        )

        self.add_supported_addon(addon_clip)

        self.set_addon_positions({
            'Clip': 'checkpoint',
        })
