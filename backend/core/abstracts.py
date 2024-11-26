# import collections
# import inspect
# from abc import ABC, abstractmethod
# from types import UnionType
# from typing import Literal, Type, get_origin, get_args
#
# import torch
#
# from misc.logger import logger
#
#
# class ParameterValidationException(Exception):
#     pass
#
# class Func(ABC):
#     def __init__(self, name=None, cache_out=True, valid_inputs=True):
#         self._name = name
#         """ We need it when multiple Func of same type in parent(Card/Addon). """
#
#         self.cache_out = cache_out
#         self._valid_inputs = valid_inputs
#
#         self.last_inputs = None
#         self.last_out = None
#
#     @abstractmethod
#     def run(self, *args, **kwargs) -> any:
#         pass
#
#     def __call__(self, *args, **kwargs):
#         if self.cache_out and self._inputs_unchanged(*args, **kwargs):
#             return self.last_out
#
#         if self._valid_inputs:
#             self.valid_inputs(*args, **kwargs)
#
#         out = self.run(*args, **kwargs)
#
#         if self.cache_out:
#             self.last_inputs = args, kwargs
#             self.last_out = out
#
#         return out
#
#     @property
#     def name(self):
#         return self._name if self._name else self.__class__.__name__
#
#     @property
#     def param_names(self):
#         names = inspect.signature(self.run).parameters.keys()
#         return tuple(names)
#
#     def valid_inputs(self, *args, **kwargs):
#         def valid_type(value, expected_type):
#             origin_type = get_origin(expected_type)
#             args_type = get_args(expected_type)
#             if origin_type is None or origin_type is collections.abc.Callable:
#                 return isinstance(value, expected_type)
#             if origin_type is Literal:
#                 return value in args_type
#             if origin_type is UnionType:
#                 return any([valid_type(value, arg_type) for arg_type in args_type])
#             if not isinstance(value, origin_type):
#                 return False
#             if origin_type is list or origin_type is tuple:
#                 return len(value) > 0 and all(valid_type(v, args_type[0]) for v in value)
#             if origin_type is dict:
#                 not_empty = len(value) > 0
#                 keys_valid = all(valid_type(k, args_type[0]) for k in value.keys())
#                 values_valid = all(valid_type(v, args_type[1]) for v in value.values())
#                 return not_empty and keys_valid and values_valid
#             return False
#
#         valid_infos = []
#         signature = inspect.signature(self.run)
#         for i, param in enumerate(signature.parameters.values()):
#             param_name = param.name
#             param_type = param.annotation
#             param_value = args[i] if i < len(args) else kwargs.get(param_name)
#             if param_type is inspect._empty or valid_type(param_value, param_type):
#                 continue
#             else:
#                 valid_infos.append('Input value: {} of param: {} mismatch, expect type {}, but got {}.'.format(
#                     param_value, param_name, param_type, type(param_value)))
#
#         if valid_infos:
#             raise ParameterValidationException(str(valid_infos))
#
#     def _inputs_unchanged(self, *args, **kwargs) -> bool:
#         if not self.last_inputs:
#             return False
#
#         last_args, last_kwargs = self.last_inputs
#
#         def equals(a, b):
#             if not type(b) == type(a):
#                 return False
#
#             if isinstance(a, (tuple, list)):
#                 if not len(a) == len(b):
#                     return False
#
#                 result = []
#                 for _a, _b in zip(a, b):
#                     result.append(equals(_a, _b))
#                 return all(result)
#
#             elif isinstance(a, dict):
#                 a_values = tuple(a.values())
#                 b_values = tuple(b.values())
#                 a_keys = tuple(a.keys())
#                 b_keys = tuple(b.keys())
#                 return equals(a_values, b_values) and equals(a_keys, b_keys)
#             elif torch.is_tensor(a) and torch.is_tensor(b):
#                 return torch.equal(a, b)
#             else:
#                 if torch.is_tensor(a) or torch.is_tensor(b):
#                     return False
#
#                 try:
#                     return a == b
#                 except Exception as e:
#                     logger.debug("Equal func exception:", e, 'a:', a, 'b:', b)
#                     return False
#
#         return equals(args, last_args) and equals(kwargs, last_kwargs)
#
#
# class Widget(ABC):
#     """ One widget for one param value, make it be the smallest unit. Take it as the bridge of frontend and backend. """
#
#     def __init__(self, param_name, display_name, default_value, value_type: Type, optional=False):
#         self.param_name = param_name
#         self.display_name = display_name
#         self.value = default_value
#         self.value_type = value_type
#         self.optional = optional
#
#         self._origin_to_new_param_name_map = {}
#         self._current_to_origin_param_name_map = {}
#
#     def set_optional(self, optional):
#         self.optional = optional
#
#     @abstractmethod
#     def valid_input(self, param_value) -> str | None:
#         """ Used to valid the values from frontend, and transform them to the right value type.
#             :param param_value: value of the param.
#             :return: error info if fails else None.
#         """
#         pass
#
#     def make_type_right(self, param_value):
#         """
#             Make the value from frontend the right type, as the data from frontend is
#             in json form, transform it to corresponding type like ComfyUI do.
#             https://github.com/comfyanonymous/ComfyUI/blob/master/execution.py#L633
#             Do not raise exception, return origin value if failed.
#             Override this method if you have custom logic.
#
#             :param param_value: value of the param.
#             :return: the value after correction
#         """
#         try:
#             if param_value == 'None' or param_value is None:
#                 return None
#             if self.value_type in [int, str, bool, float]:
#                 return self.value_type(param_value)
#             else:
#                 return param_value
#         except Exception as e:
#             return param_value
#
#     @property
#     def dict(self):
#         """ Used to tell frontend how to render UI by backend. """
#         param_name = self.param_name
#         if self.param_name in self._origin_to_new_param_name_map:
#             param_name = self._origin_to_new_param_name_map.get(param_name)
#         return {
#             # 'widget_name': self.widget_name,
#             'display_name': self.display_name,
#             'param_name': param_name,
#             'value': self.value,
#             'optional': self.optional,
#             'widget_type': self.__class__.__name__,
#         }
#
#     @property
#     def default_value_info(self):
#         return {}
#
#     def map_param_name(self, origin_param_name, new_param_name):
#         """ We need this when the upstream(Card/Addon) want a different param name, especially they have
#             multiple comps in one object to distinguish parameters.
#         """
#         assert origin_param_name == self.param_name, (
#             'Param name: {} not match widget param name. '.format(origin_param_name))
#         self._origin_to_new_param_name_map[origin_param_name] = new_param_name
#         self._current_to_origin_param_name_map[new_param_name] = origin_param_name
#
# COMP_CLASS_MAP = {}
# class Comp(Func):
#     """ Comp, short for Compose or Component,
#         when taking as Compose, means Compose of Widgets and Funcs
#         when taking as Component, means Component of Card or Addon.
#         All depends on your mood.
#         It's designed like Node in ComfyUI, but with explicit widgets and supporting composition of funcs.
#         It should be treated as the smallest unit of Card and Addon.
#     """
#
#     def __init__(self, name=None, display_name=None, cache_out=True, valid_inputs=True):
#         """ Subclass should create and add widgets and funcs here, the order of widgets to register matters. """
#         super().__init__(cache_out, valid_inputs)
#
#         self._name = name
#         self._display_name = display_name
#         self._widgets: dict[str: Widget] = {}  # { param_name: widget }
#         self.funcs: dict[str: Func] = {}  # { func_name, func }
#
#         self._origin_to_new_param_name_map = {}
#         self._current_to_origin_param_name_map = {}
#         self.optional = False
#
#     def set_optional(self, optional):
#         self.optional = optional
#         for widget in self._widgets.values():
#             widget.set_optional(optional)
#
#     @abstractmethod
#     def run(self, **kwargs):
#         """ Notice: We *force* parameters to keyword args for easier use.
#         """
#         pass
#
#     def __call__(self, **kwargs):
#         origin_kwargs = self.restore_origin_param_name(**kwargs)
#         # self.make_widget_inputs_type_right(**origin_kwargs)
#         return self.run(**origin_kwargs)
#
#     @property
#     def name(self):
#         return self._name if self._name else self.__class__.__name__
#
#     @property
#     def display_name(self):
#         return self._display_name if self._display_name else self.name
#
#     @property
#     def widgets(self):
#         _widgets = {}
#         for param_name, widget in self._widgets.items():
#             mapped_param_name = self._origin_to_new_param_name_map.get(param_name)
#             if mapped_param_name:
#                 _widgets[mapped_param_name] = widget
#             else:
#                 _widgets[param_name] = widget
#         return _widgets
#
#     @property
#     def widgets_dict(self):
#         """ Used to tell frontend how to render UI by backend. """
#         result = {}
#         for param_name, widget in self.widgets.items():
#             mapped_param_name = self._origin_to_new_param_name_map.get(param_name)
#             if mapped_param_name:
#                 result[mapped_param_name] = widget.dict
#             else:
#                 result[param_name] = widget.dict
#         return result
#
#     @property
#     def widgets_value_info(self):
#         """ Used to tell the values of widgets. """
#         result = {}
#         for param_name, widget in self.widgets.items():
#             if widget.default_value_info:
#                 result = {
#                     **result,
#                     **widget.default_value_info
#                 }
#             else:
#                 result[param_name] = widget.value
#         return result
#
#     def register_widget(self, widget: Widget):
#         self._widgets[widget.param_name] = widget
#
#     def register_func(self, func: Func):
#         self.funcs[func.name] = func
#
#     def make_widget_inputs_type_right(self, kwargs):
#         for param_name, param_value in kwargs.items():
#             widget = self.widgets.get(param_name)
#             if widget:
#                 kwargs[param_name] = widget.make_type_right(param_value)
#         return kwargs
#
#     def valid_widget_inputs(self, **kwargs) -> list[str]:
#         """ Used to valid input values from frontend by calling the widget's valid_input function.
#             Notice: Call it after param map if needed.
#             :return: errors list, return empty list if success.
#         """
#         errors = []
#         widget_param_names = list(self.widgets.keys())
#         for param_name, param_value in kwargs.items():
#             widget = self.widgets.get(param_name)
#             if not widget:
#                 continue
#             error = widget.valid_input(param_value)
#             if error:
#                 errors.append(error)
#             widget_param_names.remove(param_name)
#
#         if widget_param_names:
#             errors.append("Params from widget: {} did not get value.".format(widget_param_names))
#
#         return errors
#
#     def map_param_name(self, origin_param_name, new_param_name):
#         """ We need this when the upstream(Card/Addon) want a different param name, especially they have
#             multiple comps in one type to distinguish parameters.
#         """
#         assert origin_param_name in self.widgets.keys(), (
#             'Param name: {} not in widget param names. '.format(origin_param_name))
#         self._origin_to_new_param_name_map[origin_param_name] = new_param_name
#         self._current_to_origin_param_name_map[new_param_name] = origin_param_name
#         for widget in self._widgets.values():
#             if widget.param_name == origin_param_name:
#                 widget.map_param_name(origin_param_name, new_param_name)
#                 break
#
#     def map_all_param_names_with_prefix(self, prefix):
#         for widget in self._widgets.values():
#             origin_param_name = widget.param_name
#             mapped_param_name = prefix + 'origin_param_name'
#
#             widget.map_param_name(origin_param_name, mapped_param_name)
#             self._origin_to_new_param_name_map[origin_param_name] = mapped_param_name
#             self._current_to_origin_param_name_map[mapped_param_name] = origin_param_name
#
#     def restore_origin_param_name(self, **kwargs):
#         for current_param_name, param_value in kwargs.items():
#             if current_param_name in self._current_to_origin_param_name_map:
#                 origin_param_name = self._current_to_origin_param_name_map[current_param_name]
#                 kwargs[origin_param_name] = param_value
#                 kwargs.pop(current_param_name)
#         return kwargs
#
#
# AddonType = Literal['Vae', 'LoRA', 'Hypernet', 'HiresFix', 'Upscale', 'Controlnet']
# ADD_ON_CLASS_MAP = {}
# def register_addon_class(name, addon_class):
#     global ADD_ON_CLASS_MAP
#     ADD_ON_CLASS_MAP[name] = addon_class
#     logger.debug("register_addon_class: {} {} {}".format(ADD_ON_CLASS_MAP, name, addon_class))
#
# class Addon(ABC):
#     comp_list = False
#     """ If True, it says this addon can be add new comp instance by front user,
#         for example, user can add multiple LoRAs, the number is decided by user,
#         If False, only one single comp needed.
#     """
#     can_turn_off = False
#     """ Some addon need to turn off explicitly, e.g. HiresAddon """
#
#     def __init__(self, addon_type: AddonType, display_name: str, cache_out=True, valid_inputs=True):
#         super().__init__()
#
#         self.display_name = display_name
#         self.cache_out = cache_out
#         self.valid_inputs = valid_inputs
#
#         self.addon_type: AddonType = addon_type  # set by subclass
#         self.comp_classes = []
#         """ set by subclass, the comp/comps used to instantiate comp/comps object. """
#
#         self.comps = []
#         self.inputs_info = []
#
#         self.funcs = []
#
#     @abstractmethod
#     def run(self, *args, **kwargs):
#         pass
#
#     def __call__(self, *args, **kwargs):
#         return self.run(*args, **kwargs)
#
#     def make_type_right(self):
#         for index, (comp, comp_input) in enumerate(zip(self.comps, self.inputs_info)):
#             self.inputs_info[index] = comp.make_widget_inputs_type_right(comp_input)
#
#     def register_comp_class(self, comp_class):
#         self.comp_classes.append(comp_class)
#
#     def register_func(self, func):
#         self.funcs.append(func)
#
#     @classmethod
#     def create_by_inputs(cls, addon_type: AddonType, inputs_info: list[dict]):
#         """ Create Addon dynamically, for the situation when card user selects uncertain amount comps of Addon.
#             When addon is single comp, addon create comp when init, because no uncertain things.
#         """
#         addon_class = ADD_ON_CLASS_MAP.get(addon_type)
#         assert addon_class, 'Can not find addon class: {}'.format(addon_type)
#         addon = addon_class()
#         addon.inputs_info = inputs_info
#
#         if cls.comp_list:
#             addon.create_comp_list(inputs_info)
#
#         addon.make_type_right()
#
#         return addon
#
#     def create_comp_list(self, inputs_info: list[dict]):
#         """ The design of addon's comp list here is that one addon has only one type comp,
#             if we need multiple type comps to finish the job, do the compose thing on comp layer.
#         """
#         comp_classes = self.comp_classes
#         assert comp_classes, 'You must set comp_classes when create addon: {}'.format(self.__class__.__name__)
#         for i in range(len(inputs_info)):
#             comp_obj = comp_classes[0]()
#             self.comps.append(comp_obj)
#
#     def valid_widget_inputs(self, inputs_info: list[dict]):
#         if not len(self.comps) > 0:
#             return []  # no error
#
#         comp = self.comps[0]  # comps are in same type, any one is ok to valid.
#         errors = []
#         for inputs in inputs_info:
#             error_list = comp.valid_widget_inputs(**inputs)
#             if error_list:
#                 errors.extend(error_list)
#         return errors
#
#     @property
#     def type(self):
#         return self.addon_type
#
#     @property
#     def widget_list(self):
#         result = []
#         for comp in self.comps:
#             result.append(comp.widgets)
#         return result
#
#     @property
#     def local_widgets_info(self):
#         result = {}
#         for comp in self.comps:
#             result = {
#                 **result,
#                 **comp.widgets_dict
#             }
#         result_array = []
#         for v in result.values():
#             result_array.append(v)
#         return result_array
#
#     @property
#     def widgets_info(self):
#         result = {}
#         for comp_class in self.comp_classes:
#             comp = comp_class()
#             result = {
#                 **result,
#                 **comp.widgets_dict
#             }
#         return result
#
#     @property
#     def widgets_info_in_list(self):
#         return list(self.widgets_info.values())
#
#     @property
#     def addon_info(self):
#         result = {
#             'addon_name': self.addon_type,
#             'display_name': self.display_name,
#             'comp_list': self.comp_list,
#             'can_turn_off': self.can_turn_off,
#             'comp_widgets': self.widgets_info_in_list,  # use this to tell frontend how to render
#             'widgets': [self.widgets_info_in_list]  # use this to get inputs from frontend
#         }
#         if self.can_turn_off:
#             result['is_off'] = True
#
#         return result
# class ValidException(Exception):
#     pass
#
# class Card(ABC):
#     name = None
#     display_name = None
#     meta_data = {}
#
#     def __init__(self, name=None, display_name=None, card_type=None, cache_out=True, valid_inputs=True):
#         """ Take this as the workflow in ComfyUI, but the creation is by Card author through coding
#             instead of Workflow authors, We believe it's more friendlly for end users to run an AI job
#             with cards, and also more efficient for Card authors to creat one and share to all.
#
#             Subclass should create and add comps, the order of comps to register matters.
#         """
#
#         if name:
#             self.name = name
#         if display_name:
#             self.display_name = display_name
#
#         self.card_type = card_type
#
#         self.cache_out = cache_out
#         self.valid_inputs = valid_inputs
#
#         self.comps = {}
#         self.addons = {}
#         self.support_addon_types = []
#
#         self.progress_callbacks = {}
#
#     @abstractmethod
#     def run(self, base_inputs: dict, addon_inputs: dict, valid_func_inputs: bool) -> any:
#         """ Subclass implement this to do the real work. """
#         pass
#
#     def __call__(self, base_inputs: dict, addon_inputs: dict = None, valid_func_inputs=False):
#         base_inputs = self.make_type_right(base_inputs)
#         errors = {}
#         input_errors = self.valid_widget_inputs(base_inputs)
#         if input_errors:
#             errors['inputs_valid_errors'] = input_errors
#
#         if addon_inputs:
#             create_addon_errors = self.create_addons_by_inputs(addon_inputs)
#             if create_addon_errors:
#                 errors['create_addon_errors'] = create_addon_errors
#
#         if errors:
#             raise ValidException(str(errors))
#
#         return self.run(base_inputs=base_inputs, addon_inputs=addon_inputs, valid_func_inputs=valid_func_inputs)
#
#     def create_addons_by_inputs(self, addon_inputs):
#         errors = []
#         for addon_type, inputs in addon_inputs.items():
#             addon_class = ADD_ON_CLASS_MAP.get(addon_type)
#             if not addon_class:
#                 errors.append('Addon type: {} not found.'.format(addon_type))
#                 continue
#             addon = addon_class.create_by_inputs(addon_type=addon_type, inputs_info=inputs)
#             self.addons[addon.type] = addon
#             inputs_valid_errors = addon.valid_widget_inputs(inputs)
#             if inputs_valid_errors:
#                 errors.extend(inputs_valid_errors)
#
#         return errors
#
#     def make_type_right(self, base_inputs):
#         for comp in self.comps.values():
#             base_inputs = comp.make_widget_inputs_type_right(base_inputs)
#         return base_inputs
#
#     def valid_addon_inputs(self, addon_inputs):
#         errors = []
#         for addon_type, inputs in addon_inputs.items():
#             addon = self.addons[addon_type]
#             if not addon:
#                 errors.append('Addon type: {} not found.'.format(addon_type))
#             error_list = addon.valid_widget_inputs(inputs)
#             if error_list:
#                 errors.extend(error_list)
#         return errors
#
#     def register_comp(self, comp: Comp):
#         self.comps[comp.name] = comp
#
#     def register_addon(self, addon_key: str, addon: Addon):
#         if not addon_key or not addon:
#             return
#
#         self.addons[addon_key] = addon
#
#     def init_supported_addons(self, addons: [AddonType]):
#         for addon in addons:
#             addon_class = ADD_ON_CLASS_MAP[addon]
#             self.register_addon(addon, addon_class())
#
#     @property
#     def widgets(self):
#         result = {}
#         for comp in self.comps.values():
#             result = {
#                 **result,
#                 **comp.widgets
#             }
#         return result
#
#     @property
#     def local_widgets_info(self):
#         result = {}
#         for comp in self.comps.values():
#             result = {
#                 **result,
#                 **comp.widgets_dict
#             }
#         return result
#
#     @property
#     def widgets_info_in_list(self):
#         """ dict in python has order, but javascript seems not, so we need it here. """
#         return list(self.local_widgets_info.values())
#
#     @property
#     def default_widget_values(self):
#         result = {}
#         for comp in self.comps.values():
#             result = {
#                 **result,
#                 **comp.widgets_value_info
#             }
#         return result
#
#     @property
#     def addon_infos(self):
#         result = {}
#         for key, addon in self.addons.items():
#             result[key] = addon.addon_info
#         return result
#
#     @property
#     def addons_info_in_list(self):
#         return list(self.addon_infos.values())
#
#     @property
#     def card_info(self):
#         return {
#             'card_name': self.name,
#             'card_display_name': self.display_name,
#             'widgets': self.widgets_info_in_list,
#             'addons': self.addons_info_in_list
#         }
#
#     @property
#     def card_inputs_info(self):
#         return {
#             'card_name': self.name,
#             'widget_values': self.default_widget_values,
#             'support_addon_types': self.support_addon_types,
#         }
#
#     def valid_widget_inputs(self, inputs_info: dict) -> list[str]:
#         """ Used to valid input values from frontend by calling the comp's valid_widget_inputs function.
#             Theoretically, inputs_info are all widgets inputs.
#         """
#         errors = []
#         param_names = list(self.local_widgets_info.keys())
#         for param_name, param_value in inputs_info.items():
#             param_widget = self.widgets.get(param_name)
#             if not param_widget:
#                 errors.append("Widget of param name: {} not found.".format(param_name))
#                 continue
#
#             if param_name in param_names:
#                 param_names.remove(param_name)
#             elif param_widget.optional and param_value is None:
#                 continue
#             else:
#                 errors.append("Card got unknown param name: {}".format(param_name))
#                 continue
#
#             valid_error = param_widget.valid_input(param_value)
#             if valid_error:
#                 errors.append(valid_error)
#         if param_names:
#             errors.append("Params: {} did not get value.".format(param_names))
#         return errors
#
#     def register_progress_callback(self, name, callback):
#         self.progress_callbacks[name] = callback
#
#     def get_progress_callback(self, name):
#         return self.progress_callbacks.get(name)
