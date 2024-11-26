from typing import Callable

import torch

from core.abstracts import Card
from core.comps import (
    Comp_CheckpointLoader,
    Comp_CLIPTextEncode,
    Comp_EmptyLatentImage,
    Comp_KSamplerAdvanced
)
from core.funcs import (
    Func_CLIPTextEncode,
    Func_VAEDecode,
    Func_SaveImage
)


class SDXLCard(Card):
    name = "SDXL-With-Refiner"
    display_name = "SDXL With Refiner"

    meta_data = {
        'name': name,
        'describe': "SDXL With Refiner",

        # https://civitai.com/models/101055
        # https://civitai.com/models/101055?modelVersionId=126613
        "pre_models": ["31e35c80fc4829d14f90153f4c74cd59c90b779f6afe05a74cd6120b893f7e5b"],
        "cover_image": "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/2410801d-f9a2-46f9-b5f0-17eefe008950/width=450/SDXL1Refiner.jpeg"
    }

    def __init__(self, cache_out=True, valid_inputs=False):
        super().__init__(cache_out=cache_out, valid_inputs=valid_inputs)

        self.load_checkpoint = Comp_CheckpointLoader(
            name='checkpoint',
            display_name="Load SDXL Base Checkpoint",
            default_model_name='sd_xl_base_1.0.safetensors',
            valid_inputs=valid_inputs
        )
        self.register_comp(self.load_checkpoint)

        self.load_refiner = Comp_CheckpointLoader(
            name='refiner',
            display_name="Load SDXL Refiner Checkpoint",
            default_model_name='sd_xl_refiner_1.0.safetensors',
            valid_inputs=valid_inputs
        )
        self.load_refiner.map_all_param_names_with_prefix('refiner_')
        self.register_comp(self.load_refiner)

        self.positive_prompt = Comp_CLIPTextEncode(
            name='positive_prompt',
            display_name='Prompt',
            default_value='evening sunset scenery blue sky nature, glass bottle with a galaxy in it',
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

        self.encode_refiner_positive_prompt = Func_CLIPTextEncode()
        self.encode_refiner_negative_prompt = Func_CLIPTextEncode()

        self.empty_latent_image = Comp_EmptyLatentImage(
            width=1024,
            height=1024
        )
        self.register_comp(self.empty_latent_image)

        self.k_sampler_advanced = Comp_KSamplerAdvanced(
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
        self.k_sampler_advanced.set_group_widgets(True)
        self.register_comp(self.k_sampler_advanced)

        self.k_sampler_refiner = Comp_KSamplerAdvanced(
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
        self.k_sampler_refiner.set_group_widgets(True)
        self.k_sampler_refiner.map_all_param_names_with_prefix("refiner_")
        self.register_comp(self.k_sampler_refiner)

        self.vae_decode = Func_VAEDecode(valid_inputs=valid_inputs)
        self.save_image = Func_SaveImage(valid_inputs=valid_inputs)

    def run(self,
            base_inputs: dict,
            addon_inputs: dict,
            valid_func_inputs: bool = False,
            progress_callback: Callable = None
            ):
        with torch.inference_mode():
            checkpoint_info = base_inputs.get('checkpoint')
            model, clip, _ = self.load_checkpoint(
                checkpoint_hash=checkpoint_info.get('sha_256')
            )

            refiner_checkpoint_info = base_inputs.get('refiner_checkpoint')
            refiner_model, refiner_clip, refiner_vae = self.load_checkpoint(
                checkpoint_hash=refiner_checkpoint_info.get('sha_256')
            )

            positive_prompt = base_inputs.get('positive_prompt')
            negative_prompt = base_inputs.get('negative_prompt')

            positive_cond = self.positive_prompt(clip=clip, text=positive_prompt)
            negative_cond = self.negative_prompt(clip=clip, text=negative_prompt)

            latent_image = self.empty_latent_image(
                width=base_inputs.get('width'),
                height=base_inputs.get('height'),
            )

            sd_progress_callback = self.get_progress_callback('sd_progress_callback')
            latent_image = self.k_sampler_advanced(
                model=model,
                add_noise=base_inputs.get('add_noise'),
                noise_seed=base_inputs.get('noise_seed'),
                steps=base_inputs.get('steps'),
                cfg_scale=base_inputs.get('cfg_scale'),
                sampler_name=base_inputs.get('sampler_name'),
                scheduler=base_inputs.get('scheduler'),
                positive=positive_cond,
                negative=negative_cond,
                latent_image=latent_image,
                start_at_step=base_inputs.get('start_at_step'),
                end_at_step=base_inputs.get('end_at_step'),
                return_with_leftover_noise=base_inputs.get('return_with_leftover_noise'),
                denoise=1.0,
                callback=sd_progress_callback
            )

            refiner_positive_cond = self.encode_refiner_positive_prompt(clip=refiner_clip, text=positive_prompt)
            refiner_negative_cond = self.encode_refiner_negative_prompt(clip=refiner_clip, text=negative_prompt)
            refiner_latent_image = self.k_sampler_refiner(
                model=refiner_model,
                add_noise=base_inputs.get('refiner_add_noise'),
                noise_seed=base_inputs.get('refiner_noise_seed'),
                steps=base_inputs.get('refiner_steps'),
                cfg_scale=base_inputs.get('refiner_cfg_scale'),
                sampler_name=base_inputs.get('refiner_sampler_name'),
                scheduler=base_inputs.get('refiner_scheduler'),
                positive=refiner_positive_cond,
                negative=refiner_negative_cond,
                latent_image=latent_image,
                start_at_step=base_inputs.get('refiner_start_at_step'),
                end_at_step=base_inputs.get('refiner_end_at_step'),
                return_with_leftover_noise=base_inputs.get('refiner_return_with_leftover_noise'),
                denoise=1.0,
                callback=sd_progress_callback
            )

            pixel_samples = self.vae_decode(vae=refiner_vae, samples=refiner_latent_image)

            result = self.save_image(
                images=pixel_samples,
                card_info=self.card_inputs_info,
                inputs_info=base_inputs,
                addon_inputs_info=addon_inputs
            )

            return {
                'result': result
            }

