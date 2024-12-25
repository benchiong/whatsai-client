from core.abstracts.comp import Comp, SwitchableComp
from core.funcs import (
    Func_CheckpointLoaderSimple,
    Func_CLIPTextEncode,
    Func_KSampler,
    Func_EmptyLatentImage,
    Func_CLIPSetLastLayer,
    Func_LoraLoader,
    Func_UpscaleModelLoader,
    Func_ImageUpscaleWithModel,
    Func_VAELoader,
    Func_VAEEncode,
    Func_LoadImage,
    Func_LatentScale,
    Func_HypernetLoader,
    Func_VAEEncodeForInpaint,
    Func_ControlNetLoader,
    Func_ControlNetApply,
    Func_ImagePadForOutpaint,
    Func_KSamplerAdvanced,
    Func_ClipLoader,
    Func_DualCLIPLoader,
    Func_TripleCLIPLoader,
    Func_FluxGuidance,
    Func_UNETLoader,
    Func_BasicScheduler,
    Func_KSamplerSelect,
    Func_RandomNoise,
    Func_InpaintModelConditioning,
    Func_LTXVConditioning,
    Func_EmptyLTXVLatentVideo,
    Func_LTXVScheduler,
    Func_SamplerCustom,
    Func_SaveAnimatedWEBP, Func_LTXVImgToVideo
)
from core.widgets import ModelComboWidget, TextWidget, SeedWidget, IntWidget, FloatWidget, ComboWidget, ImageWidget, \
    BoolWidget

import comfy


class Comp_CheckpointLoader(Comp):
    def __init__(self, name='checkpoint', display_name='Checkpoint', default_model=None):
        super().__init__(name=name, display_name=display_name)

        load_checkpoint = Func_CheckpointLoaderSimple()
        self.register_func(load_checkpoint)

        widget_model_list = ModelComboWidget(
            display_name=display_name,
            param_name='checkpoint_id',
            values_function_name='list_checkpoints',
            default_value=default_model
        )
        self.register_widget(widget_model_list)


class Comp_VAELoader(Comp):
    def __init__(self,
                 name="Vae Loader",
                 display_name='Vae',
                 default_vae_id=None
                 ):
        super().__init__(name=name, display_name=display_name)

        func_model_loader = Func_VAELoader()
        self.register_func(func_model_loader)

        widget_model_loader = ModelComboWidget(
            display_name=display_name,
            param_name='vae_id',
            values_function_name='list_vaes',
            values_function_params=None,
            default_value=default_vae_id
        )
        widget_model_loader.set_optional(True)
        self.register_widget(widget_model_loader)


class Comp_CLIPTextEncode(Comp):
    def __init__(self, name='text', display_name='Text', default_value=None):
        super().__init__(name=name, display_name=display_name)

        encode_text = Func_CLIPTextEncode()
        self.register_func(encode_text)

        widget_text = TextWidget(
            display_name=display_name,
            param_name='text',
            default_value=default_value
        )
        self.register_widget(widget_text)


class Comp_EmptyLatentImage(Comp):
    def __init__(self,
                 name='latent image',
                 display_name='Image Size',
                 width=512,
                 height=512,
                 grouped_widgets=True
                 ):
        super().__init__(name=name, display_name=display_name, grouped_widgets=grouped_widgets)

        latent_image = Func_EmptyLatentImage()
        self.register_func(latent_image)

        widget_width = IntWidget(
            display_name='Width',
            param_name='width',
            default_value=width,
            min=128,
            max=5120,
            step=64
        )
        self.register_widget(widget_width)

        widget_height = IntWidget(
            display_name='Height',
            param_name='height',
            default_value=height,
            min=128,
            max=5120,
            step=64
        )
        self.register_widget(widget_height)


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
                 grouped_widgets=True,
                 preview_steps=3
                 ):
        super().__init__(name=name, display_name=display_name, grouped_widgets=grouped_widgets)

        k_sampler = Func_KSampler(preview_steps=preview_steps)
        self.register_func(k_sampler)

        widget_seed = SeedWidget(
            display_name='Seed',
            param_name='seed',
            default_value=seed
        )
        self.register_widget(widget_seed)

        widget_steps = IntWidget(
            display_name='Steps',
            param_name='steps',
            default_value=steps,
            min=1,
            max=1000,
            step=1
        )
        self.register_widget(widget_steps)

        widget_cfg = FloatWidget(
            display_name='CFG Scale',
            param_name='cfg',
            default_value=cfg_scale,
            min=0.0,
            max=100.0,
            step=0.1,
            round=2
        )
        self.register_widget(widget_cfg)

        widget_sampler_name = ComboWidget(
            display_name='Sampler',
            param_name='sampler_name',
            default_value=sampler_name,
            values=comfy.samplers.KSampler.SAMPLERS
        )
        self.register_widget(widget_sampler_name)

        widget_scheduler_name = ComboWidget(
            display_name='Scheduler',
            param_name='scheduler',
            default_value=scheduler_name,
            values=comfy.samplers.KSampler.SCHEDULERS
        )
        self.register_widget(widget_scheduler_name)

        widget_denoise = FloatWidget(
            display_name='Denoise',
            param_name='denoise',
            default_value=denoise,
            min=0.0,
            max=1.0,
            step=0.05,
            round=2
        )
        self.register_widget(widget_denoise)


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
                 preview_steps=3,
                 ):
        super().__init__(name=name, display_name=display_name, grouped_widgets=True)

        k_sampler_advanced = Func_KSamplerAdvanced(preview_steps=preview_steps)
        self.register_func(k_sampler_advanced)

        widget_add_noise = ComboWidget(
            display_name='Add noise',
            param_name='add_noise',
            values=["enable", "disable"],
            default_value=add_noise
        )
        self.register_widget(widget_add_noise)

        widget_noise_seed = SeedWidget(
            display_name='Seed',
            param_name='noise_seed',
            default_value=noise_seed
        )
        self.register_widget(widget_noise_seed)

        widget_steps = IntWidget(
            display_name='Steps',
            param_name='steps',
            default_value=steps,
            min=1,
            max=10000,
            step=1
        )
        self.register_widget(widget_steps)

        widget_start_at_step = IntWidget(
            display_name='Start At Step',
            param_name='start_at_step',
            default_value=start_at_step,
            min=0,
            max=10000,
            step=1
        )
        self.register_widget(widget_start_at_step)

        widget_end_at_steps = IntWidget(
            display_name='End At Step',
            param_name='end_at_step',
            default_value=end_at_step,
            min=0,
            max=10000,
            step=1
        )
        self.register_widget(widget_end_at_steps)

        widget_cfg = FloatWidget(
            display_name='CFG Scale',
            param_name='cfg',
            default_value=cfg_scale,
            min=0.0,
            max=100.0,
            step=0.1,
            round=2
        )
        self.register_widget(widget_cfg)

        widget_sampler_name = ComboWidget(
            display_name='Sampler',
            param_name='sampler_name',
            default_value=sampler_name,
            values=comfy.samplers.KSampler.SAMPLERS
        )
        self.register_widget(widget_sampler_name)

        widget_scheduler_name = ComboWidget(
            display_name='Scheduler',
            param_name='scheduler',
            default_value=scheduler_name,
            values=comfy.samplers.KSampler.SCHEDULERS
        )
        self.register_widget(widget_scheduler_name)

        widget_return_with_leftover_noise = ComboWidget(
            display_name='Return with Leftover Noise',
            param_name='return_with_leftover_noise',
            values=["enable", "disable"],
            default_value=return_with_leftover_noise
        )
        self.register_widget(widget_return_with_leftover_noise)


class Comp_CLIPSetLastLayer(Comp):
    def __init__(self, name="Clip Skip", display_name='Clip Skip'):
        super().__init__(name=name, display_name=display_name)

        clip_skip = Func_CLIPSetLastLayer()
        self.register_func(clip_skip)

        widget_clip_skip = IntWidget(
            display_name='Clip Skip',
            param_name='clip_skip',
            default_value=-1,
            max=-1,
            min=-24,
            step=1
        )
        self.register_widget(widget_clip_skip)


class Comp_LoRALoader(Comp):
    def __init__(self,
                 name="LoRA",
                 display_name='LoRA',
                 ):
        super().__init__(name=name, display_name=display_name, )

        self.lora_loader = Func_LoraLoader()
        self.register_func(self.lora_loader)

        self.widget_lora_list = ModelComboWidget(
            display_name=display_name,
            param_name='lora_id',
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


class Comp_HypernetLoader(Comp):
    def __init__(self,
                 name="Hypernet",
                 display_name='Hypernet',
                 ):
        super().__init__(name=name, display_name=display_name)

        hypernet_loader = Func_HypernetLoader()
        self.register_func(hypernet_loader)

        widget_hypernet_list = ModelComboWidget(
            display_name='Hypernet',
            param_name='hypernet_id',
            values_function_name='list_hypernets',
            default_value=None
        )
        widget_hypernet_list.set_optional(True)
        self.register_widget(widget_hypernet_list)

        widget_strength = FloatWidget(
            display_name='Strength',
            param_name='strength',
            default_value=1.0,
            min=0.0,
            max=100.0,
            step=0.1,
            round=2,
        )
        self.register_widget(widget_strength)


class Comp_UpscaleImageUsingModel(Comp):
    def __init__(self,
                 name="Upscale Image Using Model",
                 display_name='Upscale Image',
                 ):
        super().__init__(name=name, display_name=display_name)

        func_load_upscale_model = Func_UpscaleModelLoader()
        self.register_func(func_load_upscale_model, share_io=False)

        func_upscale_image_using_model = Func_ImageUpscaleWithModel()
        self.register_func(func_upscale_image_using_model, share_io=False)

        self.set_inputs_with_dict({
            **func_load_upscale_model.inputs,
            **func_upscale_image_using_model.inputs,
        })

        widget_load_upscale_model = ModelComboWidget(
            display_name=display_name,
            param_name='upscale_model_id',
            values_function_name='list_upscalers',
            default_value=None
        )
        widget_load_upscale_model.set_optional(True)
        self.register_widget(widget_load_upscale_model)

        self.link(func_load_upscale_model.outputs.upscale_model, func_upscale_image_using_model.inputs.upscale_model)

        self.share_outputs(func_upscale_image_using_model)


class Comp_UpscaleLatent(Comp):
    def __init__(self,
                 name="Upscale Latent",
                 display_name='Upscale Latent',
                 width=1152,
                 height=1152,
                 ):
        super().__init__(name=name, display_name=display_name)

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


class Comp_LoadImage(Comp):
    def __init__(self, name='LoadImage', display_name='Load Image'):
        super().__init__(name=name, display_name=display_name)

        func_load_image = Func_LoadImage()
        self.register_func(func_load_image)

        widget_load_image = ImageWidget(
            param_name='image_path',
            display_name=display_name,
            default_value=None,
            value_type=str
        )
        self.register_widget(widget_load_image)


class Comp_Image2Latent(Comp):
    def __init__(self,
                 name='Image to Latent',
                 display_name='Load Image For Image to Image',
                 ):
        super().__init__(name=name, display_name=display_name)

        func_load_image = Func_LoadImage()
        self.register_func(func_load_image, share_io=False)

        func_vae_encode = Func_VAEEncode()
        self.register_func(func_vae_encode, share_io=False)

        self.set_inputs_with_dict({
            **func_load_image.inputs,
            **func_vae_encode.inputs,
        })

        widget_load_image = ImageWidget(
            param_name='image_path',
            display_name=display_name,
            default_value=None,
            value_type=str
        )
        self.register_widget(widget_load_image)

        self.link(func_load_image.outputs.image, func_vae_encode.inputs.pixels)
        self.share_outputs(func_vae_encode)


class Comp_LoadImageAndMaskForInpainting(Comp):
    def __init__(self,
                 name="Load Image And Mask For Inpainting",
                 display_name='Load Mask',
                 ):
        super().__init__(name=name, display_name=display_name)

        func_load_image = Func_LoadImage()
        self.register_func(func_load_image, share_io=False)

        func_vae_encode = Func_VAEEncodeForInpaint()
        self.register_func(func_vae_encode, share_io=False)

        self.set_inputs_with_dict({
            **func_load_image.inputs,
            **{
                'vae': func_vae_encode.inputs.vae,
                'grow_mask_by': func_vae_encode.inputs.grow_mask_by
            }
        })

        widget_load_image = ImageWidget(
            param_name='image_path',
            display_name=display_name,
            default_value=None,
            value_type=str
        )
        self.register_widget(widget_load_image)

        widget_grow_mask_by = IntWidget(
            display_name='Grow Mask By',
            param_name='grow_mask_by',
            default_value=6,
            min=0,
            max=64,
            step=1
        )
        self.register_widget(widget_grow_mask_by)

        self.link(func_load_image.outputs.image, func_vae_encode.inputs.pixels)
        self.link(func_load_image.outputs.mask, func_vae_encode.inputs.mask)

        self.share_outputs(func_vae_encode)


class Comp_ImagePadForOutpaint(Comp):
    def __init__(self,
                 name="ImagePadForOutpaint",
                 display_name='Image Pad For Outpaint',
                 left=0,
                 top=128,
                 right=0,
                 bottom=128,
                 feathering=40
                 ):
        super().__init__(name=name, display_name=display_name, grouped_widgets=True)

        func_pad_image = Func_ImagePadForOutpaint()
        self.register_func(func_pad_image)

        widget_pad_left = IntWidget(
            display_name='Left Padding',
            param_name='left',
            default_value=left,
            min=0,
            max=10240,
            step=32
        )
        self.register_widget(widget_pad_left)

        widget_pad_top = IntWidget(
            display_name='Top Padding',
            param_name='top',
            default_value=top,
            min=0,
            max=10240,
            step=32
        )
        self.register_widget(widget_pad_top)

        widget_pad_right = IntWidget(
            display_name='Right Padding',
            param_name='right',
            default_value=right,
            min=0,
            max=10240,
            step=32
        )
        self.register_widget(widget_pad_right)

        widget_pad_bottom = IntWidget(
            display_name='Bottom Padding',
            param_name='bottom',
            default_value=bottom,
            min=0,
            max=10240,
            step=32
        )
        self.register_widget(widget_pad_bottom)

        widget_feathering = IntWidget(
            display_name='Feathering',
            param_name='feathering',
            default_value=feathering,
            min=0,
            max=10240,
            step=1
        )
        self.register_widget(widget_feathering)


class Comp_LoadImageAndPadForOutpaint(Comp):
    def __init__(self,
                 name="Load Image And Pad For Outpainting",
                 display_name='Load Image to outpaint',
                 ):
        super().__init__(name=name, display_name=display_name, grouped_widgets=True)

        func_load_image = Func_LoadImage()
        self.register_func(func_load_image, share_io=False)

        func_pad_image = Func_ImagePadForOutpaint()
        self.register_func(func_pad_image, share_io=False)

        func_vae_encode = Func_VAEEncodeForInpaint()
        self.register_func(func_vae_encode, share_io=False)

        self.set_inputs_with_dict({
            **func_load_image.inputs,
            **{
                'left': func_pad_image.inputs.left,
                'top': func_pad_image.inputs.top,
                'right': func_pad_image.inputs.right,
                'bottom': func_pad_image.inputs.bottom,
                'feathering': func_pad_image.inputs.feathering,
            },
            **{
                'vae': func_vae_encode.inputs.vae,
                'grow_mask_by': func_vae_encode.inputs.grow_mask_by
            }
        })

        widget_load_image = ImageWidget(
            param_name='image_path',
            display_name=display_name,
            default_value=None,
            value_type=str
        )
        self.register_widget(widget_load_image)

        widget_pad_left = IntWidget(
            display_name='Left Padding',
            param_name='left',
            default_value=0,
            min=0,
            max=10240,
            step=32
        )
        self.register_widget(widget_pad_left)

        widget_pad_top = IntWidget(
            display_name='Top Padding',
            param_name='top',
            default_value=128,
            min=0,
            max=10240,
            step=32
        )
        self.register_widget(widget_pad_top)

        widget_pad_right = IntWidget(
            display_name='Right Padding',
            param_name='right',
            default_value=0,
            min=0,
            max=10240,
            step=32
        )
        self.register_widget(widget_pad_right)

        widget_pad_bottom = IntWidget(
            display_name='Bottom Padding',
            param_name='bottom',
            default_value=128,
            min=0,
            max=10240,
            step=32
        )
        self.register_widget(widget_pad_bottom)

        widget_feathering = IntWidget(
            display_name='Feathering',
            param_name='feathering',
            default_value=40,
            min=0,
            max=10240,
            step=1
        )
        self.register_widget(widget_feathering)

        widget_grow_mask_by = IntWidget(
            display_name='Grow Mask By',
            param_name='grow_mask_by',
            default_value=8,
            min=0,
            max=64,
            step=1
        )
        self.register_widget(widget_grow_mask_by)

        self.link(func_load_image.outputs.image, func_pad_image.inputs.image)
        self.link(func_pad_image.outputs.image, func_vae_encode.inputs.pixels)
        self.link(func_pad_image.outputs.mask, func_vae_encode.inputs.mask)

        self.share_outputs(func_vae_encode)


class Comp_LoadAndApplyControlNet(Comp):
    def __init__(self,
                 name="Load And Apply ControlNet",
                 display_name='ControlNet',
                 ):
        super().__init__(name=name, display_name=display_name)

        func_load_control_net = Func_ControlNetLoader()
        self.register_func(func_load_control_net, share_io=False)

        func_load_image = Func_LoadImage()
        self.register_func(func_load_image, share_io=False)

        func_apply_controlnet = Func_ControlNetApply()
        self.register_func(func_apply_controlnet, share_io=False)

        self.set_inputs_with_dict({
            **func_load_control_net.inputs,
            **func_load_image.inputs,
            **{
                'conditioning': func_apply_controlnet.inputs.conditioning,
                'strength': func_apply_controlnet.inputs.strength
            }
        })

        widget_controlnet_list = ModelComboWidget(
            display_name=display_name,
            param_name='controlnet_id',
            values_function_name='list_controlnets',
            default_value=None
        )
        widget_controlnet_list.set_optional(True)
        self.register_widget(widget_controlnet_list)

        widget_strength = FloatWidget(
            display_name='Strength',
            param_name='strength',
            default_value=1.0,
            min=0.0,
            max=10.0,
            step=0.1,
            round=2,
        )
        self.register_widget(widget_strength)

        widget_select_image = ImageWidget(
            param_name='image_path'
        )
        self.register_widget(widget_select_image)

        self.link(func_load_control_net.outputs.control_net, func_apply_controlnet.inputs.control_net)
        self.link(func_load_image.outputs.image, func_apply_controlnet.inputs.image)

        self.share_outputs(func_apply_controlnet)


class Comp_ClipLoader(Comp):
    def __init__(self,
                 name="Load CLIP",
                 display_name='Load CLIP',
                 default_clip_id='t5xxl_fp16.safetensors',
                 default_model_type='sd3'
                 ):
        super().__init__(name=name, display_name=display_name)

        func_load_clip = Func_ClipLoader()
        self.register_func(func_load_clip)

        widget_model_list = ModelComboWidget(
            display_name='Clip Model',
            param_name='clip_id',
            values_function_name='list_clips',
            default_value=default_clip_id
        )
        self.register_widget(widget_model_list)

        widget_clip_type = ComboWidget(
            display_name='Model Type',
            param_name='type',
            default_value=default_model_type,
            values=["stable_diffusion", "stable_cascade", "sd3", "stable_audio", "mochi", "ltxv"]
        )
        self.register_widget(widget_clip_type)


class Comp_DualCLIPLoader(Comp):
    def __init__(self,
                 name="Dual CLIP Loader",
                 display_name="Dual CLIP Loader",
                 default_clip_id1='clip_l.safetensors',
                 default_clip_id2='clip_g.safetensors',
                 default_model_type='sd3'
                 ):
        super().__init__(name=name, display_name=display_name)

        func_load_dual_clip = Func_DualCLIPLoader()
        self.register_func(func_load_dual_clip)

        widget_clip1 = ModelComboWidget(
            display_name='Clip 1',
            param_name='clip_id1',
            values_function_name='list_clips',
            default_value=default_clip_id1
        )
        self.register_widget(widget_clip1)

        widget_clip2 = ModelComboWidget(
            display_name='Clip 2',
            param_name='clip_id2',
            values_function_name='list_clips',
            default_value=default_clip_id2
        )
        self.register_widget(widget_clip2)

        widget_clip_type = ComboWidget(
            display_name='Model Type',
            param_name='type',
            default_value=default_model_type,
            values=["sdxl", "sd3", "flux"]
        )
        self.register_widget(widget_clip_type)


class Comp_TripleCLIPLoader(Comp):
    def __init__(self,
                 name="Triple CLIP Loader",
                 display_name="Triple CLIP Loader",
                 default_clip_id1='clip_l.safetensors',
                 default_clip_id2='clip_g.safetensors',
                 default_clip_id3='t5xxl_fp16.safetensors',
                 ):
        super().__init__(name=name, display_name=display_name)

        func_load_triple_clip = Func_TripleCLIPLoader()
        self.register_func(func_load_triple_clip)

        widget_clip1 = ModelComboWidget(
            display_name='Clip 1',
            param_name='clip_id1',
            values_function_name='list_clips',
            default_value=default_clip_id1
        )
        self.register_widget(widget_clip1)

        widget_clip2 = ModelComboWidget(
            display_name='Clip 2',
            param_name='clip_id2',
            values_function_name='list_clips',
            default_value=default_clip_id2
        )
        self.register_widget(widget_clip2)

        widget_clip3 = ModelComboWidget(
            display_name='Clip 3',
            param_name='clip_id3',
            values_function_name='list_clips',
            default_value=default_clip_id3
        )
        self.register_widget(widget_clip3)


class Comp_SD3ClipLoader(SwitchableComp):
    def __init__(self, name='SD3ClipLoader', display_name='SD3 Clip Loader'):
        super().__init__(name=name, display_name=display_name)
        comp_clip_loader = Comp_ClipLoader(name='Single Clip', display_name='Single Clip')
        comp_dual_clip_loader = Comp_DualCLIPLoader(name='Dual Clip', display_name='Dual Clip')
        comp_triple_loader = Comp_TripleCLIPLoader(name='Triple Clip', display_name='Triple Clip')
        self.set_comps([comp_clip_loader, comp_dual_clip_loader, comp_triple_loader])
        self.select_comp('Triple Clip')


class Comp_FluxGuidance(Comp):
    def __init__(self, name='FluxGuidance', display_name='Flux Guidance', guidance=3.5):
        super().__init__(name=name, display_name=display_name)

        flux_guidance = Func_FluxGuidance()
        self.register_func(flux_guidance)

        widget_guidance = FloatWidget(
            display_name='Flux Guidance',
            param_name='guidance',
            default_value=guidance,
            min=0.0,
            max=100.0,
            step=0.1,
            round=2
        )
        self.register_widget(widget_guidance)


class Comp_UNETLoader(Comp):
    def __init__(self, name='UnetLoader', display_name='Unet Loader', default_unet_id=None,
                 default_weight_type='default'):
        super().__init__(name=name, display_name=display_name)
        unet_loader = Func_UNETLoader()
        self.register_func(unet_loader)

        widget_unet_loader = ModelComboWidget(
            display_name=display_name,
            param_name='unet_id',
            values_function_name='list_checkpoints',
            default_value=default_unet_id
        )
        self.register_widget(widget_unet_loader)

        widget_weight_dtype = ComboWidget(
            display_name='Widget Type',
            param_name='weight_dtype',
            values=["default", "fp8_e4m3fn", "fp8_e4m3fn_fast", "fp8_e5m2"],
            default_value=default_weight_type
        )
        self.register_widget(widget_weight_dtype)


class Comp_BasicScheduler(Comp):
    def __init__(self, name='BasicScheduler', display_name='Basic Scheduler', scheduler_name='simple', steps=20,
                 denoise=1.0, grouped_widgets=True):
        super().__init__(name=name, display_name=display_name, grouped_widgets=grouped_widgets)

        basic_scheduler = Func_BasicScheduler()
        self.register_func(basic_scheduler)

        widget_scheduler_name = ComboWidget(
            display_name='Scheduler',
            param_name='scheduler',
            default_value=scheduler_name,
            values=comfy.samplers.SCHEDULER_NAMES
        )
        self.register_widget(widget_scheduler_name)

        widget_steps = IntWidget(
            display_name='Steps',
            param_name='steps',
            default_value=steps,
            min=1,
            max=1000,
            step=1
        )
        self.register_widget(widget_steps)

        widget_denoise = FloatWidget(
            display_name='Denoise',
            param_name='denoise',
            default_value=denoise,
            min=0.0,
            max=1.0,
            step=0.05,
            round=2
        )
        self.register_widget(widget_denoise)


class Comp_KSamplerSelect(Comp):
    def __init__(self, name='KSamplerSelect', display_name='KSampler Select', sampler_name='euler'):
        super().__init__(name=name, display_name=display_name)

        ksampler_select = Func_KSamplerSelect()
        self.register_func(ksampler_select)

        widget_sampler_name = ComboWidget(
            display_name='Sampler',
            param_name='sampler_name',
            default_value=sampler_name,
            values=comfy.samplers.SAMPLER_NAMES
        )
        self.register_widget(widget_sampler_name)


class Comp_RandomNoise(Comp):
    def __init__(self, name='RandomNoise', display_name='Random Noise', noise_seed=None):
        super().__init__(name=name, display_name=display_name)

        random_noise = Func_RandomNoise()
        self.register_func(random_noise)

        widget_noise_seed = SeedWidget(
            display_name='Seed',
            param_name='noise_seed',
            default_value=noise_seed
        )
        self.register_widget(widget_noise_seed)


class Comp_InpaintModelConditioning(Comp):
    def __init__(self, name='InpaintModelConditioning', display_name='Inpaint Model Conditioning', noise_mask=False):
        super().__init__(name=name, display_name=display_name)

        inpaint_model_conditioning = Func_InpaintModelConditioning()
        self.register_func(inpaint_model_conditioning)

        widget_noise_mask = BoolWidget(
            display_name='Noise Mask',
            param_name='noise_mask',
            default_value=noise_mask
        )
        self.register_widget(widget_noise_mask)


class Comp_LTXVConditioning(Comp):
    def __init__(self, name='LTXVConditioning', display_name='LTXV Conditioning', frame_rate=25.0):
        super().__init__(name=name, display_name=display_name)

        ltxv_cond = Func_LTXVConditioning()
        self.register_func(ltxv_cond)

        widget_frame_rate = FloatWidget(
            display_name='Frame Rate',
            param_name='frame_rate',
            default_value=frame_rate,
            min=0.0,
            max=1000.0,
            step=0.1,
            round=2
        )
        self.register_widget(widget_frame_rate)


class Comp_EmptyLTXVLatentVideo(Comp):
    def __init__(self,
                 name='EmptyLTXVLatentVideo',
                 display_name='Empty LTXV Latent Video',
                 width=768,
                 height=512,
                 length=97,
                 grouped_widgets=True
                 ):
        super().__init__(name=name, display_name=display_name, grouped_widgets=grouped_widgets)

        empty_latent_video = Func_EmptyLTXVLatentVideo()
        self.register_func(empty_latent_video)

        widget_width = IntWidget(
            display_name='Width',
            param_name='width',
            default_value=width,
            min=64,
            max=5120,
            step=32
        )
        self.register_widget(widget_width)

        widget_height = IntWidget(
            display_name='Height',
            param_name='height',
            default_value=height,
            min=64,
            max=5120,
            step=32
        )
        self.register_widget(widget_height)

        widget_length = IntWidget(
            display_name='Length',
            param_name='length',
            default_value=length,
            min=1,
            max=5120,
            step=8
        )
        self.register_widget(widget_length)


class Comp_LTXVScheduler(Comp):
    def __init__(self,
                 name='LTXVScheduler',
                 display_name='LTXV Scheduler',
                 steps=20,
                 max_shift=2.05,
                 base_shift=0.95,
                 stretch=True,
                 terminal=0.1,
                 grouped_widgets=True
                 ):
        super().__init__(name=name, display_name=display_name, grouped_widgets=grouped_widgets)

        ltxv_scheduler = Func_LTXVScheduler()
        self.register_func(ltxv_scheduler)

        widget_steps = IntWidget(
            display_name='Steps',
            param_name='steps',
            default_value=steps,
            min=1,
            max=10000,
        )
        self.register_widget(widget_steps)

        widget_max_shift = FloatWidget(
            display_name='Max Shift',
            param_name='max_shift',
            default_value=max_shift,
            min=0.0,
            max=100.0,
            step=0.01,
        )
        self.register_widget(widget_max_shift)

        widget_base_shift = FloatWidget(
            display_name='Base Shift',
            param_name='base_shift',
            default_value=base_shift,
            min=0.0,
            max=100.0,
            step=0.01,
        )
        self.register_widget(widget_base_shift)

        widget_stretch = BoolWidget(
            display_name='Stretch',
            param_name='stretch',
            default_value=stretch
        )
        self.register_widget(widget_stretch)

        widget_terminal = FloatWidget(
            display_name='Terminal',
            param_name='terminal',
            default_value=terminal,
            min=0.0,
            max=0.99,
            step=0.01,
        )
        self.register_widget(widget_terminal)


class Comp_SamplerCustom(Comp):
    def __init__(self,
                 name='SamplerCustom',
                 display_name='Sampler Custom',
                 add_noise=True,
                 noise_seed=1001,
                 cfg=3.0,
                 grouped_widgets=True,
                 preview_steps=1
                 ):
        super().__init__(name=name, display_name=display_name, grouped_widgets=grouped_widgets)

        sampler_custom = Func_SamplerCustom(preview_steps=preview_steps)
        self.register_func(sampler_custom)

        widget_add_noise = BoolWidget(
            display_name='add_noise',
            param_name='add_noise',
            default_value=add_noise
        )
        self.register_widget(widget_add_noise)

        widget_noise_seed = SeedWidget(
            display_name='Seed',
            param_name='noise_seed',
            default_value=noise_seed
        )
        self.register_widget(widget_noise_seed)

        widget_cfg = FloatWidget(
            display_name='CFG Scale',
            param_name='cfg',
            default_value=cfg,
            min=0.0,
            max=100.0,
            step=0.1,
            round=2
        )
        self.register_widget(widget_cfg)


class Comp_SaveAnimatedWEBP(Comp):
    def __init__(self,
                 name='SaveAnimatedWEBP',
                 display_name='Save Animated WEBP',
                 fps=6.0,
                 lossless=True,
                 quality=80,
                 method='default',
                 grouped_widgets=True
                 ):
        super().__init__(name=name, display_name=display_name, grouped_widgets=grouped_widgets)

        save_animated_webp = Func_SaveAnimatedWEBP()
        self.register_func(save_animated_webp)

        widget_fps = FloatWidget(
            display_name='FPS',
            param_name='fps',
            default_value=fps,
            min=0.01,
            max=1000.0,
            step=0.1,
            round=2
        )
        self.register_widget(widget_fps)

        widget_lossless = BoolWidget(
            display_name='Lossless',
            param_name='lossless',
            default_value=lossless
        )
        self.register_widget(widget_lossless)

        widget_quality = IntWidget(
            display_name='Quality',
            param_name='quality',
            default_value=quality,
            min=0,
            max=100,
        )
        self.register_widget(widget_quality)

        widget_method = ComboWidget(
            display_name='Method',
            param_name='method',
            default_value=method,
            values=save_animated_webp.method_names
        )
        self.register_widget(widget_method)


class Comp_LTXVImgToVideo(Comp):
    def __init__(self,
                 name='LTXVImgToVideo',
                 display_name='LTXV Image To Video',
                 width=768,
                 height=512,
                 length=97,
                 grouped_widgets=True
                 ):
        super().__init__(name=name, display_name=display_name, grouped_widgets=grouped_widgets)

        ltxv_img_to_video = Func_LTXVImgToVideo()
        self.register_func(ltxv_img_to_video)

        widget_width = IntWidget(
            display_name='Width',
            param_name='width',
            default_value=width,
            min=64,
            max=5120,
            step=32
        )
        self.register_widget(widget_width)

        widget_height = IntWidget(
            display_name='Height',
            param_name='height',
            default_value=height,
            min=64,
            max=5120,
            step=32
        )
        self.register_widget(widget_height)

        widget_length = IntWidget(
            display_name='Length',
            param_name='length',
            default_value=length,
            min=1,
            max=5120,
            step=8
        )
        self.register_widget(widget_length)
