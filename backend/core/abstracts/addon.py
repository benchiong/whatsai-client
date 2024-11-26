from abc import ABC, abstractmethod
from typing import Literal

AddonType = Literal['Vae', 'LoRA', 'Hypernet', 'HiresFix', 'Upscale', 'Controlnet']
ADD_ON_CLASS_MAP = {}

def register_addon_class(name, addon_class):
    global ADD_ON_CLASS_MAP
    ADD_ON_CLASS_MAP[name] = addon_class

class Addon(ABC):
    comp_list = False
    """ If True, it says this addon can be add new comp instance by front user, 
        for example, user can add multiple LoRAs, the number is decided by user,
        If False, only one single comp needed.
    """
    can_turn_off = False
    """ Some addon need to turn off explicitly, e.g. HiresAddon """

    def __init__(self, addon_type: AddonType, display_name: str, cache_out=True, valid_inputs=True):
        super().__init__()

        self.display_name = display_name
        self.cache_out = cache_out
        self.valid_inputs = valid_inputs

        self.addon_type: AddonType = addon_type  # set by subclass
        self.comp_classes = []
        """ set by subclass, the comp/comps used to instantiate comp/comps object. """

        self.comps = []
        self.inputs_info = []

        self.funcs = []

    @abstractmethod
    def run(self, *args, **kwargs):
        pass

    def __call__(self, *args, **kwargs):
        return self.run(*args, **kwargs)

    def make_type_right(self):
        for index, (comp, comp_input) in enumerate(zip(self.comps, self.inputs_info)):
            self.inputs_info[index] = comp.make_widget_inputs_type_right(comp_input)

    def register_comp_class(self, comp_class):
        self.comp_classes.append(comp_class)

    def register_func(self, func):
        self.funcs.append(func)

    @classmethod
    def create_by_inputs(cls, addon_type: AddonType, inputs_info: list[dict]):
        """ Create Addon dynamically, for the situation when card user selects uncertain amount comps of Addon.
            When addon is single comp, addon create comp when init, because no uncertain things.
        """
        addon_class = ADD_ON_CLASS_MAP.get(addon_type)
        assert addon_class, 'Can not find addon class: {}'.format(addon_type)
        addon = addon_class()
        addon.inputs_info = inputs_info

        if cls.comp_list:
            addon.create_comp_list(inputs_info)

        addon.make_type_right()

        return addon

    def create_comp_list(self, inputs_info: list[dict]):
        """ The design of addon's comp list here is that one addon has only one type comp,
            if we need multiple type comps to finish the job, do the compose thing on comp layer.
        """
        comp_classes = self.comp_classes
        assert comp_classes, 'You must set comp_classes when create addon: {}'.format(self.__class__.__name__)
        for i in range(len(inputs_info)):
            comp_obj = comp_classes[0]()
            self.comps.append(comp_obj)

    def valid_widget_inputs(self, inputs_info: list[dict]):
        if not len(self.comps) > 0:
            return []  # no error

        comp = self.comps[0]  # comps are in same type, any one is ok to valid.
        errors = []
        for inputs in inputs_info:
            error_list = comp.valid_widget_inputs(**inputs)
            if error_list:
                errors.extend(error_list)
        return errors

    @property
    def type(self):
        return self.addon_type

    @property
    def widget_list(self):
        result = []
        for comp in self.comps:
            result.append(comp.widgets)
        return result

    @property
    def local_widgets_info(self):
        result = {}
        for comp in self.comps:
            result = {
                **result,
                **comp.widgets_dict
            }
        result_array = []
        for v in result.values():
            result_array.append(v)
        return result_array

    @property
    def widgets_info(self):
        result = {}
        for comp_class in self.comp_classes:
            comp = comp_class()
            result = {
                **result,
                **comp.widgets_dict
            }
        return result

    @property
    def widgets_info_in_list(self):
        return list(self.widgets_info.values())

    @property
    def addon_info(self):
        result = {
            'addon_name': self.addon_type,
            'display_name': self.display_name,
            'comp_list': self.comp_list,
            'can_turn_off': self.can_turn_off,
            'comp_widgets': self.widgets_info_in_list,  # use this to tell frontend how to render
            'widgets': [self.widgets_info_in_list]  # use this to get inputs from frontend
        }
        if self.can_turn_off:
            result['is_off'] = True

        return result