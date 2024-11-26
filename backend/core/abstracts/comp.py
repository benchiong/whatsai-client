from abc import abstractmethod

from .widget import Widget
from .func import Func

COMP_CLASS_MAP = {}
class Comp(Func):
    """ Comp, short for Compose or Component,
        when taking as Compose, means Compose of Widgets and Funcs
        when taking as Component, means Component of Card or Addon.
        All depends on your mood.
        It's designed like Node in ComfyUI, but with explicit widgets and supporting composition of funcs.
        Func, Comp should be treated as the smallest unit's of Card and Addon.
    """

    def __init__(self, name=None, display_name=None, cache_out=True, valid_inputs=True):
        """ Subclass should create and add widgets and funcs here, the order of widgets to register matters. """
        super().__init__(cache_out, valid_inputs)

        self._name = name
        self._display_name = display_name
        self._widgets: dict[str: Widget] = {}  # { param_name: widget }
        self.funcs: dict[str: Func] = {}  # { func_name, func }

        self._origin_to_new_param_name_map = {}
        self._current_to_origin_param_name_map = {}
        self.optional = False

        self.grouped_widgets = False  # if put all widgets in one GroupedWidgets widget.

    def set_optional(self, optional):
        self.optional = optional
        for widget in self._widgets.values():
            widget.set_optional(optional)

    def set_group_widgets(self, grouped_widgets):
        self.grouped_widgets = grouped_widgets

    @abstractmethod
    def run(self, **kwargs):
        """ Notice: We *force* parameters to keyword args for easier use.
        """
        pass

    def __call__(self, **kwargs):
        origin_kwargs = self.restore_origin_param_name(**kwargs)
        # self.make_widget_inputs_type_right(**origin_kwargs)
        return self.run(**origin_kwargs)

    @property
    def name(self):
        return self._name if self._name else self.__class__.__name__

    @property
    def display_name(self):
        return self._display_name if self._display_name else self.name

    @property
    def widgets(self):
        _widgets = {}
        for param_name, widget in self._widgets.items():
            mapped_param_name = self._origin_to_new_param_name_map.get(param_name)
            if mapped_param_name:
                _widgets[mapped_param_name] = widget
            else:
                _widgets[param_name] = widget
        return _widgets

    @property
    def widgets_dict(self):
        """ Used to tell frontend how to render UI by backend. """
        result = {}
        for param_name, widget in self.widgets.items():
            mapped_param_name = self._origin_to_new_param_name_map.get(param_name)
            if mapped_param_name:
                result[mapped_param_name] = widget.dict
            else:
                result[param_name] = widget.dict
        return result

    @property
    def widgets_dict_grouped_widgets_considered(self):
        """ Grouped Widgets is added here.
         When a comp's grouped_widgets is set True, the _widgets is as same as before,
         but call this method will make all it's _widgets in a grouped widget, so frontend get the grouped widgets
         and render.
         When frontend submits inputs to validate and generate, server.router.card_info_to_prompt
         do the unpack work, then following processing can work without knowing the grouped widgets,
         so it's transparent to them.
         issue: not sure if it's appropriate to put it here in abstract layer.
        """
        result = {}
        for param_name, widget in self.widgets.items():
            mapped_param_name = self._origin_to_new_param_name_map.get(param_name)
            if mapped_param_name:
                result[mapped_param_name] = widget.dict
            else:
                result[param_name] = widget.dict
        if self.grouped_widgets:
            return {
                self.display_name: {
                    'display_name': self.display_name,
                    'widget_type': 'GroupedWidgets',
                    'value': list(result.values())
                }
            }
        else:
            return result

    @property
    def widgets_value_info(self):
        """ Used to tell the values of widgets. """
        result = {}
        for param_name, widget in self.widgets.items():
            if widget.default_value_info:
                result = {
                    **result,
                    **widget.default_value_info
                }
            else:
                result[param_name] = widget.value
        return result

    def register_widget(self, widget: Widget):
        self._widgets[widget.param_name] = widget

    def register_func(self, func: Func):
        self.funcs[func.name] = func

    def make_widget_inputs_type_right(self, kwargs):
        for param_name, param_value in kwargs.items():
            widget = self.widgets.get(param_name)
            if widget:
                kwargs[param_name] = widget.make_type_right(param_value)
        return kwargs

    def valid_widget_inputs(self, **kwargs) -> list[str]:
        """ Used to valid input values from frontend by calling the widget's valid_input function.
            Notice: Call it after param map if needed.
            :return: errors list, return empty list if success.
        """
        errors = []
        widget_param_names = list(self.widgets.keys())
        for param_name, param_value in kwargs.items():
            widget = self.widgets.get(param_name)
            if not widget:
                continue
            error = widget.valid_input(param_value)
            if error:
                errors.append(error)
            widget_param_names.remove(param_name)

        if widget_param_names:
            errors.append("Params from widget: {} did not get value.".format(widget_param_names))

        return errors

    def map_param_name(self, origin_param_name, new_param_name):
        """ We need this when the upstream(Card/Addon) want a different param name, especially they have
            multiple comps in one type to distinguish parameters.
        """
        assert origin_param_name in self.widgets.keys(), (
            'Param name: {} not in widget param names. '.format(origin_param_name))
        self._origin_to_new_param_name_map[origin_param_name] = new_param_name
        self._current_to_origin_param_name_map[new_param_name] = origin_param_name
        for widget in self._widgets.values():
            if widget.param_name == origin_param_name:
                widget.map_param_name(origin_param_name, new_param_name)
                break

    def map_all_param_names_with_prefix(self, prefix):
        for widget in self._widgets.values():
            origin_param_name = widget.param_name
            mapped_param_name = prefix + origin_param_name

            widget.map_param_name(origin_param_name, mapped_param_name)
            self._origin_to_new_param_name_map[origin_param_name] = mapped_param_name
            self._current_to_origin_param_name_map[mapped_param_name] = origin_param_name

    def restore_origin_param_name(self, **kwargs):
        for current_param_name, param_value in kwargs.items():
            if current_param_name in self._current_to_origin_param_name_map:
                origin_param_name = self._current_to_origin_param_name_map[current_param_name]
                kwargs[origin_param_name] = param_value
                kwargs.pop(current_param_name)
        return kwargs

