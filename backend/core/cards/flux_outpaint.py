from core.abstracts.card import Card
from core.comps import (
    Comp_CLIPTextEncode,
    Comp_UNETLoader,
    Comp_DualCLIPLoader,
    Comp_VAELoader,
    Comp_FluxGuidance,
    Comp_LoadImage,
    Comp_KSampler,
    Comp_ImagePadForOutpaint,
    Comp_InpaintModelConditioning,
)
from core.funcs import (
    Func_VAEDecode,
    Func_SaveImage,
    Func_DifferentialDiffusion,
)


class FluxOutpaintCard(Card):
    name = 'Flux Outpaint'
    meta_data = {
        'name': name,
        'display_name': "Flux Outpaint",
        'describe': "Flux Outpaint",

        "pre_models": [
            {
                # https://civitai.com/models/970162/flux-tools-fill
                'hash': '03E289F530DF51D014F48E675A9FFA2141BC003259BF5F25D75B957E920A41CA'
            }
        ],

        "cover_image": "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/92c51e53-c272-4b81-b407-2c183ce14496/original=true,quality=90/41583441.jpeg"
    }

    def __init__(self):
        super().__init__()

        load_checkpoint = Comp_UNETLoader(
            name='unet_loader',
            default_unet_id='flux1-fill-dev.safetensors',
        )
        model = self.register_func(load_checkpoint)

        dual_clip_loader = Comp_DualCLIPLoader(
            default_clip_id1='clip_l.safetensors',
            default_clip_id2='t5xxl_fp16.safetensors',
            default_model_type='flux'
        )
        clip = self.register_func(dual_clip_loader)

        vae_loader = Comp_VAELoader(default_vae_id='ae.safetensors')
        vae = self.register_func(vae_loader)

        positive_prompt = Comp_CLIPTextEncode(
            name='positive_prompt',
            default_value='beautiful scenery'
        )
        positive_prompt.change_param_name_and_display_name('text', 'positive_prompt', 'Prompt')
        self.link(clip, positive_prompt.inputs.clip)
        positive_cond = self.register_func(positive_prompt)

        guidance = Comp_FluxGuidance(name='guidance', guidance=30)
        self.link(positive_cond, guidance.inputs.conditioning)
        positive_cond = self.register_func(guidance)

        negative_prompt = Comp_CLIPTextEncode(
            name='negative_prompt',
            default_value='',
        )
        negative_prompt.change_param_name_and_display_name('text', 'negative_prompt', 'Negative Prompt')
        self.link(clip, negative_prompt.inputs.clip)
        negative_prompt.set_visible(False)
        negative_cond = self.register_func(negative_prompt)

        load_image = Comp_LoadImage(name='load_image')
        image, _ = self.register_func(load_image)

        image_pad_for_outpaint = Comp_ImagePadForOutpaint(
            name='image_pad_for_outpaint',
            left=400,
            top=0,
            right=400,
            bottom=400,
            feathering=24
        )
        self.link(image, image_pad_for_outpaint.inputs.image)
        image, mask = self.register_func(image_pad_for_outpaint)

        inpaint_model_cond = Comp_InpaintModelConditioning(name='inpaint_model_conditioning')
        self.link(positive_cond, inpaint_model_cond.inputs.positive)
        self.link(negative_cond, inpaint_model_cond.inputs.negative)
        self.link(vae, inpaint_model_cond.inputs.vae)
        self.link(image, inpaint_model_cond.inputs.pixels)
        self.link(mask, inpaint_model_cond.inputs.mask)
        positive, negative, latent = self.register_func(inpaint_model_cond)

        differential_diffusion = Func_DifferentialDiffusion(name='differential_diffusion')
        self.link(model, differential_diffusion.inputs.model)
        model = self.register_func(differential_diffusion)

        k_sampler = Comp_KSampler(
            name='ksampler',
            seed=164211176398261,
            steps=20,
            cfg_scale=1.0,
            denoise=1.0,
            sampler_name='euler',
            scheduler_name='normal',
            preview_steps=1
        )
        self.link(model, k_sampler.inputs.model)
        self.link(positive, k_sampler.inputs.positive)
        self.link(negative, k_sampler.inputs.negative)
        self.link(latent, k_sampler.inputs.latent_image)
        latent = self.register_func(k_sampler)

        vae_decode = Func_VAEDecode('vae decoder')
        self.link(latent, vae_decode.inputs.samples)
        self.link(vae, vae_decode.inputs.vae)
        pixel_samples = self.register_func(vae_decode)

        save_image = Func_SaveImage('save image')
        self.link(pixel_samples, save_image.inputs.images)
        _ = self.register_func(save_image)
