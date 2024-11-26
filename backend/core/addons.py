from core.abstracts import Addon
from core.comps import (
    Comp_VAELoader,
    Comp_LoRALoader,
    Comp_UpscaleLatent,
    Comp_KSampler,
    Comp_HypernetLoader,
    Comp_UpscaleImageUsingModel,
    Comp_LoadAndApplyControlNet,
)
from core.abstracts import register_addon_class
from core.funcs import Func_VAEDecode, Func_SaveImage


class Addon_Vae(Addon):
    comp_list = False

    def __init__(self):
        super().__init__(addon_type='Vae', display_name='Vae', cache_out=True, valid_inputs=True)

        self.register_comp_class(Comp_VAELoader)
        self.comps.append(Comp_VAELoader())

    def run(self):
        assert len(self.comps) == 1, "Addon_Vae should only have one comp."
        return self.comps[0](vae_model=self.inputs_info[0].get('vae'))

class Addon_LoRA(Addon):
    comp_list = True

    def __init__(self):
        super().__init__(addon_type='LoRA', display_name='LoRA', cache_out=True, valid_inputs=True)

        self.register_comp_class(Comp_LoRALoader)

    def run(self, model, clip):
        for comp, _inputs in zip(self.comps, self.inputs_info):
            model, clip = comp(
                model=model,
                clip=clip,
                lora=_inputs.get('lora'),
                weight=_inputs.get('weight')
            )
        return model, clip

class Addon_Hypernet(Addon):
    comp_list = True

    def __init__(self):
        super().__init__(addon_type='Hypernet', display_name='Hypernet', cache_out=True, valid_inputs=True)

        self.register_comp_class(Comp_HypernetLoader)

    def run(self, model):
        for comp, _inputs in zip(self.comps, self.inputs_info):
            model = comp(
                model=model,
                hypernet=_inputs.get('hypernet'),
                strength=_inputs.get('strength')
            )
        return model

class Addon_Upscale(Addon):
    comp_list = False

    def __init__(self):
        super().__init__(addon_type='Upscale', display_name='Upscale', cache_out=True, valid_inputs=True)

        self.register_comp_class(Comp_UpscaleImageUsingModel)
        self.comps.append(Comp_UpscaleImageUsingModel())

    def run(self, image):
        assert len(self.comps) == 1, "Addon_Upscale should only have one comp."
        return self.comps[0](
            upscale_model=self.inputs_info[0].get('upscale_model'),
            image=image
        )

class Addon_HiresFix(Addon):
    comp_list = False
    can_turn_off = True

    def __init__(self):
        super().__init__(addon_type='HiresFix', display_name='Hires Fix', cache_out=True, valid_inputs=True)

        self.register_comp_class(Comp_UpscaleLatent)
        self.register_comp_class(Comp_KSampler)

        self.comp_upscale_latent = Comp_UpscaleLatent()
        self.comp_ksampler = Comp_KSampler(
            name="KSampler",
            display_name='KSampler',
            seed=1001,
            steps=14,
            cfg_scale=8.0,
            denoise=0.5,
            sampler_name='dpmpp_2m',
            scheduler_name='simple',
            cache_out=True,
            valid_inputs=True
        )

        self.func_vae_decoder = Func_VAEDecode()
        self.func_save_image = Func_SaveImage()

    def run(self, samples, model, positive, negative, vae, callback, card_info, inputs_info, addon_inputs_info, meta_info):

        input_info = self.inputs_info[0]
        assert input_info, "input info required."

        latent = self.comp_upscale_latent(
            samples=samples,
            upscale_method=input_info.get('upscale_method'),
            width=input_info.get('width'),
            height=input_info.get('height'),
            crop=input_info.get('crop')
        )

        latent = self.comp_ksampler(
            model=model,
            positive=positive,
            negative=negative,
            latent_image=latent,
            seed=input_info.get('seed'),
            steps=input_info.get('steps'),
            cfg_scale=input_info.get('cfg_scale'),
            sampler_name=input_info.get('sampler_name'),
            scheduler_name=input_info.get('scheduler_name'),
            denoise=input_info.get('denoise'),
            callback=callback
        )

        images = self.func_vae_decoder(
            vae=vae,
            samples=latent
        )

        result = self.func_save_image(
            images=images,
            card_info=card_info,
            inputs_info=inputs_info,
            addon_inputs_info=addon_inputs_info,
            meta_info=meta_info

        )
        return result

    @property
    def local_widgets_info(self):
        comp_upscale_latent = Comp_UpscaleLatent()
        comp_ksampler = Comp_KSampler(
            name="KSampler",
            display_name='KSampler',
            seed=1001,
            steps=14,
            cfg_scale=8.0,
            denoise=0.5,
            sampler_name='dpmpp_2m',
            scheduler_name='simple',
            cache_out=True,
            valid_inputs=True
        )

        result_dict = {
                **comp_upscale_latent.widgets_dict,
                **comp_ksampler.widgets_dict
            }
        return [v for v in result_dict.values()]

    @property
    def addon_info(self):
        result = super().addon_info
        widgets_info = {
            **self.comp_upscale_latent.widgets_dict,
            **self.comp_ksampler.widgets_dict
        }
        return {
            **result,
            'widgets_info': widgets_info
        }


class Addon_ControlNet(Addon):
    comp_list = True

    def __init__(self):
        super().__init__(addon_type='Controlnet', display_name='ControlNet', cache_out=True, valid_inputs=True)

        self.register_comp_class(Comp_LoadAndApplyControlNet)

    def run(self, conditioning):
        for comp, _inputs in zip(self.comps, self.inputs_info):
            conditioning = comp(
                conditioning=conditioning,
                image_path=_inputs.get('image_path'),
                controlnet=_inputs.get('controlnet'),
                strength=_inputs.get('strength')
            )
        return conditioning

register_addon_class('Vae', Addon_Vae)
register_addon_class('LoRA', Addon_LoRA)
register_addon_class('Hypernet', Addon_Hypernet)
register_addon_class('HiresFix', Addon_HiresFix)
register_addon_class('Upscale', Addon_Upscale)
register_addon_class('Controlnet', Addon_ControlNet)


