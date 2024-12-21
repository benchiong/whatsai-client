from core.abstracts.addon import AddonOutputToReplace, AddonInputToLink
from core.addons import Addon_Vae, Addon_LoRA, Addon_Hypernet, Addon_ControlNet, Addon_Upscale
from core.abstracts.card import Card
from core.comps import (
    Comp_CheckpointLoader,
    Comp_CLIPTextEncode,
    Comp_KSampler,
    Comp_CLIPSetLastLayer,
    Comp_LoadImageAndPadForOutpainting,
)
from core.funcs import Func_VAEDecode, Func_SaveImage


class SDOutpaintingCard(Card):
    name = "Stable-Diffusion-Outpainting"
    meta_data = {
        'name': name,
        'display_name': "Stable Diffusion Outpainting",
        'describe': "Outpainting with Stable diffusion.",

        "pre_models": [
            {
                # https://civitai.com/models/117263/sd15-inpainting
                "hash": "C6BBC15E3224E6973459BA78DE4998B80B50112B0AE5B5C67113D56B4E366B19"
            }
        ],

        "cover_image": "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/31d00daf-9575-4195-bdb0-69130abe6f7b/width=450/20257461.jpeg"
    }

    def __init__(self):
        super().__init__()

        load_checkpoint = Comp_CheckpointLoader(
            name='checkpoint',
            default_model='v1-5-pruned-emaonly.safetensors'
        )
        model, clip, vae = self.register_func(load_checkpoint)

        clip_skip = Comp_CLIPSetLastLayer(name='clip_skip')
        self.link(clip, clip_skip.inputs.clip)
        clip = self.register_func(clip_skip)

        positive_prompt = Comp_CLIPTextEncode(
            name='positive_prompt',
            default_value='outdoors in the yosemite national park mountains nature',
        )
        positive_prompt.change_param_name_and_display_name('text', 'positive_prompt', 'Prompt')
        self.link(clip, positive_prompt.inputs.clip)
        positive_cond = self.register_func(positive_prompt)

        negative_prompt = Comp_CLIPTextEncode(
            name='negative_prompt',
            default_value='text, watermark',
        )
        negative_prompt.change_param_name_and_display_name('text', 'negative_prompt', 'Negative Prompt')
        self.link(clip, negative_prompt.inputs.clip)
        negative_cond = self.register_func(negative_prompt)

        latent_from_outpainting = Comp_LoadImageAndPadForOutpainting(name='latent')
        self.link(vae, latent_from_outpainting.inputs.vae)
        latent = self.register_func(latent_from_outpainting)

        k_sampler = Comp_KSampler(name='ksampler')
        self.link(model, k_sampler.inputs.model)
        self.link(positive_cond, k_sampler.inputs.positive)
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

        ###  LoRA
        lora_addon = Addon_LoRA()
        lora_addon.set_outputs_to_replace(
            AddonOutputToReplace(func_name='checkpoint', func_output_name='model', addon_output_name='model'),
            AddonOutputToReplace(func_name='checkpoint', func_output_name='clip', addon_output_name='clip'),
        )
        lora_addon.set_inputs_to_link(
            AddonInputToLink(addon_input_name='model', func_name='checkpoint', func_output_name='model'),
            AddonInputToLink(addon_input_name='clip', func_name='checkpoint', func_output_name='clip'),
        )
        self.add_supported_addon(lora_addon)

        ###  Hypernet
        hypernet_addon = Addon_Hypernet()
        hypernet_addon.set_outputs_to_replace(
            AddonOutputToReplace(func_name='checkpoint', func_output_name='model', addon_output_name='model'),
        )
        hypernet_addon.set_inputs_to_link(
            AddonInputToLink(addon_input_name='model', func_name='checkpoint', func_output_name='model'),
        )
        self.add_supported_addon(hypernet_addon)

        ###  Vae
        vae_addon = Addon_Vae()
        vae_addon.set_outputs_to_replace(
            AddonOutputToReplace(func_name='checkpoint', func_output_name='vae', addon_output_name='vae'),
        )
        self.add_supported_addon(vae_addon)

        ###  ControlNet
        controlnet_addon = Addon_ControlNet()
        controlnet_addon.set_outputs_to_replace(
            AddonOutputToReplace(func_name='positive_prompt', func_output_name='cond', addon_output_name='cond'),
        )
        controlnet_addon.set_inputs_to_link(
            AddonInputToLink(addon_input_name='conditioning', func_name='positive_prompt', func_output_name='cond'),
        )
        self.add_supported_addon(controlnet_addon)

        ### Upscale
        upscale_addon = Addon_Upscale()
        upscale_addon.set_outputs_to_replace(
            AddonOutputToReplace(func_name='vae decoder', func_output_name='image', addon_output_name='image'),
        )
        upscale_addon.set_inputs_to_link(
            AddonInputToLink(addon_input_name='image', func_name='vae decoder', func_output_name='image'),
        )
        self.add_supported_addon(upscale_addon)

        self.set_addon_positions({
            'Vae': 'checkpoint',
            'LoRA': 'checkpoint',
            'Hypernet': 'checkpoint',
            'Controlnet': 'positive_prompt',
            'Upscale': 'vae decoder',
        })
