from typing import Callable

import torch

from core.abstracts import Card
from core.comps import (
    Comp_CheckpointLoader,
    Comp_CLIPTextEncode,
    Comp_KSampler,
    Comp_EmptyLatentImage,
    Comp_CLIPSetLastLayer,
)
from core.funcs import Func_VAEDecode, Func_SaveImage
from misc.logger import logger


class SDT2ICard(Card):
    name = "Stable-Diffusion-Text-to-Image"
    display_name = "Stable Diffusion Text-to-Image"

    meta_data = {
        'name': name,
        'describe': "Text-to-Image with Stable diffusion.",
        # https://civitai.com/models/62437
        "pre_models": ["6ce0161689b3853acaa03779ec93eafe75a02f4ced659bee03f50797806fa2fa"],
        "cover_image": "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/0efc4253-57cc-444d-a501-2bfd0cf86697/width=450/00000-2585056719.jpeg"
    }

    def __init__(self, cache_out=True, valid_inputs=False):
        super().__init__(cache_out=cache_out, valid_inputs=valid_inputs)

        self.load_checkpoint = Comp_CheckpointLoader(
            name='checkpoint',
            default_model_name='v1-5-pruned-emaonly.safetensors',
            valid_inputs=valid_inputs
        )
        self.register_comp(self.load_checkpoint)

        self.positive_prompt = Comp_CLIPTextEncode(
            name='positive_prompt',
            display_name='Prompt',
            default_value='beautiful scenery nature glass bottle landscape, , purple galaxy bottle,',
            valid_inputs=valid_inputs
        )
        self.positive_prompt.map_param_name('text', 'positive_prompt')
        self.register_comp(self.positive_prompt)

        self.negative_prompt = Comp_CLIPTextEncode(
            name='negative_prompt',
            display_name='Negative Prompt',
            default_value='text, watermark',
            valid_inputs=valid_inputs
        )
        self.negative_prompt.map_param_name('text', 'negative_prompt')
        self.register_comp(self.negative_prompt)

        self.empty_latent_image = Comp_EmptyLatentImage()
        self.empty_latent_image.set_optional(True)
        self.register_comp(self.empty_latent_image)

        self.clip_skip = Comp_CLIPSetLastLayer(
            valid_inputs=valid_inputs
        )
        self.register_comp(self.clip_skip)

        self.k_sampler = Comp_KSampler()
        self.register_comp(self.k_sampler)

        self.vae_decode = Func_VAEDecode(valid_inputs=valid_inputs)
        self.save_image = Func_SaveImage(valid_inputs=valid_inputs)

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

            logger.debug('checkpoint_info: {}'.format(checkpoint_info))

            model, clip, vae = self.load_checkpoint(
                checkpoint_hash=checkpoint_info.get('sha_256')
            )

            logger.debug('model: {} clip {}, vae:'.format(model, clip, vae))

            if addon_vae and addon_inputs.get('Vae'):
                vae = addon_vae()

            if addon_hypernet and addon_inputs.get('Hypernet'):
                model = addon_hypernet(model)

            if addon_lora and addon_inputs.get('LoRA'):
                model, clip = addon_lora(model, clip)

            clip = self.clip_skip(clip=clip, clip_skip=base_inputs.get('clip_skip'))

            positive_cond = self.positive_prompt(clip=clip, text=base_inputs.get('positive_prompt'))
            if addon_ControlNet and addon_inputs.get('ControlNet'):
                positive_cond = addon_ControlNet(positive_cond)

            negative_cond = self.negative_prompt(clip=clip, text=base_inputs.get('negative_prompt'))

            latent_image = self.empty_latent_image(
                width=base_inputs.get('width'),
                height=base_inputs.get('height'),
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
