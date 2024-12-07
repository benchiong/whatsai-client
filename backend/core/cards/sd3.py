from typing import Callable

import torch

from core.abstracts import Card
from core.comps import Comp_CheckpointLoader, Comp_CLIPTextEncode, Comp_EmptyLatentImage, Comp_KSampler
from core.funcs import Func_VAEDecode, Func_SaveImage


class SD3Card(Card):

    meta_data = {
        'name': 'SD3',
        'describe': "SD3",
        'display_name': "SD3",

        "pre_models": [
            {
                # https://civitai.com/models/497255
                "hash": "CC236278D28C8C3ECCB8E21EE0A67EBED7DD6E9CE40AA9DE914FA34E8282F191"
            }
        ],

        "cover_image": "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/0a7b3477-f915-487b-934f-7d84c5ecedcc/width=450/image-90.jpeg"
    }

    def __init__(self, cache_out=True, valid_inputs=False):
        super().__init__(cache_out=cache_out, valid_inputs=valid_inputs)

        self.load_checkpoint = Comp_CheckpointLoader(
            name='checkpoint',
            default_model_name='sd3_medium_incl_clips_t5xxlfp8.safetensors',
            valid_inputs=valid_inputs
        )
        self.register_comp(self.load_checkpoint)

        self.positive_prompt = Comp_CLIPTextEncode(
            name='positive_prompt',
            display_name='Prompt',
            default_value='a bottle with a pink and red galaxy inside it on top of a wooden table on a table in the middle of a modern kitchen',
            valid_inputs=valid_inputs
        )
        self.positive_prompt.map_param_name('text', 'positive_prompt')
        self.register_comp(self.positive_prompt)

        self.negative_prompt = Comp_CLIPTextEncode(
            name='negative_prompt',
            display_name='Negative Prompt',
            default_value='',
            valid_inputs=valid_inputs
        )
        self.negative_prompt.map_param_name('text', 'negative_prompt')
        self.register_comp(self.negative_prompt)

        self.empty_latent_image = Comp_EmptyLatentImage(
            width=1024,
            height=1024
        )
        self.empty_latent_image.set_optional(True)
        self.register_comp(self.empty_latent_image)

        self.k_sampler = Comp_KSampler(
            seed=125338548270506,
            steps=30,
            cfg_scale=5.5,
            sampler_name='euler',
            scheduler_name='sgm_uniform'
        )
        self.register_comp(self.k_sampler)

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
            model, clip, vae = self.load_checkpoint(
                checkpoint_hash=checkpoint_info.get('sha_256')
            )

            positive_cond = self.positive_prompt(clip=clip, text=base_inputs.get('positive_prompt'))
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

            result = self.save_image(
                images=pixel_samples,
                card_name=self.card_inputs_info.get('card_name'),
                inputs_info=base_inputs,
                addon_inputs_info=addon_inputs
            )

            return {
                'result': result
            }
