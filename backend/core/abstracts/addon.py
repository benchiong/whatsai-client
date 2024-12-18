from abc import abstractmethod
from typing import Type

from core.abstracts.cache import OutputsCache
from core.abstracts.comp import Comp


class AddonInputToLink:
    """ When an Addon is created dynamically, it's after the card graph creation,
        at that time, it must be told where got its inputs from card.

        addon_input_name: the input_name of the addon to link
        func_name: Func/Comp/Addon name of the addon neet to get output from.
        func_output_name: Which output of Func/Comp/Addon to get out from.
    """

    def __init__(self, addon_input_name: str, func_name: str, func_output_name: str):
        self.addon_input_name = addon_input_name
        self.func_name = func_name
        self.func_output_name = func_output_name


class AddonOutputToReplace:
    """ When an Addon is created dynamically, it's after the card graph creation,
        at that time, it must be told which output the card holds will be replaced by it.
        And it will take over all links the output holds then.
        todo: support lock a link don't wish to be taken over.

        func_name: Func/Comp/Addon name of the addon neet to get output from.
        func_output_name: Which output of Func/Comp/Addon to replace.
        addon_output_name: the output_name of the addon to replace the output in card.
    """

    def __init__(self, func_name: str, func_output_name: str, addon_output_name: str):
        self.func_name = func_name
        self.func_output_name = func_output_name
        self.addon_output_name = addon_output_name


class Addon(Comp):
    """ An Addon is designed in this purpose: a card(workflow in ComfyUI) can be very information heavy,
        some unit of it can be optional, a LoRA is a classic example, but it's a common thing in this area.
        Addon comes here to make the main card simple, and put addon on side, when people want it, go there,
        leave if unnoticed otherwise.
        Because it's decide by people who use it, so we don't know how many funcs/comps we should have until
        people tell us, so it's dynamically creation, and with some different with other parts of WhatsAI.
    """
    addon_type = None

    def __init__(self, name, display_name, can_user_add_new=False, can_turn_off=False):
        super().__init__(name)
        """ The name should exactly same as addon_type. """

        self.display_name = display_name

        # todo: consider other situation of scalability?.
        self.can_user_add_new = can_user_add_new
        """ If True, it says this addon can be add new comp instance by front user, 
        for example, user can add multiple LoRAs, the number is decided by user,
        If False, only one single comp needed.
        """

        self.can_turn_off = can_turn_off
        """ Some addon need to turn off explicitly, e.g. HiresAddon """

        self.comp_class: Type[Comp] | None = None
        """ The class of comp to create comp list of addon when can_user_add_new is True, 
            
            *Notice*: only one comp_class is supported yet, if you have multiple comps in comp unit, 
            try to compose them in one Comp for now.
        """

        self.comp_list: list[Comp] = []

        self.init_comp_unit_or_comp_list()

        self.inputs_to_link: list[AddonInputToLink] = []
        self.outputs_to_replace: list[AddonOutputToReplace] = []
        self.replaced_items = []

        self.cache = {}
        """ An inner cache of Addon, because multiple Funcs are addon's inner logic, so the cache should 
            managed by Addon itself. e.g. loras loader's cache should not be exposed to upstream.
        """

    @abstractmethod
    def init_comp_unit_or_comp_list(self):
        """ Every subclass should implement this method to make sure card can do the following work to put
            the addon in graph:
            if people can't add new comp, take vae as an example, the comp_list should be ready;
            if people can add new comp with Comp_unit, then Comp_unit should be ready then, take LoRA as an example.

            Do the comp link thing in comps unit thing here if you have multiple comps when can_user_add_new is True.
        """
        pass

    def create_comps_with_inputs(self, inputs: list[dict]):
        """ Create comps_list when got addon inputs from frontend. """

        if self.can_user_add_new:
            self.func_list = []
            self.comp_list = []  # todo: deal with memory clear and reuse thing.

            prev_comp = None
            inputs_length = len(inputs)
            self._links = []

            for i in range(inputs_length):
                comp = self.comp_class()
                if i == 0:  # the first comp
                    self.share_inputs(comp)
                if i == inputs_length - 1:  # the last comp
                    self.share_outputs(comp)
                if prev_comp:
                    links = comp.link_to_sibling(prev_comp)
                    self.add_links(links)

                self.register_comp(comp)
                prev_comp = comp
        else:
            pass
            """ It should be initialized in init_comp_unit_or_comp_list. """

    def set_prompt(self, prompt):
        self.prompt = prompt
        for comp in self.comp_list:
            comp.set_prompt(prompt)

    def set_position_in_card(self, position):
        """ Addon can hold comps, comp can't for now, so it need share the position with comps it holds,
            todo: if Comp supports holding comps, clear this method then.
        """
        super().set_position_in_card(position)
        for comp in self.comp_list:
            comp.set_position_in_card(position)

    def set_inputs_to_link(self, *inputs_to_link: AddonInputToLink):
        """ Tell card where to link its inputs after it is created. """
        self.inputs_to_link = []
        for input_to_link in inputs_to_link:
            self.inputs_to_link.append(input_to_link)

    def set_outputs_to_replace(self, *outputs_to_replace: AddonOutputToReplace):
        """ Tell card which outputs to take over after it is created. """
        self.outputs_to_replace = []
        for out_put_to_replace in outputs_to_replace:
            self.outputs_to_replace.append(out_put_to_replace)

    def register_comp(self, comp: Comp):
        """ Register a Comp, do the IO share thing manually, most time it's the situation,
            If you have one Comp in Addon, and the Comp have one Func, share IO should be alright,
            remember to do it yourself.
        """
        self.comp_list.append(comp)

        for func in comp.func_list:
            self.register_func(func, share_io=False)

    def make_type_right_and_valid_inputs(self, addon_inputs: dict):
        inputs_list = addon_inputs.get(self.addon_type)
        if not inputs_list:
            return

        valid_errors = []
        if self.can_user_add_new:
            comp = self.comp_class()
            for i, inputs in enumerate(inputs_list):
                updated_inputs, errors = comp.make_type_right_and_valid_inputs(inputs)
                inputs_list[i] = updated_inputs
                if errors:
                    valid_errors.extend(errors)
        else:
            inputs = inputs_list[0]
            """ There should be only on element in inputs_list when can_user_add_new is False """

            for comp in self.comp_list:
                updated_inputs, errors = comp.make_type_right_and_valid_inputs(inputs)
                inputs = {**inputs, **updated_inputs}
                if errors:
                    valid_errors.extend(errors)

            inputs_list[0] = inputs

        addon_inputs[self.addon_type] = inputs_list
        return valid_errors

    @property
    def widgets_info(self):
        if self.can_user_add_new:
            return self.comp_class().widgets_info
        else:
            return Comp.widgets_info_of_comps(self.comp_list)

    @property
    def widgets_info_in_list(self):
        return list(self.widgets_info.values())

    def execute(self, addon_inputs: dict, cached_outputs: OutputsCache, card, func_name):
        this_addon_inputs = addon_inputs.get(self.name)

        for index, (comp, inputs) in enumerate(zip(self.comp_list, this_addon_inputs)):
            is_first = index == 0
            is_last = index == len(self.comp_list) - 1
            if is_first:
                comp_outputs = comp.execute(inputs, cached_outputs, card, func_name)
            else:
                comp_outputs = comp.execute(inputs, self.cached_outputs, card, func_name)

            func_count_per_comp = len(comp.func_list)

            # here we use the fact, the last func of comp hold the outputs of comp
            output_func_index = (index + 1) * func_count_per_comp - 1
            self.cached_outputs.cache_func_outputs(self.name, output_func_index, comp_outputs)

            if is_last:
                self.cached_outputs.clear_all()
                cached_outputs.cache_func_outputs(self.name, index, comp_outputs)
                return comp_outputs

    @property
    def addon_info(self):
        return {
            'addon_name': self.name,
            'display_name': self.display_name,
            'comp_list': self.can_user_add_new,
            'can_turn_off': self.can_turn_off,
            'comp_widgets': self.widgets_info_in_list,  # use this to tell frontend how to render new.
            'widgets': [self.widgets_info_in_list],  # use this to get inputs from frontend.
            'is_off': True if self.can_turn_off else None
        }
