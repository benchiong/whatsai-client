from core.abstracts.card import Card
from core.comps import (
    Comp_CLIPTextEncode,
    Comp_SaveAnimatedWEBP,
    Comp_UNETLoader,
    Comp_VAELoader,
    Comp_DualCLIPLoader,
    Comp_ModelSamplingSD3,
    Comp_EmptyHunyuanLatentVideo,
    Comp_RandomNoise,
    Comp_KSamplerSelect,
    Comp_BasicScheduler,
    Comp_FluxGuidance,
    Comp_VAEDecodeTiled,
)
from core.funcs import Func_BasicGuider, Func_SamplerCustomAdvanced


class HunyuanT2VCard(Card):
    name = 'HunyuanT2v'
    meta_data = {
        'name': name,
        'display_name': "Hunyuan T2V",
        'describe': "Hunyuan Text to Video",

        "pre_models": [
            {

            }
        ],

        "cover_image": "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/54b13142-5d2c-4188-89ee-8cce17ea7553/width=500,quality=90.jpeg"
    }

    def __init__(self):
        super().__init__()

        load_diffusion_model = Comp_UNETLoader(
            name='unet_loader',
            default_unet_id='hunyuan_video_t2v_720p_bf16.safetensors',
        )
        model = self.register_func(load_diffusion_model)

        dual_clip_loader = Comp_DualCLIPLoader(
            default_clip_id1='clip_l.safetensors',
            default_clip_id2='llava_llama3_fp16.safetensors',
            default_model_type='hunyuan_video'
        )
        clip = self.register_func(dual_clip_loader)

        vae_loader = Comp_VAELoader(default_vae_id='hunyuan_video_vae_bf16.safetensors')
        vae = self.register_func(vae_loader)

        model_sampling = Comp_ModelSamplingSD3(name='model_sampling')
        self.link(model, model_sampling.inputs.model)
        patched_model = self.register_func(model_sampling)

        positive_prompt = Comp_CLIPTextEncode(
            name='positive_prompt',
            default_value="anime style anime girl with massive fennec ears and one big fluffy tail, she has blonde hair long hair blue eyes wearing a pink sweater and a long blue skirt walking in a beautiful outdoor scenery with snow mountains in the background"
        )
        positive_prompt.change_param_name_and_display_name('text', 'positive_prompt', 'Prompt')
        self.link(clip, positive_prompt.inputs.clip)
        positive_cond = self.register_func(positive_prompt)

        guidance = Comp_FluxGuidance(name='guidance', guidance=6.0)
        self.link(positive_cond, guidance.inputs.conditioning)
        positive_cond = self.register_func(guidance)

        basic_guider = Func_BasicGuider('basic_guider')
        self.link(patched_model, basic_guider.inputs.model)
        self.link(positive_cond, basic_guider.inputs.conditioning)
        guider = self.register_func(basic_guider)

        empty_hunyuan_latent_video = Comp_EmptyHunyuanLatentVideo(name='empty_hunyuan_latent_video')
        latent = self.register_func(empty_hunyuan_latent_video)

        random_noise = Comp_RandomNoise(name='random_noise', noise_seed=1)
        noise = self.register_func(random_noise)

        sampler_select = Comp_KSamplerSelect(name='sampler_select')
        sampler = self.register_func(sampler_select)

        basic_scheduler = Comp_BasicScheduler(name='basic_scheduler')
        self.link(model, basic_scheduler.inputs.model)
        sigmas = self.register_func(basic_scheduler)

        sampler_custom_advanced = Func_SamplerCustomAdvanced(name='sampler_custom_advanced', preview_steps=1)
        self.link(noise, sampler_custom_advanced.inputs.noise)
        self.link(guider, sampler_custom_advanced.inputs.guider)
        self.link(sampler, sampler_custom_advanced.inputs.sampler)
        self.link(sigmas, sampler_custom_advanced.inputs.sigmas)
        self.link(latent, sampler_custom_advanced.inputs.latent_image)
        latent, _ = self.register_func(sampler_custom_advanced)

        vae_decode = Comp_VAEDecodeTiled('vae_decoder')
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
