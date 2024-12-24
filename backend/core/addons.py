from core.abstracts.addon import Addon
from core.comps import (
    Comp_VAELoader,
    Comp_LoRALoader,
    Comp_HypernetLoader,
    Comp_UpscaleImageUsingModel,
    Comp_LoadAndApplyControlNet, Comp_SD3ClipLoader,
)


class Addon_Vae(Addon):
    addon_type = 'Vae'

    def __init__(self):
        super().__init__(
            name='Vae',
            display_name='Vae',
            can_user_add_new=False,
            can_turn_off=False,
        )

    def init_comp_unit_or_comp_list(self):
        vae_comp = Comp_VAELoader()
        self.register_comp(vae_comp)
        self.share_io(vae_comp)


class Addon_LoRA(Addon):
    addon_type = 'LoRA'

    def __init__(self):
        super().__init__(name='LoRA', display_name='LoRA', can_user_add_new=True, can_turn_off=False)

    def init_comp_unit_or_comp_list(self):
        self.comp_class = Comp_LoRALoader


class Addon_Hypernet(Addon):
    addon_type = 'Hypernet'

    def __init__(self):
        super().__init__(name='Hypernet', display_name='Hypernet', can_user_add_new=True, can_turn_off=False)

    def init_comp_unit_or_comp_list(self):
        self.comp_class = Comp_HypernetLoader


class Addon_Upscale(Addon):
    addon_type = 'Upscale'

    def __init__(self):
        super().__init__(name='Upscale', display_name='Upscale', can_user_add_new=False, can_turn_off=False)

    def init_comp_unit_or_comp_list(self):
        scale_comp = Comp_UpscaleImageUsingModel()
        self.register_comp(scale_comp)
        self.share_io(scale_comp)


class Addon_ControlNet(Addon):
    addon_type = 'Controlnet'

    def __init__(self):
        super().__init__(name='Controlnet', display_name='Controlnet', can_user_add_new=True, can_turn_off=False)

    def init_comp_unit_or_comp_list(self):
        self.comp_class = Comp_LoadAndApplyControlNet


class Addon_SD3Clip(Addon):
    addon_type = 'Clip'

    def __init__(self):
        super().__init__(
            name='Clip',
            display_name='Clip',
            can_user_add_new=False,
            can_turn_off=False,
            is_switchable=True
        )

    def init_comp_unit_or_comp_list(self):
        clip_comp = Comp_SD3ClipLoader()
        self.register_comp(clip_comp)


ADD_ON_CLASS_MAP = {
    Addon_Vae.addon_type: Addon_Vae,
    Addon_LoRA.addon_type: Addon_LoRA,
    Addon_Hypernet.addon_type: Addon_Hypernet,
    Addon_Upscale.addon_type: Addon_Upscale,
    Addon_ControlNet.addon_type: Addon_Upscale,
    Addon_SD3Clip.addon_type: Addon_SD3Clip
}
