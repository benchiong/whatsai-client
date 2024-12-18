from core.abstracts.card import Card
from core.comps import (
    Comp_CheckpointLoader,
    Comp_CLIPTextEncode,
    Comp_EmptyLatentImage,
    Comp_KSamplerAdvanced,
)
from core.funcs import Func_VAEDecode, Func_SaveImage


class SDXLCard(Card):
    name = "SDXL-With-Refiner"

    meta_data = {
        'name': name,
        'display_name': "SDXL With Refiner",
        'describe': "SDXL With Refiner",

        "pre_models": [
            {
                # SDXL 1.0 VAE fix
                # https://civitai.com/models/101055?modelVersionId=128078
                "hash": "E6BB9EA85BBF7BF6478A7C6D18B71246F22E95D41BCDD80ED40AA212C33CFEFF"
            },
            {
                # refiner
                # https://civitai.com/models/101055?modelVersionId=126613
                "hash": "7440042BBDC8A24813002C09B6B69B64DC90FDED4472613437B7F55F9B7D9C5F"
            },
        ],

        "cover_image": "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/2410801d-f9a2-46f9-b5f0-17eefe008950/width=450/SDXL1Refiner.jpeg"
    }

    def __init__(self):
        super().__init__()

        load_checkpoint = Comp_CheckpointLoader(
            name='checkpoint',
            display_name="Load SDXL Base Checkpoint",
            default_model='sd_xl_base_1.0.safetensors',
        )
        model, clip, vae = self.register_func(load_checkpoint)

        load_refiner = Comp_CheckpointLoader(
            name='refiner',
            display_name="Load SDXL Refiner Checkpoint",
            default_model='sd_xl_refiner_1.0.safetensors',
        )
        load_refiner.set_widget_param_names_prefix('refiner_')
        refiner_model, refiner_clip, refiner_vae = self.register_func(load_refiner)

        positive_prompt = Comp_CLIPTextEncode(
            name='positive_prompt',
            display_name='Prompt',
            default_value='evening sunset scenery blue sky nature, glass bottle with a galaxy in it',
        )
        positive_prompt.change_param_name_and_display_name('text', 'positive_prompt', 'Prompt')
        self.link(clip, positive_prompt.inputs.clip)
        positive_cond = self.register_func(positive_prompt)

        negative_prompt = Comp_CLIPTextEncode(
            name='negative_prompt',
            display_name='Negative Prompt',
            default_value='text, watermark',
        )
        negative_prompt.change_param_name_and_display_name('text', 'negative_prompt', 'Negative Prompt')
        self.link(clip, negative_prompt.inputs.clip)
        negative_cond = self.register_func(negative_prompt)

        empty_latent_image = Comp_EmptyLatentImage(
            name='latent image',
            width=1024,
            height=1024,
        )
        latent = self.register_func(empty_latent_image)

        k_sampler_advanced = Comp_KSamplerAdvanced(
            name="KSamplerAdvanced",
            display_name='Advanced KSampler',
            add_noise='enable',
            noise_seed=721897303308196,
            cfg_scale=8.0,
            sampler_name='euler',
            scheduler_name='normal',
            steps=25,
            start_at_step=0,
            end_at_step=20,
            return_with_leftover_noise='enable',
        )
        self.link(model, k_sampler_advanced.inputs.model)
        self.link(positive_cond, k_sampler_advanced.inputs.positive)
        self.link(negative_cond, k_sampler_advanced.inputs.negative)
        self.link(latent, k_sampler_advanced.inputs.latent_image)
        latent = self.register_func(k_sampler_advanced)

        # this will override positive_prompt, and make a final single positive_prompt
        refiner_positive_prompt = Comp_CLIPTextEncode(
            name='positive_prompt',
            display_name='Prompt',
            default_value='evening sunset scenery blue sky nature, glass bottle with a galaxy in it',
        )
        refiner_positive_prompt.change_param_name_and_display_name('text', 'positive_prompt', 'Prompt')
        self.link(refiner_clip, refiner_positive_prompt.inputs.clip)
        refiner_positive_cond = self.register_func(refiner_positive_prompt)

        # this will override negative_prompt, and make a final single negative_prompt
        refiner_negative_prompt = Comp_CLIPTextEncode(
            name='negative_prompt',
            display_name='Negative Prompt',
            default_value='text, watermark',
        )
        refiner_negative_prompt.change_param_name_and_display_name('text', 'negative_prompt', 'Negative Prompt')
        self.link(refiner_clip, refiner_negative_prompt.inputs.clip)
        refiner_negative_cond = self.register_func(refiner_negative_prompt)

        k_sampler_refiner = Comp_KSamplerAdvanced(
            name="RefinerKSamplerAdvanced",
            display_name='Refiner Advanced KSampler',
            add_noise='disable',
            noise_seed=0,
            cfg_scale=8.0,
            sampler_name='euler',
            scheduler_name='normal',
            steps=25,
            start_at_step=20,
            end_at_step=10000,
            return_with_leftover_noise='disable',
        )
        k_sampler_refiner.set_widget_param_names_prefix("refiner_")
        self.link(refiner_model, k_sampler_refiner.inputs.model)
        self.link(refiner_positive_cond, k_sampler_refiner.inputs.positive)
        self.link(refiner_negative_cond, k_sampler_refiner.inputs.negative)
        self.link(latent, k_sampler_refiner.inputs.latent_image)
        refiner_latent = self.register_func(k_sampler_refiner)

        vae_decode = Func_VAEDecode('vae decoder')
        self.link(refiner_latent, vae_decode.inputs.samples)
        self.link(refiner_vae, vae_decode.inputs.vae)
        pixel_samples = self.register_func(vae_decode)

        save_image = Func_SaveImage('save image')
        self.link(pixel_samples, save_image.inputs.images)
        _ = self.register_func(save_image)
