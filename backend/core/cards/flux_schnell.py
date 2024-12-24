from core.abstracts.card import Card
from core.comps import (
    Comp_CLIPTextEncode,
    Comp_EmptyLatentImage,
    Comp_UNETLoader,
    Comp_DualCLIPLoader,
    Comp_VAELoader,
    Comp_BasicScheduler,
    Comp_KSamplerSelect,
    Comp_RandomNoise,
)
from core.funcs import Func_VAEDecode, Func_SaveImage, Func_BasicGuider, Func_SamplerCustomAdvanced


class FluxSchnellCard(Card):
    name = 'Flux Schnell'
    meta_data = {
        'name': name,
        'display_name': "Flux Schnell",
        'describe': "Simple version of Flux Schnell",

        "pre_models": [
            {
                # https://civitai.com/models/628862/flux1-schnell-merged-with-flux1-dev-bnb-nf4-fp8-4-steps
                'hash': '74E101ABACB700E4B1AC9BA229847B1BC0F5F94561E2C9B4751039FE2542C77B'
            }
        ],

        "cover_image": "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/903274ab-d9d2-4079-9751-5fa9fd68f787/original=true,quality=90/00025-2074345123.jpeg"
    }

    def __init__(self):
        super().__init__()

        load_checkpoint = Comp_UNETLoader(
            name='unet_loader',
            default_unet_id='flux1-schnell.safetensors',
        )
        model = self.register_func(load_checkpoint)

        dual_clip_loader = Comp_DualCLIPLoader(
            default_clip_id1='t5xxl_fp16.safetensors',
            default_clip_id2='clip_l.safetensors',
            default_model_type='flux'
        )
        clip = self.register_func(dual_clip_loader)

        vae_loader = Comp_VAELoader(default_vae_id='ae.safetensors')
        vae = self.register_func(vae_loader)

        empty_latent_image = Comp_EmptyLatentImage(name='latent image', width=1024, height=1024)
        latent = self.register_func(empty_latent_image)

        sampler_select = Comp_KSamplerSelect(name='sampler_select')
        sampler = self.register_func(sampler_select)

        random_noise = Comp_RandomNoise('noise', noise_seed=219670278747233)
        noise = self.register_func(random_noise)

        basic_scheduler = Comp_BasicScheduler(name='basic_scheduler')
        self.link(model, basic_scheduler.inputs.model)
        sigmas = self.register_func(basic_scheduler)

        positive_prompt = Comp_CLIPTextEncode(
            name='positive_prompt',
            default_value='a bottle with a beautiful rainbow galaxy inside it on top of a wooden table in the middle of a modern kitchen beside a plate of vegetables and mushrooms and a wine glasse that contains a planet earth with a plate with a half eaten apple pie on it'
        )
        positive_prompt.change_param_name_and_display_name('text', 'positive_prompt', 'Prompt')
        self.link(clip, positive_prompt.inputs.clip)
        positive_cond = self.register_func(positive_prompt)

        basic_guider = Func_BasicGuider('basic_guider')
        self.link(model, basic_guider.inputs.model)
        self.link(positive_cond, basic_guider.inputs.conditioning)
        guider = self.register_func(basic_guider)

        sampler_custom_advanced = Func_SamplerCustomAdvanced(name='sampler_custom_advanced', preview_steps=1)
        self.link(noise, sampler_custom_advanced.inputs.noise)
        self.link(guider, sampler_custom_advanced.inputs.guider)
        self.link(sampler, sampler_custom_advanced.inputs.sampler)
        self.link(sigmas, sampler_custom_advanced.inputs.sigmas)
        self.link(latent, sampler_custom_advanced.inputs.latent_image)
        latent, _ = self.register_func(sampler_custom_advanced)

        vae_decode = Func_VAEDecode('vae decoder')
        self.link(latent, vae_decode.inputs.samples)
        self.link(vae, vae_decode.inputs.vae)
        pixel_samples = self.register_func(vae_decode)

        save_image = Func_SaveImage('save image')
        self.link(pixel_samples, save_image.inputs.images)
        _ = self.register_func(save_image)
