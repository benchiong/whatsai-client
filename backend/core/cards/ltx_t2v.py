from core.abstracts.card import Card
from core.comps import (
    Comp_CheckpointLoader,
    Comp_CLIPTextEncode,
    Comp_ClipLoader,
    Comp_LTXVConditioning,
    Comp_EmptyLTXVLatentVideo,
    Comp_LTXVScheduler,
    Comp_SamplerCustom,
    Comp_KSamplerSelect,
    Comp_SaveAnimatedWEBP,
)
from core.funcs import Func_VAEDecode


class LightricksT2VCard(Card):
    name = 'LightricksT2V'
    meta_data = {
        'name': name,
        'display_name': "Lightricks T2V",
        'describe': "Lightricks Text to Video",

        "pre_models": [
            {

            }
        ],

        "cover_image": "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/a19a462a-147d-41bb-a0ac-de9fc6fb8b5b/original=true,quality=90/LTXVideo_ComfyUI_22-12-2024_130707_00001.jpeg"
    }

    def __init__(self):
        super().__init__()

        load_checkpoint = Comp_CheckpointLoader(
            name='checkpoint',
            default_model='ltx-video-2b-v0.9.safetensors',
        )
        model, _, vae = self.register_func(load_checkpoint)

        clip_loader = Comp_ClipLoader(
            name='Clip',
            display_name='Clip',
            default_clip_id='t5xxl_fp16.safetensors',
            default_model_type='ltxv'
        )
        clip = self.register_func(clip_loader)

        positive_prompt = Comp_CLIPTextEncode(
            name='positive_prompt',
            default_value="A woman with long brown hair and light skin smiles at another woman with long blonde hair. The woman with brown hair wears a black jacket and has a small, barely noticeable mole on her right cheek. The camera angle is a close-up, focused on the woman with brown hair's face. The lighting is warm and natural, likely from the setting sun, casting a soft glow on the scene. The scene appears to be real-life footage.")
        positive_prompt.change_param_name_and_display_name('text', 'positive_prompt', 'Prompt')
        self.link(clip, positive_prompt.inputs.clip)
        positive_cond = self.register_func(positive_prompt)

        negative_prompt = Comp_CLIPTextEncode(
            name='negative_prompt',
            default_value='low quality, worst quality, deformed, distorted, disfigured, motion smear, motion artifacts, fused fingers, bad anatomy, weird hand, ugly',
        )
        negative_prompt.change_param_name_and_display_name('text', 'negative_prompt', 'Negative Prompt')
        self.link(clip, negative_prompt.inputs.clip)
        negative_cond = self.register_func(negative_prompt)

        ltxv_cond = Comp_LTXVConditioning(name='ltxv_cond')
        self.link(positive_cond, ltxv_cond.inputs.positive)
        self.link(negative_cond, ltxv_cond.inputs.negative)
        positive, negative = self.register_func(ltxv_cond)

        empty_ltxv_latent_video = Comp_EmptyLTXVLatentVideo(
            name='empty_ltxv_latent_video',
            width=384,
            height=256,
        )
        latent = self.register_func(empty_ltxv_latent_video)

        sampler_select = Comp_KSamplerSelect(name='sampler_select')
        sampler = self.register_func(sampler_select)

        ltxv_scheduler = Comp_LTXVScheduler(name='ltxv_scheduler')
        self.link(latent, ltxv_scheduler.inputs.latent)
        sigmas = self.register_func(ltxv_scheduler)

        sampler_custom = Comp_SamplerCustom(name='sampler_custom')
        self.link(model, sampler_custom.inputs.model)
        self.link(positive, sampler_custom.inputs.positive)
        self.link(negative, sampler_custom.inputs.negative)
        self.link(sampler, sampler_custom.inputs.sampler)
        self.link(sigmas, sampler_custom.inputs.sigmas)
        self.link(latent, sampler_custom.inputs.latent_image)
        output, _ = self.register_func(sampler_custom)

        vae_decode = Func_VAEDecode('vae_decoder')
        self.link(output, vae_decode.inputs.samples)
        self.link(vae, vae_decode.inputs.vae)
        pixel_samples = self.register_func(vae_decode)

        save_animated_webp = Comp_SaveAnimatedWEBP('save_animated_webp')
        self.link(pixel_samples, save_animated_webp.inputs.images)
        _ = self.register_func(save_animated_webp)
