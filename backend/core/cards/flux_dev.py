from core.abstracts.addon import AddonOutputToReplace
from core.abstracts.card import Card
from core.addons import Addon_SD3Clip
from core.comps import (
    Comp_CheckpointLoader,
    Comp_CLIPTextEncode,
    Comp_KSampler,
    Comp_EmptyLatentImage, Comp_SD3ClipLoader, Comp_FluxGuidance,
)
from core.funcs import Func_VAEDecode, Func_SaveImage


class FluxDevCard(Card):
    name = 'Flux Dev'
    meta_data = {
        'name': name,
        'display_name': "Flux Dev",
        'describe': "Simple version of Flux Dev",

        "pre_models": [
            {
                # https://civitai.com/models/1032613/flux1-dev-scaled-fp8
                'hash': '358FFF9355C962532593898B10436F13E6F9BFB0389F36DF03C6E55FE7C9CBFE'
            }
        ],

        "cover_image": "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/d8fc82a0-0429-4dd7-b0f2-34cdb095b831/original=true,quality=90/2024-12-12-204709_00001_.jpeg"
    }

    def __init__(self):
        super().__init__()

        load_checkpoint = Comp_CheckpointLoader(
            name='checkpoint',
            default_model='flux_dev.safetensors',
            # default_model='flux1DevScaledFp8_v2.safetensors',
        )
        model, clip, vae = self.register_func(load_checkpoint)

        positive_prompt = Comp_CLIPTextEncode(
            name='positive_prompt',
            default_value='cute anime girl with massive fluffy fennec ears and a big fluffy tail blonde messy long hair blue eyes wearing a maid outfit with a long black gold leaf pattern dress and a white apron mouth open placing a fancy black forest cake with candles on top of a dinner table of an old dark Victorian mansion lit by candlelight with a bright window to the foggy forest and very expensive stuff everywhere there are paintings on the walls',
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
        negative_prompt.set_visible(False)
        negative_cond = self.register_func(negative_prompt)

        guidance = Comp_FluxGuidance('guidance')
        self.link(positive_cond, guidance.inputs.conditioning)
        guidance_cond = self.register_func(guidance)

        empty_latent_image = Comp_EmptyLatentImage(name='latent image', width=1024, height=1024)
        latent = self.register_func(empty_latent_image)

        k_sampler = Comp_KSampler(
            seed=972054013131368,
            steps=20,
            cfg_scale=1.0,
            sampler_name='euler',
            scheduler_name='simple',
            denoise=1.0
        )
        k_sampler.set_widgets_visibility(['cfg', 'denoise'], False)
        self.link(model, k_sampler.inputs.model)
        self.link(guidance_cond, k_sampler.inputs.positive)
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
