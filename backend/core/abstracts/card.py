import gc
import traceback
from abc import ABC, abstractmethod

from .comp import Comp
from .addon import Addon, ADD_ON_CLASS_MAP, AddonType


class ValidException(Exception):
    pass

class Card(ABC):
    name = None
    display_name = None
    meta_data = {}

    def __init__(self, name=None, display_name=None, card_type=None, cache_out=True, valid_inputs=True):
        """ Take this as the workflow in ComfyUI, but the creation is by Card author through coding
            instead of Workflow authors, We believe it's more friendlly for end users to run an AI job
            with cards, and also more efficient for Card authors to creat one and share to all.

            Subclass should create and add comps, the order of comps to register matters.
        """

        if name:
            self.name = name
        if display_name:
            self.display_name = display_name

        self.card_type = card_type

        self.cache_out = cache_out
        self.valid_inputs = valid_inputs

        self.comps = {}
        self.addons = {}
        self.support_addon_types = []

        self.progress_callbacks = {}

    @abstractmethod
    def run(self, base_inputs: dict, addon_inputs: dict, valid_func_inputs: bool) -> any:
        """ Subclass implement this to do the real work. """
        pass

    def __call__(self, base_inputs: dict, addon_inputs: dict = None, valid_func_inputs=False):
        base_inputs = self.make_type_right(base_inputs)
        errors = {}
        input_errors = self.valid_widget_inputs(base_inputs)
        if input_errors:
            errors['inputs_valid_errors'] = input_errors

        if addon_inputs:
            create_addon_errors = self.create_addons_by_inputs(addon_inputs)
            if create_addon_errors:
                errors['create_addon_errors'] = create_addon_errors

        if errors:
            raise ValidException(str(errors))
        try:
            return self.run(base_inputs=base_inputs, addon_inputs=addon_inputs, valid_func_inputs=valid_func_inputs)
        except Exception as e:
            traceback.print_exc()

    def create_addons_by_inputs(self, addon_inputs):
        errors = []
        for addon_type, inputs in addon_inputs.items():
            addon_class = ADD_ON_CLASS_MAP.get(addon_type)
            if not addon_class:
                errors.append('Addon type: {} not found.'.format(addon_type))
                continue
            addon = addon_class.create_by_inputs(addon_type=addon_type, inputs_info=inputs)
            self.addons[addon.type] = addon
            inputs_valid_errors = addon.valid_widget_inputs(inputs)
            if inputs_valid_errors:
                errors.extend(inputs_valid_errors)

        return errors

    def make_type_right(self, base_inputs):
        for comp in self.comps.values():
            base_inputs = comp.make_widget_inputs_type_right(base_inputs)
        return base_inputs

    def valid_addon_inputs(self, addon_inputs):
        errors = []
        for addon_type, inputs in addon_inputs.items():
            addon = self.addons[addon_type]
            if not addon:
                errors.append('Addon type: {} not found.'.format(addon_type))
            error_list = addon.valid_widget_inputs(inputs)
            if error_list:
                errors.extend(error_list)
        return errors

    def register_comp(self, comp: Comp):
        self.comps[comp.name] = comp

    def register_addon(self, addon_key: str, addon: Addon):
        if not addon_key or not addon:
            return

        self.addons[addon_key] = addon

    def init_supported_addons(self, addons: [AddonType]):
        for addon in addons:
            addon_class = ADD_ON_CLASS_MAP[addon]
            self.register_addon(addon, addon_class())

    @property
    def widgets(self):
        result = {}
        for comp in self.comps.values():
            result = {
                **result,
                **comp.widgets
            }
        return result

    @property
    def local_widgets_info(self):
        """ Widgets all flat map to param, used to validate"""
        result = {}
        for comp in self.comps.values():
            result = {
                **result,
                **comp.widgets_dict
            }
        return result

    @property
    def local_widgets_info_grouped_widgets_considered(self):
        """ Widgets may be grouped, used to tell frontend to render"""
        result = {}
        for comp in self.comps.values():
            result = {
                **result,
                **comp.widgets_dict_grouped_widgets_considered
            }
        return result

    @property
    def widgets_info_in_list(self):
        """ dict in python has order, but javascript seems not, so we need it here. """
        return list(self.local_widgets_info_grouped_widgets_considered.values())

    @property
    def default_widget_values(self):
        result = {}
        for comp in self.comps.values():
            result = {
                **result,
                **comp.widgets_value_info
            }
        return result

    @property
    def addon_infos(self):
        result = {}
        for key, addon in self.addons.items():
            result[key] = addon.addon_info
        return result

    @property
    def addons_info_in_list(self):
        return list(self.addon_infos.values())

    @property
    def card_info(self):
        return {
            'card_name': self.name,
            'card_display_name': self.display_name,
            'widgets': self.widgets_info_in_list,
            'addons': self.addons_info_in_list
        }

    @property
    def card_inputs_info(self):
        return {
            'card_name': self.name,
            'widget_values': self.default_widget_values,
            'support_addon_types': self.support_addon_types,
        }

    def valid_widget_inputs(self, inputs_info: dict) -> list[str]:
        """ Used to valid input values from frontend by calling the comp's valid_widget_inputs function.
            Theoretically, inputs_info are all widgets inputs.
        """
        errors = []
        param_names = list(self.local_widgets_info.keys())
        for param_name, param_value in inputs_info.items():
            param_widget = self.widgets.get(param_name)
            if not param_widget:
                errors.append("Widget of param name: {} not found.".format(param_name))
                continue

            if param_name in param_names:
                param_names.remove(param_name)
            elif param_widget.optional and param_value is None:
                continue
            else:
                errors.append("Card got unknown param name: {}".format(param_name))
                continue

            valid_error = param_widget.valid_input(param_value)
            if valid_error:
                errors.append(valid_error)
        if param_names:
            errors.append("Params: {} did not get value.".format(param_names))
        return errors

    def register_progress_callback(self, name, callback):
        self.progress_callbacks[name] = callback

    def get_progress_callback(self, name):
        return self.progress_callbacks.get(name)
