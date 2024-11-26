from core.abstracts import Comp
from core.funcs import (
    Func_CheckpointLoaderSimple,
    Func_CLIPTextEncode,
    Func_KSampler,
    Func_EmptyLatentImage,
    Func_CLIPSetLastLayer,
    Func_LoraLoader,
    Func_UpscaleModelLoader,
    Func_ImageUpscaleWithModel,
    Func_ImageScale,
    Func_VAELoader,
    Func_VAEEncode,
    Func_LoadImage,
    Func_LatentScale,
    Func_HypernetLoader,
    Func_VAEEncodeForInpainting,
    Func_ControlNetLoader,
    Func_ControlNetApply,
    Func_ImagePadForOutpainting,
    Func_KSamplerAdvanced
)
from core.widgets import ModelComboWidget, TextWidget, SeedWidget, IntWidget, FloatWidget, ComboWidget, ImageWidget

import comfy
from tiny_db.model_info import ModelInfoTable


class Comp_CheckpointLoader(Comp):
    def __init__(self, name='Checkpoint', default_model_name=None, display_name='Checkpoint', cache_out=True, valid_inputs=True):
        super().__init__(name=name, display_name=display_name, cache_out=cache_out, valid_inputs=valid_inputs)

        self.load_checkpoint = Func_CheckpointLoaderSimple(cache_out=cache_out, valid_inputs=valid_inputs)
        self.register_func(self.load_checkpoint)

        default_model = ModelInfoTable.sync_get_model_info_by_file_name(default_model_name)

        self.widget_model_list = ModelComboWidget(
            display_name=display_name,
            param_name='checkpoint',
            values_function_name='list_checkpoints',
            default_value=default_model
        )
        self.register_widget(self.widget_model_list)

    def run(self, checkpoint_hash):
        model, clip, vae = self.load_checkpoint(checkpoint_hash)
        return model, clip, vae

class Comp_VAELoader(Comp):
    def __init__(self,
                 name="Vae Loader",
                 default_model_name=None,
                 display_name='Vae',
                 cache_out=True,
                 valid_inputs=True,
                 ):
        super().__init__(name=name, display_name=display_name, cache_out=cache_out, valid_inputs=valid_inputs)

        self.func_model_loader = Func_VAELoader(valid_inputs=valid_inputs)
        self.register_func(self.func_model_loader)

        default_model = ModelInfoTable.sync_get_model_info_by_file_name(default_model_name) if default_model_name else None

        self.widget_model_loader = ModelComboWidget(
            display_name=display_name,
            param_name='vae',
            values_function_name='list_vaes',
            values_function_params=None,
            default_value=default_model
        )
        self.register_widget(self.widget_model_loader)

    def run(self, vae_model):
        return self.func_model_loader(vae_model)

class Comp_CLIPTextEncode(Comp):
    def __init__(self, name='prompt', display_name='Text', default_value='', cache_out=True, valid_inputs=True):
        super().__init__(name=name, display_name=display_name, cache_out=cache_out, valid_inputs=valid_inputs)

        self.encode_text = Func_CLIPTextEncode(cache_out=cache_out, valid_inputs=valid_inputs)
        self.register_func(self.encode_text)

        self.widget_text = TextWidget(
            display_name=display_name,
            param_name='text',
            default_value=default_value
        )
        self.register_widget(self.widget_text)

    def run(self, clip, text):
        conditioning = self.encode_text(clip, text)
        return conditioning

class Comp_EmptyLatentImage(Comp):
    def __init__(self,
                 name='latent image',
                 display_name='Empty Latent Image',
                 width=512,
                 height=512,
                 batch_size=1,
                 cache_out=True,
                 valid_inputs=True,
                 ):
        super().__init__(name=name, display_name=display_name, cache_out=cache_out, valid_inputs=valid_inputs)

        self.latent_image = Func_EmptyLatentImage(cache_out=cache_out, valid_inputs=valid_inputs)
        self.register_func(self.latent_image)

        self.widget_width = IntWidget(
            display_name='Width',
            param_name='width',
            default_value=width,
            min=128,
            max=5120,
            step=64
        )
        self.register_widget(self.widget_width)

        self.widget_height = IntWidget(
            display_name='Height',
            param_name='height',
            default_value=height,
            min=128,
            max=5120,
            step=64
        )
        self.register_widget(self.widget_height)

        # only one batch supported yet.
        # self.width_batch_size = IntWidget(
        #     display_name='Batch Size',
        #     param_name='batch_size',
        #     default_value=batch_size,
        #     min=1,
        #     max=64,
        #     step=1
        # )
        # self.register_widget(self.width_batch_size)

    def run(self, width, height, batch_size=1):
        latent_image = self.latent_image(width=width, height=height, batch_size=batch_size)
        return latent_image

class Comp_KSampler(Comp):
    def __init__(self,
                 name="KSampler",
                 display_name='KSampler',
                 seed=1001,
                 steps=20,
                 cfg_scale=8.0,
                 denoise=1.0,
                 sampler_name='euler',
                 scheduler_name='normal',
                 cache_out=True,
                 valid_inputs=True
                 ):
        super().__init__(name=name, display_name=display_name, cache_out=cache_out, valid_inputs=valid_inputs)

        self.k_sampler = Func_KSampler(cache_out=cache_out, valid_inputs=valid_inputs)
        self.register_func(self.k_sampler)

        self.widget_seed = SeedWidget(
            display_name='Seed',
            param_name='seed',
            default_value=seed
        )
        self.register_widget(self.widget_seed)

        self.widget_steps = IntWidget(
            display_name='Steps',
            param_name='steps',
            default_value=steps,
            min=1,
            max=1000,
            step=1
        )
        self.register_widget(self.widget_steps)

        self.widget_cfg = FloatWidget(
            display_name='CFG Scale',
            param_name='cfg_scale',
            default_value=cfg_scale,
            min=0.0,
            max=100.0,
            step=0.1,
            round=2
        )
        self.register_widget(self.widget_cfg)

        self.widget_sampler_name = ComboWidget(
            display_name='Sampler',
            param_name='sampler_name',
            default_value=sampler_name,
            values=comfy.samplers.KSampler.SAMPLERS
        )
        self.register_widget(self.widget_sampler_name)

        self.widget_scheduler_name = ComboWidget(
            display_name='Scheduler',
            param_name='scheduler_name',
            default_value=scheduler_name,
            values=comfy.samplers.KSampler.SCHEDULERS
        )
        self.register_widget(self.widget_scheduler_name)

        self.widget_denoise = FloatWidget(
            display_name='Denoise',
            param_name='denoise',
            default_value=denoise,
            min=0.0,
            max=1.0,
            step=0.05,
            round=2
        )
        self.register_widget(self.widget_denoise)

    def run(self, model, positive, negative, latent_image, seed, steps, cfg_scale, sampler_name, scheduler_name, denoise, callback):
        latent = self.k_sampler(
            model=model,
            positive=positive,
            negative=negative,
            latent_image=latent_image,
            seed=seed,
            steps=steps,
            cfg=cfg_scale,
            sampler_name=sampler_name,
            scheduler=scheduler_name,
            denoise=denoise,
            callback=callback
        )
        return latent


class Comp_KSamplerAdvanced(Comp):
    def __init__(self,
                 name="KSamplerAdvanced",
                 display_name='Advanced KSampler',
                 add_noise='disable',
                 noise_seed=0,
                 cfg_scale=8.0,
                 sampler_name='euler',
                 scheduler_name='normal',
                 steps=20,
                 start_at_step=0,
                 end_at_step=10000,
                 return_with_leftover_noise='disable',
                 cache_out=True,
                 valid_inputs=True
                 ):
        super().__init__(name=name, display_name=display_name, cache_out=cache_out, valid_inputs=valid_inputs)

        self.k_sampler_advanced = Func_KSamplerAdvanced(cache_out=cache_out, valid_inputs=valid_inputs)
        self.register_func(self.k_sampler_advanced)

        self.widget_add_noise = ComboWidget(
            display_name='Add noise',
            param_name='add_noise',
            values=["enable", "disable"],
            default_value=add_noise
        )
        self.register_widget(self.widget_add_noise)

        self.widget_noise_seed = SeedWidget(
            display_name='Seed',
            param_name='noise_seed',
            default_value=noise_seed
        )
        self.register_widget(self.widget_noise_seed)

        self.widget_steps = IntWidget(
            display_name='Steps',
            param_name='steps',
            default_value=steps,
            min=1,
            max=10000,
            step=1
        )
        self.register_widget(self.widget_steps)

        self.widget_start_at_step = IntWidget(
            display_name='Start At Step',
            param_name='start_at_step',
            default_value=start_at_step,
            min=0,
            max=10000,
            step=1
        )
        self.register_widget(self.widget_start_at_step)

        self.widget_end_at_steps = IntWidget(
            display_name='End At Step',
            param_name='end_at_step',
            default_value=end_at_step,
            min=0,
            max=10000,
            step=1
        )
        self.register_widget(self.widget_end_at_steps)

        self.widget_cfg = FloatWidget(
            display_name='CFG Scale',
            param_name='cfg_scale',
            default_value=cfg_scale,
            min=0.0,
            max=100.0,
            step=0.1,
            round=2
        )
        self.register_widget(self.widget_cfg)

        self.widget_sampler_name = ComboWidget(
            display_name='Sampler',
            param_name='sampler_name',
            default_value=sampler_name,
            values=comfy.samplers.KSampler.SAMPLERS
        )
        self.register_widget(self.widget_sampler_name)

        self.widget_scheduler_name = ComboWidget(
            display_name='Scheduler',
            param_name='scheduler_name',
            default_value=scheduler_name,
            values=comfy.samplers.KSampler.SCHEDULERS
        )
        self.register_widget(self.widget_scheduler_name)

        self.widget_return_with_leftover_noise = ComboWidget(
            display_name='Return with Leftover Noise',
            param_name='return_with_leftover_noise',
            values=["enable", "disable"],
            default_value=return_with_leftover_noise
        )
        self.register_widget(self.widget_return_with_leftover_noise)

    def run(self, model, add_noise, noise_seed, steps, cfg_scale, sampler_name, scheduler, positive, negative,
            latent_image, start_at_step, end_at_step, return_with_leftover_noise, denoise=1.0, callback=None):
        latent = self.k_sampler_advanced(
            model=model,
            add_noise=add_noise,
            noise_seed=noise_seed,
            steps=steps,
            cfg=cfg_scale,
            sampler_name=sampler_name,
            scheduler=scheduler,
            positive=positive,
            negative=negative,
            latent_image=latent_image,
            start_at_step=start_at_step,
            end_at_step=end_at_step,
            return_with_leftover_noise=return_with_leftover_noise,
            denoise=denoise,
            callback=callback
        )
        return latent



class Comp_CLIPSetLastLayer(Comp):
    def __init__(self,
                 name="Clip Skip",
                 display_name='Clip Skip',
                 cache_out=True,
                 valid_inputs=True
                 ):
        super().__init__(name=name, display_name=display_name, cache_out=cache_out, valid_inputs=valid_inputs)

        self.clip_skip = Func_CLIPSetLastLayer(cache_out=cache_out, valid_inputs=valid_inputs)

        self.widget_clip_skip = IntWidget(
            display_name='Clip Skip',
            param_name='clip_skip',
            default_value=-1,
            max=-1,
            min=-24,
            step=1
        )
        self.register_widget(self.widget_clip_skip)

    def run(self, clip, clip_skip):
        if clip_skip >= -1:
            return clip

        clip = self.clip_skip(clip=clip, stop_at_clip_layer=clip_skip)
        return clip

class Comp_LoRALoader(Comp):
    def __init__(self,
                 name="LoRA",
                 display_name='LoRA',
                 cache_out=True,
                 valid_inputs=True
                 ):
        super().__init__(name=name, display_name=display_name, cache_out=cache_out, valid_inputs=valid_inputs)

        self.lora_loader = Func_LoraLoader(cache_out=cache_out, valid_inputs=valid_inputs)
        self.register_func(self.lora_loader)

        self.widget_lora_list = ModelComboWidget(
            display_name=display_name,
            param_name='lora',
            values_function_name='list_loras',
            default_value=None,
        )
        self.widget_lora_list.set_optional(True)
        self.register_widget(self.widget_lora_list)

        self.widget_weight = FloatWidget(
            display_name='Weight',
            param_name='weight',
            default_value=1.0,
            min=0.0,
            max=100.0,
            step=0.1,
            round=2,
        )
        self.register_widget(self.widget_weight)

    def run(self, model, clip, lora, weight):
        lora_hash = lora.get('sha_256')
        assert lora_hash, "LoRA hash must not be empty."
        model_lora, clip_lora = self.lora_loader(
            model=model,
            clip=clip,
            lora_hash=lora_hash,
            strength_model=weight,
            strength_clip=weight
        )
        return model_lora, clip_lora

class Comp_HypernetLoader(Comp):
    def __init__(self,
                 name="Hypernet",
                 display_name='Hypernet',
                 cache_out=True,
                 valid_inputs=True
                 ):
        super().__init__(name=name, display_name=display_name, cache_out=cache_out, valid_inputs=valid_inputs)

        self.hypernet_loader = Func_HypernetLoader(cache_out=cache_out, valid_inputs=valid_inputs)
        self.register_func(self.hypernet_loader)

        self.widget_hypernet_list = ModelComboWidget(
            display_name=display_name,
            param_name='hypernet',
            values_function_name='list_hypernets',
            default_value=None
        )
        self.widget_hypernet_list.set_optional(True)
        self.register_widget(self.widget_hypernet_list)

        self.widget_strength = FloatWidget(
            display_name='Strength',
            param_name='strength',
            default_value=1.0,
            min=0.0,
            max=100.0,
            step=0.1,
            round=2,
        )
        self.register_widget(self.widget_strength)

    def run(self, model, hypernet, strength):
        hypernet_hash = hypernet.get('sha_256')
        assert hypernet_hash, "Hypernet hash must not be empty."
        model_hypernet = self.hypernet_loader(
            model=model,
            hypernet_hash=hypernet_hash,
            strength=strength,
        )
        return model_hypernet

class Comp_UpscalerLoader(Comp):
    def __init__(self,
                 name="Upscaler",
                 display_name='Upscaler',
                 cache_out=True,
                 valid_inputs=True
                 ):
        super().__init__(name=name, display_name=display_name, cache_out=cache_out, valid_inputs=valid_inputs)

        self.widget_select_image = ImageWidget(
            param_name='image_path'
        )
        self.register_widget(self.widget_select_image)

        self.widget_select_upscale_model = ModelComboWidget(
            display_name=display_name,
            param_name='model_name',
            values_function_name='list_vaes',
            default_value=None
        )
        self.widget_select_upscale_model.set_optional(True)
        self.register_widget(self.widget_select_upscale_model)

        self.load_upscale_model = Func_UpscaleModelLoader(cache_out=cache_out, valid_inputs=valid_inputs)
        self.register_func(self.load_upscale_model)

        self.image_upscale_with_model = Func_ImageUpscaleWithModel(cache_out=cache_out, valid_inputs=valid_inputs)
        self.register_func(self.load_upscale_model)

    def run(self, model, image_path):
        model_hash = model.get('sha_256')
        assert model_hash, "Model hash must not be empty."
        upscale_model = self.load_upscale_model(model_hash)
        image = self.image_upscale_with_model(upscale_model, image_path)
        return image


class Comp_UpscaleImage(Comp):
    def __init__(self,
                 name="Upscale Image",
                 display_name='Upscale Image',
                 cache_out=True,
                 valid_inputs=True,
                 width=1024,
                 height=1024,
                 ):
        super().__init__(name=name, display_name=display_name, cache_out=cache_out, valid_inputs=valid_inputs)

        self.widget_upscale_methods = ComboWidget(
            display_name="Upscale Method",
            param_name="upscale_method",
            values=["nearest-exact", "bilinear", "area", "bicubic", "lanczos"],
            value_type=str,
            default_value="bilinear"
        )
        self.register_widget(self.widget_upscale_methods)

        self.widget_width = IntWidget(
            display_name='Width',
            param_name='width',
            default_value=width,
            min=512,
            max=5120,
            step=64
        )
        self.register_widget(self.widget_width)

        self.widget_height = IntWidget(
            display_name='Height',
            param_name='height',
            default_value=height,
            min=512,
            max=5120,
            step=64
        )
        self.register_widget(self.widget_height)

        self.widget_crop = ComboWidget(
            display_name="Crop",
            param_name="crop",
            values=["disabled", "center"],
            value_type=str,
            default_value="disabled"
        )
        self.register_widget(self.widget_crop)

        self.func_upscale = Func_ImageScale()

    def run(self, image, upscale_method, width, height, crop):
        return self.func_upscale(image, upscale_method, width, height, crop)

class Comp_UpscaleImageUsingModel(Comp):
    def __init__(self,
                 name="Upscale Image Using Model",
                 display_name='Upscale Image',
                 cache_out=True,
                 valid_inputs=True,
                 ):
        super().__init__(name=name, display_name=display_name, cache_out=cache_out, valid_inputs=valid_inputs)

        self.widget_load_upscale_model = ModelComboWidget(
            display_name=display_name,
            param_name='upscale_model',
            values_function_name='list_upscalers',
            default_value=None
        )
        self.widget_load_upscale_model.set_optional(True)
        self.register_widget(self.widget_load_upscale_model)

        self.func_load_upscale_model = Func_UpscaleModelLoader(valid_inputs=valid_inputs)
        self.register_func(self.func_load_upscale_model)

        self.func_upscale_image_using_model = Func_ImageUpscaleWithModel(valid_inputs=valid_inputs)
        self.register_func(self.func_upscale_image_using_model)

    def run(self, upscale_model, image):
        upscale_model_hash = upscale_model.get('sha_256')
        assert upscale_model_hash, "Model hash must not be empty."

        upscale_model = self.func_load_upscale_model(upscale_model_hash)
        return self.func_upscale_image_using_model(upscale_model, image)

class Comp_UpscaleLatent(Comp):
    def __init__(self,
                 name="Upscale Latent",
                 display_name='Upscale Latent',
                 cache_out=True,
                 valid_inputs=True,
                 width=1152,
                 height=1152,
                 ):
        super().__init__(name=name, display_name=display_name, cache_out=cache_out, valid_inputs=valid_inputs)

        self.widget_upscale_methods = ComboWidget(
            display_name="Upscale Method",
            param_name="upscale_method",
            values=["nearest-exact", "bilinear", "area", "bicubic", "lanczos"],
            value_type=str,
            default_value="nearest-exact"
        )
        self.register_widget(self.widget_upscale_methods)

        self.widget_width = IntWidget(
            display_name='Width',
            param_name='width',
            default_value=width,
            min=512,
            max=5120,
            step=64
        )
        self.register_widget(self.widget_width)

        self.widget_height = IntWidget(
            display_name='Height',
            param_name='height',
            default_value=height,
            min=512,
            max=5120,
            step=64
        )
        self.register_widget(self.widget_height)

        self.widget_crop = ComboWidget(
            display_name="Crop",
            param_name="crop",
            values=["disabled", "center"],
            value_type=str,
            default_value="disabled"
        )
        self.register_widget(self.widget_crop)

        self.func_upscale = Func_LatentScale()

    def run(self, samples, upscale_method, width, height, crop):
        return self.func_upscale(samples, upscale_method, width, height, crop)

class Comp_Image2Latent(Comp):
    def __init__(self,
                 name="Image to Latent",
                 display_name='Image to Latent',
                 cache_out=True,
                 valid_inputs=True,
                 ):
        super().__init__(name=name, display_name=display_name, cache_out=cache_out, valid_inputs=valid_inputs)

        self.widget_load_image = ImageWidget(
            param_name='image_path',
            display_name=display_name,
            default_value=None,
            value_type=str
        )
        self.register_widget(self.widget_load_image)

        self.func_vae_encode = Func_VAEEncode(
            valid_inputs=valid_inputs
        )
        self.register_func(self.func_vae_encode)

        self.func_load_image = Func_LoadImage(
            valid_inputs=valid_inputs
        )
        self.register_func(self.func_load_image)

    def run(self, image_path, vae):
        pixels, _ = self.func_load_image(image_path)
        return self.func_vae_encode(vae=vae, pixels=pixels)

class Comp_LoadImageAndMaskForInpainting(Comp):
    def __init__(self,
                 name="Load Image And Mask For Inpainting",
                 display_name='Load Mask',
                 cache_out=True,
                 valid_inputs=True,
                 ):
        super().__init__(name=name, display_name=display_name, cache_out=cache_out, valid_inputs=valid_inputs)

        self.widget_load_image = ImageWidget(
            param_name='mask_path',
            display_name=display_name,
            default_value=None,
            value_type=str
        )
        self.register_widget(self.widget_load_image)

        self.widget_grow_mask_by = IntWidget(
            display_name='Grow Mask By',
            param_name='grow_mask_by',
            default_value=6,
            min=0,
            max=64,
            step=1
        )
        self.register_widget(self.widget_grow_mask_by)

        self.func_load_image = Func_LoadImage()
        self.register_func(self.func_load_image)

        self.func_vae_encode = Func_VAEEncodeForInpainting()
        self.register_func(self.func_vae_encode)

    def run(self, mask_path, vae, grow_mask_by):
        pixels, mask = self.func_load_image(mask_path)
        return self.func_vae_encode(vae, pixels, mask, grow_mask_by=6)

class Comp_LoadImageAndPadForOutpainting(Comp):
    def __init__(self,
                 name="Load Image And Pad For Outpainting",
                 display_name='Load Image to outpaint',
                 cache_out=True,
                 valid_inputs=True,
                 ):
        super().__init__(name=name, display_name=display_name, cache_out=cache_out, valid_inputs=valid_inputs)

        self.widget_load_image = ImageWidget(
            param_name='image_to_outpainting',
            display_name=display_name,
            default_value=None,
            value_type=str
        )
        self.register_widget(self.widget_load_image)

        self.widget_pad_left = IntWidget(
            display_name='Left Padding',
            param_name='left_padding',
            default_value=0,
            min=0,
            max=10240,
            step=32
        )
        self.register_widget(self.widget_pad_left)

        self.widget_pad_top = IntWidget(
            display_name='Top Padding',
            param_name='top_padding',
            default_value=128,
            min=0,
            max=10240,
            step=32
        )
        self.register_widget(self.widget_pad_top)

        self.widget_pad_right = IntWidget(
            display_name='Right Padding',
            param_name='right_padding',
            default_value=0,
            min=0,
            max=10240,
            step=32
        )
        self.register_widget(self.widget_pad_right)

        self.widget_pad_bottom = IntWidget(
            display_name='Bottom Padding',
            param_name='bottom_padding',
            default_value=128,
            min=0,
            max=10240,
            step=32
        )
        self.register_widget(self.widget_pad_bottom)

        self.widget_feathering = IntWidget(
            display_name='Feathering',
            param_name='feathering',
            default_value=40,
            min=0,
            max=10240,
            step=1
        )
        self.register_widget(self.widget_feathering)

        self.widget_grow_mask_by = IntWidget(
            display_name='Grow Mask By',
            param_name='grow_mask_by',
            default_value=8,
            min=0,
            max=64,
            step=1
        )
        self.register_widget(self.widget_grow_mask_by)

        self.func_load_image = Func_LoadImage()
        self.register_func(self.func_load_image)

        self.func_pad_image = Func_ImagePadForOutpainting()
        self.register_func(self.func_pad_image)

        self.func_vae_encode = Func_VAEEncodeForInpainting()
        self.register_func(self.func_vae_encode)

    def run(self,
            vae,
            image_to_outpainting,
            left_padding,
            top_padding,
            right_padding,
            bottom_padding,
            feathering,
            grow_mask_by
            ):
        image, _ = self.func_load_image(image_to_outpainting)
        new_image, mask = self.func_pad_image(image, left_padding, top_padding, right_padding, bottom_padding, feathering)
        latent = self.func_vae_encode(vae, new_image, mask, grow_mask_by)
        return latent

class Comp_LoadAndApplyControlNet(Comp):
    def __init__(self,
                 name="Load And Apply ControlNet",
                 display_name='ControlNet',
                 cache_out=True,
                 valid_inputs=True,
                 ):
        super().__init__(name=name, display_name=display_name, cache_out=cache_out, valid_inputs=valid_inputs)

        self.widget_controlnet_list = ModelComboWidget(
            display_name=display_name,
            param_name='controlnet',
            values_function_name='list_controlnets',
            default_value=None
        )
        self.widget_controlnet_list.set_optional(True)
        self.register_widget(self.widget_controlnet_list)

        self.widget_strength = FloatWidget(
            display_name='Strength',
            param_name='strength',
            default_value=1.0,
            min=0.0,
            max=10.0,
            step=0.1,
            round=2,
        )
        self.register_widget(self.widget_strength)

        self.widget_select_image = ImageWidget(
            param_name='image_path'
        )
        self.register_widget(self.widget_select_image)

        self.func_load_image = Func_LoadImage()
        self.register_func(self.func_load_image)

        self.func_load_control_net = Func_ControlNetLoader()
        self.register_func(self.func_load_control_net)

        self.func_apply_controlnet = Func_ControlNetApply()
        self.register_func(self.func_apply_controlnet)

    def run(self, conditioning, image_path, controlnet, strength):
        controlnet_hash = controlnet.get('sha_256')
        controlnet_model = self.func_load_control_net(controlnet_hash)
        image, _ = self.func_load_image(image_path)
        return self.func_apply_controlnet(
            conditioning=conditioning,
            control_net=controlnet_model,
            image=image,
            strength=strength
        )

