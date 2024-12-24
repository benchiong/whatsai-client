from misc.logger import logger
from .cache import OutputsCache
from .widget import Widget
from .func import Func, FuncPos, Link, FuncOutput, FuncInput


class Comp(Func):
    """ Comp, short for Compose or Component,
        when taking as Compose, means Compose of Widgets and Funcs
        when taking as Component, means Component of Card or Addon.
        All depends on your mood.
        It's designed like Node in ComfyUI, but with explicit widgets and supporting composition of funcs.
        Func, Comp should be treated as the smallest unit's of Card and Addon.
    """

    def __init__(self, name=None, display_name=None, optional=False, grouped_widgets=False):
        """ Subclass should create and add widgets and funcs here, the order of widgets to register matters. """

        super().__init__(name)

        self.display_name = display_name

        self._widgets: dict[str: Widget] = {}
        """ Notice: the key of _widgets is for inner use only, use param_name in widget to make sure high level uniqueness. """

        self.func_list: list[Func] = []
        """ A Comp can hold multiple Funcs, if you do that, remember to map Inputs and Outputs of Funcs and Comp,
            and connect the inner Inputs and Outputs manually, turn register_func's share_io off.
        """

        self.optional = optional
        """ The value will influence frontend, e.g. decide a model can be set to null,
            and the value validation.
        """

        self.grouped_widgets = grouped_widgets
        """ Put all widgets in one GroupedWidgets widget or not, used for frontend to collapse a comp has 
            a lots of widgets, a brain friendly thing.
        """

        self._links: list[Link] = []
        """ Inner links of comp, happened before registered to a card, 
        copy them to Card when registered. 
        """

        self.cached_outputs = OutputsCache()

        # todo?: when the comp is optional, design a mechanism to make it work with its backup outputs,
        #  or keep using addon as the Option solver

    @property
    def func_inputs(self):
        return {name: _input for name, _input in self._inputs.items() if _input.is_from_func}

    @property
    def widgets(self):
        """ Widgets of the comp, grouped_widgets is not considered here, use widgets_info instead. """
        return {widget.param_name: widget for widget in self._widgets.values()}

    @property
    def links(self):
        return self._links

    @property
    def widgets_info(self):
        """ Used to tell frontend how to render UI by backend. Dealing with grouped_widgets logic here. """

        result = {}
        for widget in self._widgets.values():
            result[widget.param_name] = widget.info

        if self.grouped_widgets:
            return {
                self.display_name: {
                    'display_name': self.display_name,
                    'widget_type': 'GroupedWidgets',
                    'value': list(result.values())
                }
            }
        return result

    def set_prompt(self, prompt):
        self.prompt = prompt
        for func in self.func_list:
            func.set_prompt(prompt)

    def set_position_in_card(self, position):
        """ A comp can hold funcs, which Func do not, so do it after it's origin manner. """
        super().set_position_in_card(position)
        for func in self.func_list:
            func.set_position_in_card(position)

    def set_optional(self, optional):
        """ It will affect the interaction behavior on the frontend and value validation,
            sync it with widgets, who do the validation work.
         """
        self.optional = optional
        for widget in self._widgets.values():
            widget.set_optional(optional)

    def set_group_widgets(self, grouped_widgets):
        """ Set the widgets of comp grouped, frontend will pack it. """
        self.grouped_widgets = grouped_widgets

    def change_param_name_and_display_name(self, origin_param, param_name, display_name=None):
        """ Sometimes you need to change the param_name, display_name of widgets of comp, use this.
            origin_param is unchanged since the comp created, so use it as an index, comp's widgets_info
            will use widgets' param_name instead of origin_param.
        """
        widget = self._widgets[origin_param]
        if widget:
            widget.param_name = param_name
            if display_name:
                widget.display_name = display_name
            self._widgets[origin_param] = widget

        input_ = self._inputs[origin_param]
        if input_:
            input_.mapped_name = param_name

    def set_widget_param_names_prefix(self, prefix):
        """ Set all param_name of widgets with a common prefix """
        for widget in self._widgets.values():
            widget.param_name = str(prefix) + widget.param_name

        for input_ in self._inputs.values():
            input_.mapped_name = str(prefix) + input_.name

    def set_widget_param_names_suffix(self, suffix):
        """ Set all param_name of widgets with a common suffix """
        for widget in self._widgets.values():
            widget.param_name = widget.param_name + str(suffix)

        for input_ in self._inputs.values():
            input_.mapped_name = input_.name + str(suffix)

    def restore_all_param_names(self):
        """ clear all param_name set thing. """
        for name, widget in self._widgets.items():
            widget.param_name = name

    def register_widget(self, widget):
        """ Add a widget to comp, do when comp init, make sure it's after the Func which the widget's param belongs. """

        assert widget.param_name in self._inputs.keys(), f"Widget's param_name: {widget.param_name} not found in inputs, register func first, or make sure widget's param_name is exactly same as param of the Func."

        self._widgets[widget.param_name] = widget
        self._inputs[widget.param_name].source = 'widget'

    def register_func(self, func: Func, share_io=True):
        """ Register a func in comp, share_io means the comp share inputs and outputs with the func,
            it is most situation when comp has only one func, you should set it False when comp has
            multiple Funcs.

            Warning: if you have multiple funcs, the inner func should not touch other inputs from outside,
            it's a very basic rule whatsAI rely on, otherwise the system will crash.
        """

        if share_io:
            self.share_io(func)

        """ Func_index default to 0, got actual value when registered to a Comp. """
        func_index = len(self.func_list)
        func.set_index_in_comp(func_index)

        for output in func.outputs.values():
            output.set_func_index(func_index)

        for input_ in func.inputs.values():
            input_.set_func_index(func_index)

        self.func_list.append(func)

    def link(self, output: FuncOutput, input_: FuncInput):
        """ Remember a link between one output and input. """

        assert isinstance(output, FuncOutput), f"output type: {type(output)} error."
        assert isinstance(input_, FuncInput), f"input_ type: {type(input_)} error "
        assert output.data_type == input_.data_type, \
            f"Link between output {output.data_type} put and input {input_.data_type} have different data type."

        link_ = Link.link(frm=output, to=input_)
        if link_ not in self._links:
            self._links.append(link_)

    def can_link_to_self(self, strict=True):
        """ If a comp can link to self or siblings, it must have same func inputs with outputs.
        e.g. a lora/controlnet follow this rule, not sure if every a comp like them have this feature,
        let's find out.
        """

        func_inputs = self.func_inputs.values()
        outputs = self.outputs.values()

        if len(func_inputs) != len(outputs):
            return False

        for _input, output in zip(func_inputs, outputs):
            if strict:
                is_same = (_input.data_type == output.data_type and _input.name == output.name)
            else:
                is_same = _input.data_type == output.data_type
            if not is_same:
                return False

        return True

    def link_to_sibling(self, pre_sibling: Func):
        """ Useful when created Addon dynamically,  some addon are created base on user inputs,
            You don't know how many comp the Addon will have until got user's addon_inputs,
            take LoRA as an example.
            Create inner links of the Comp/Addon, return the links.
        """
        assert self.can_link_to_self()

        links = []
        for index, (input_, output) in enumerate(zip(self.func_inputs.values(), pre_sibling.outputs.values())):
            link = Link.link(frm=output, to=input_)
            links.append(link)

        return links

    def add_links(self, links: list[Link]):
        for link in links:
            if link not in self._links:
                self._links.append(link)

    def make_type_right_and_valid_inputs(self, inputs: dict) -> (dict, list[str]):
        """ Used to valid input values from frontend by calling the widget's valid_input function.
            :return: errors list, return empty list if success.
        """
        errors = []

        widget_param_names = list(self.widgets.keys())
        for param_name, param_value in inputs.items():
            widget = self.widgets.get(param_name)
            if not widget:
                continue

            inputs[param_name] = widget.make_type_right(param_value)
            error = widget.valid_input(param_value)
            if error:
                errors.append(error)
            widget_param_names.remove(param_name)

        if widget_param_names:
            errors.append(f"Params from {str(self)}: {widget_param_names} did not get value")

        # Is it necessary to return the inputs?
        return inputs, errors

    def execute(self, inputs: dict, cached_outputs: OutputsCache, card, func_name):
        for index, func in enumerate(self.func_list):
            is_first = index == 0
            is_last = index == len(self.func_list) - 1

            if is_first:
                func_outputs = func.execute(inputs, cached_outputs, card, func_name)
                self.cached_outputs.sync_cache(cached_outputs)
            else:
                func_outputs = func.execute(inputs, self.cached_outputs, card, func_name)

            self.cached_outputs.cache_func_outputs(func_name, index, func_outputs)

            if is_last:
                self.cached_outputs.clear_all()
                cached_outputs.cache_func_outputs(func_name, index, func_outputs)
                return func_outputs

    @classmethod
    def widgets_info_of_comps(cls, comps):
        return {**{key: value for comp in comps for key, value in comp.widgets_info.items()}}


class SwitchableComp(Comp):
    def __init__(self, name=None, display_name=None, optional=True):
        super().__init__(name=name, display_name=display_name, optional=optional, grouped_widgets=False)

        self.comps: dict[str: Comp] = {}
        self.selected_comp_name = None

    def set_comps(self, comp_list: list[Comp]):
        # todo: make sure outputs of each comp be same?
        for comp in comp_list:
            self.comps[comp.name] = comp

    def select_comp(self, comp_name):
        self.selected_comp_name = comp_name
        selected_comp = self.comps.get(comp_name)
        if selected_comp:
            self._widgets = selected_comp._widgets
            self.func_list = selected_comp.func_list
            self.share_io(selected_comp)
            return selected_comp
        return None

    @property
    def widgets_info(self):
        assert self.name, "SwitchableComp's name must exists and be unique like widget's param_name."

        widgets_info = {}
        widgets_info_with_selected = {}

        for comp in self.comps.values():
            widgets_list_info = list(comp.widgets_info.values())
            widgets_info[comp.display_name] = widgets_list_info
            widgets_info_with_selected[comp.display_name] = {
                'selected': comp.display_name == self.selected_comp_name,
                'widgets': widgets_list_info
            }

        return {
            self.display_name: {
                'param_name': self.name,
                'display_name': self.display_name,
                'widget_type': 'SwitchableWidgets',
                'value': widgets_info_with_selected,
                'values': widgets_info
            }
        }

    def make_type_right_and_valid_inputs(self, inputs: dict):
        selected_comp_name = inputs.get(self.name)
        if selected_comp_name:
            selected_comp = self.select_comp(comp_name=selected_comp_name)
            if selected_comp:
                return selected_comp.make_type_right_and_valid_inputs(inputs)
        else:
            return inputs, []
