from typing import Callable

import torch

from core.abstracts import Card
from core.comps import (
    Comp_CheckpointLoader,
    Comp_CLIPTextEncode,
    Comp_LoadImageAndPadForOutpainting,
    Comp_CLIPSetLastLayer,
    Comp_KSampler
)
from core.funcs import Func_VAEDecode, Func_SaveImage


class SDOutpaintingCard(Card):
    name = "Stable-Diffusion-Outpainting"
    display_name = "Stable Diffusion Outpainting"

    meta_data = {
        'name': name,
        'describe': "Outpainting with Stable diffusion.",
        # https://civitai.com/models/117263/sd15-inpainting
        "pre_models": ["C6BBC15E3224E6973459BA78DE4998B80B50112B0AE5B5C67113D56B4E366B19"],
        "cover_image": "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/31d00daf-9575-4195-bdb0-69130abe6f7b/width=450/20257461.jpeg"
    }

    def __init__(self, cache_out=True, valid_inputs=False):
        super().__init__(cache_out=cache_out, valid_inputs=valid_inputs)

        self.load_checkpoint = Comp_CheckpointLoader(
            name='checkpoint',
            default_model_name='sd-v1-5-inpainting.ckpt',
            valid_inputs=valid_inputs
        )
        self.register_comp(self.load_checkpoint)

        self.positive_prompt = Comp_CLIPTextEncode(
            name='positive_prompt',
            display_name='Prompt',
            default_value='outdoors in the yosemite national park mountains nature',
            valid_inputs=valid_inputs
        )
        self.positive_prompt.map_param_name('text', 'positive_prompt')
        self.register_comp(self.positive_prompt)

        self.negative_prompt = Comp_CLIPTextEncode(
            name='negative_prompt',
            display_name='Negative Prompt',
            default_value='watermark, text',
            valid_inputs=valid_inputs
        )
        self.negative_prompt.map_param_name('text', 'negative_prompt')
        self.register_comp(self.negative_prompt)

        self.latent_from_outpainting = Comp_LoadImageAndPadForOutpainting()
        self.register_comp(self.latent_from_outpainting)

        self.clip_skip = Comp_CLIPSetLastLayer()
        self.register_comp(self.clip_skip)

        self.k_sampler = Comp_KSampler(
            seed=152545289528694,
            steps=20,
            cfg_scale=8.0,
            sampler_name="dpmpp_2m",
            scheduler_name="normal",
            denoise=1.0
        )
        self.register_comp(self.k_sampler)

        self.vae_decode = Func_VAEDecode()
        self.save_image = Func_SaveImage()

        self.support_addon_types = ['Vae', 'LoRA', 'Hypernet', 'HiresFix', 'Upscale', 'Controlnet']
        self.init_supported_addons(['Vae', 'LoRA', 'Hypernet', 'HiresFix', 'Upscale', 'Controlnet'])

    def run(self,
            base_inputs: dict,
            addon_inputs: dict,
            valid_func_inputs: bool = False,
            progress_callback: Callable = None
            ):
        addon_vae = self.addons.get('Vae')
        addon_lora = self.addons.get('LoRA')
        addon_hypernet = self.addons.get('Hypernet')
        addon_hires_fix = self.addons.get('Hires Fix')
        addon_Upscale = self.addons.get('Upscale')
        addon_ControlNet = self.addons.get('ControlNet')

        with torch.inference_mode():
            checkpoint_info = base_inputs.get('checkpoint')
            model, clip, vae = self.load_checkpoint(
                checkpoint_hash=checkpoint_info.get('sha_256')
            )
            if addon_vae and addon_inputs.get('Vae'):
                vae = addon_vae()

            if addon_hypernet and addon_inputs.get('Hypernet'):
                model = addon_hypernet(model)

            if addon_lora and addon_inputs.get('LoRA'):
                model, clip = addon_lora(model, clip)

            clip = self.clip_skip(clip=clip, clip_skip=base_inputs.get('clip_skip'))

            positive_cond = self.positive_prompt(clip=clip, text=base_inputs.get('positive_prompt'))
            if addon_ControlNet:
                positive_cond = addon_ControlNet(positive_cond)

            negative_cond = self.negative_prompt(clip=clip, text=base_inputs.get('negative_prompt'))

            latent_image = self.latent_from_outpainting(
                vae=vae,
                image_to_outpainting=base_inputs.get("image_to_outpainting"),
                left_padding=base_inputs.get('left_padding'),
                top_padding=base_inputs.get('top_padding'),
                right_padding=base_inputs.get('right_padding'),
                bottom_padding=base_inputs.get('bottom_padding'),
                feathering=base_inputs.get('feathering'),
                grow_mask_by=base_inputs.get('grow_mask_by')
            )

            sd_progress_callback = self.get_progress_callback('sd_progress_callback')
            latent_image = self.k_sampler(
                model=model,
                latent_image=latent_image,
                positive=positive_cond,
                negative=negative_cond,
                seed=base_inputs.get('seed'),
                steps=base_inputs.get('steps'),
                cfg_scale=base_inputs.get('cfg_scale'),
                denoise=base_inputs.get('denoise'),
                sampler_name=base_inputs.get('sampler_name'),
                scheduler_name=base_inputs.get('scheduler_name'),
                callback=sd_progress_callback
            )

            pixel_samples = self.vae_decode(vae=vae, samples=latent_image)

            if addon_Upscale and addon_inputs.get('Upscale'):
                pixel_samples = addon_Upscale(
                    image=pixel_samples
                )

            result = self.save_image(
                images=pixel_samples,
                card_info=self.card_inputs_info,
                inputs_info=base_inputs,
                addon_inputs_info=addon_inputs
            )

            if addon_hires_fix and addon_inputs.get('Hires Fix'):
                sd_hires_fix_callback = self.get_progress_callback('sd_hires_fix_callback')
                meta_info = {
                    'width': addon_inputs.get('Hires Fix')[0].get('width'),
                    'height': addon_inputs.get('Hires Fix')[0].get('height')
                }
                hires_fix_result = addon_hires_fix(
                    samples=latent_image,
                    model=model,
                    vae=vae,
                    positive=positive_cond,
                    negative=negative_cond,
                    callback=sd_hires_fix_callback,
                    card_info=self.card_inputs_info,
                    inputs_info=base_inputs,
                    addon_inputs_info=addon_inputs,
                    meta_info=meta_info
                )
                return {
                    'result': result,
                    'hires_fix_result': hires_fix_result
                }

            return {
                'result': result
            }