from abc import ABC
from typing import Optional

from pydantic import BaseModel

from data_type.whatsai_card import PreModel, Prompt
from misc.logger import logger
from .addon import Addon
from .comp import Comp
from .func import Func, FuncOutput, FuncInput, Link, ParamPos
from ..addons import ADD_ON_CLASS_MAP
from ..funcs import Func_KSampler, Func_KSamplerAdvanced, Func_SamplerCustomAdvanced


class CardMetaData(BaseModel):
    name: str
    display_name: Optional[str] = None
    describe: Optional[str] = None
    pre_models: Optional[list[PreModel]] = None
    cover_image: Optional[str] = None


class Card(ABC):
    """ The card is exactly like a workflow in ComfyUI, the difference is you create the card with codes instead of
        graph from frontend.

        Why we need a card in front of the truth: ComfyUI does it so well already?
        It's really a big problem to answer, ha.

        I still wonder the whatsAI's value for now actually, but what I believe is what people hope to use is
        something easy. So opinion here is workflow in ComfyUI is not easy to use enough, no offense here at all,
        the fact is "No ComfyUI, No WhatsAI", but I really do something can help the area be better,
        and hoping I am right.

        Maybe the name of the project should be called CardUI instead of WhatsAI, I make the choice just for
        in memory of last project I failed before,
        and show respect WhatsApp have done: make a big influence among people with a pure engineer way.

        ComfyUI is the hero in this area, thanks for open source.

     """
    name: str
    meta_data: dict  # a dict can be parsed to CardMetaData

    def __init__(self):

        self.prompt: Prompt | None = None

        self.func_list: list[Func] = []
        """ Because Comp and Addon are Func, func_list includes all three types of them, don't take it as a narrow Func. """

        self._func_inputs: dict[str, list[FuncInput]] = {}
        self._func_outputs: dict[str, list[FuncOutput]] = {}
        self._links: list[Link] = []

        self.supported_addons: dict[str: Addon] = {}

        self.addon_positions = {}
        """ Decide where the addon locates in card, key: addon_name/addon_type, value: func/comp/addon name the addon after, 
        if value is a list, find the position from beginning to end, quit when found. """

        self.progress_callbacks = {}

    @property
    def support_addon_types(self):
        return list(self.supported_addons.keys())

    @property
    def func_names(self):
        return [func.name for func in self.func_list]

    @property
    def comps(self):
        _comps = []
        for func in self.func_list:
            if isinstance(func, Comp):
                _comps.append(func)
        return _comps

    @property
    def addons(self):
        addons_ = []
        for func in self.func_list:
            if isinstance(func, Addon):
                addons_.append(func)
        return addons_

    @property
    def widgets(self):
        """ The actual widgets of the card, no grouped widgets infos here, return param_name: widget object dict """

        result = {}
        for comp in self.comps:
            result = {**result, **comp.widgets}
        return result

    @property
    def widgets_info(self):
        """ The widgets info of the card, return a dict in type of param_name: widget_info """

        result = {}
        for comp in self.comps:
            result = {**result, **comp.widgets_info}
        return result

    @property
    def widgets_info_list(self):
        """ list version of widgets_info"""

        return list(self.widgets_info.values())

    @property
    def supported_addons_info(self):
        result = {}
        for key, addon in self.supported_addons.items():
            result[key] = addon.addon_info
        return result

    @property
    def links(self):
        return self._links

    @property
    def current_position(self):
        """ Get the position to put a Func/Comp/Addon. """

        return len(self.func_list)

    @property
    def card_info(self):
        return {
            'card_name': self.meta_data.get('name'),
            'card_display_name': self.meta_data.get('display_name'),
            'widgets': self.widgets_info_list,
            'addons': list(self.supported_addons_info.values())
        }

    def create_addons(self, addon_inputs):
        """ Create addons with the addon_inputs, make the data type right and return the updated addon_inputs,
            and validate the addon_inputs, if something wrong, return error in validation_errors.
        """
        validation_errors = []
        for addon_name, addon_input in addon_inputs.items():
            if not addon_name in self.support_addon_types:
                logger.debug(f"Addon: {addon_name} not found in supported addon types: {self.support_addon_types}")
                continue

            addon_execute_after = self.addon_positions.get(addon_name)
            assert addon_execute_after, \
                f"Config addon position of Addon: {addon_name} first, or whatsai will not know where to place the addon."

            addon = self.supported_addons.get(addon_name)

            if not addon_input:
                logger.debug(f"Empty addon input: {addon.name}")
                self.unlink_addon(addon)
                self.unregister_func(addon)
                continue

            if addon.is_switchable:
                addon.create_comps_with_inputs(addon_input)

            errors = addon.make_type_right_and_valid_inputs(addon_inputs)
            if errors:
                validation_errors.extend(errors)
                logger.debug(f"Addon: {addon.name} validation error: {errors}")
                continue

            after = self.find_position_of_func(addon_execute_after)
            if after is None:
                logger.debug(f"The func of {addon_execute_after} not found")
                continue

            self.unlink_addon(addon)
            self.unregister_func(addon)

            if not addon.is_switchable:
                addon.create_comps_with_inputs(addon_input)

            self.register_func_after(addon, after)
            self.relink_addon(addon)

        for registered_addon in self.addons:
            if registered_addon.name not in addon_inputs.keys():
                self.unlink_addon(registered_addon)
                self.unregister_func(registered_addon)

        return validation_errors

    def make_type_right_and_valid_inputs(self, inputs: dict):
        valid_errors = []

        for func in self.func_list:
            if not isinstance(func, Addon) and isinstance(func, Comp):
                _, errors = func.make_type_right_and_valid_inputs(inputs)
                if errors:
                    valid_errors.extend(errors)

        return valid_errors

    def get_func(self, func_name):
        for func in self.func_list:
            if func.name == func_name:
                return func
        return None

    def set_addon_positions(self, addon_positions: dict):
        self.addon_positions = addon_positions

    def set_prompt(self, prompt):
        """ Hold the prompt, then send to Func/Comp/Addon. """

        self.prompt = prompt
        for func in self.func_list:
            func.set_prompt(prompt)

    def find_position_of_func(self, name_or_names):
        """ Find position by func_name, name list supported. """

        if isinstance(name_or_names, list):
            for name_ in name_or_names:
                result = self._find_position_of_func(name_)
                if result is not None:
                    return result
        else:
            return self._find_position_of_func(name_or_names)

    def _find_position_of_func(self, name):
        """ Find position by single func_name. """

        for index, func_ in enumerate(self.func_list):
            if func_.name == name:
                return index
        return None

    def _add_func_inputs(self, func: Func):
        self._func_inputs[func.name] = func.inputs.values()

    def _add_func_outputs(self, func: Func):
        self._func_outputs[func.name] = func.outputs.values()

    def get_func_input(self, func_name, param_name):
        """ Get input of a Func with func_name and param_name. """

        func_inputs = self._func_inputs.get(func_name, [])
        for input_ in func_inputs:
            if input_.name == param_name:
                return input_
        return None

    def get_func_output(self, func_name, param_name):
        """ Get output of a Func with func_name and param_name. """

        func_outputs = self._func_outputs.get(func_name, [])
        for output in func_outputs:
            if output.name == param_name:
                return output
        return None

    def register_func(self, func):
        """ Put a func/comp/addon in func_list, take func_list as a flatten workflow in ComfyUI.
            Also deal with inputs/outputs/links thing.
            return the neat outputs, which do unpack work when output has only one element,
            avoiding codes below:

            >>> (a_output, ) = self.register_func()

        """
        func.set_position_in_card(self.current_position)

        self._add_func_inputs(func)
        self._add_func_outputs(func)

        self.func_list.append(func)

        if isinstance(func, Comp):
            self.add_links(func.links)

        return func.neat_outputs

    def register_func_after(self, func, after: int):
        """ Register a func after some index, a little stupid, but should work. """

        self.func_list.insert(after + 1, func)
        func.set_position_in_card(after + 1)
        func.set_prompt(self.prompt)

        for func_ in self.func_list[after + 2:]:
            func_.set_position_in_card(func_.position + 1)

        if isinstance(func, Comp):
            self.add_links(func.links)

        return func.neat_outputs

    def unregister_func(self, func):
        if func in self.func_list:
            index = self.func_list.index(func)
            self.func_list.remove(func)
            for func_ in self.func_list[index:]:
                func_.set_position_in_card(func_.position - 1)

    def link(self, output: FuncOutput, input_: FuncInput):
        """ Remember a link between one output and input. """

        assert isinstance(output, FuncOutput), f"output type: {type(output)} error."
        assert isinstance(input_, FuncInput), f"input_ type: {type(input_)} error "
        assert output.data_type == input_.data_type, \
            f"Link between output {output.data_type} put and input {input_.data_type} have different data type."

        link_ = Link.link(frm=output, to=input_)
        if link_ not in self._links:
            self._links.append(link_)

    def unlink(self, output: FuncOutput, input_: FuncInput):
        for link_ in self._links:
            if link_.frm == output and link_.to == input_:
                link_.unlink()
                self._links.remove(link_)
                break

    def add_links(self, links: list[Link]):
        """ Sync inner links of Comp/Addon, make sure card have all links to execute. """

        for link in links:
            if link not in self._links:
                self._links.append(link)

    def replace_output(self, origin: FuncOutput, replace: FuncOutput):
        """  Take over an origin output
            For example:
            After a Lora created, it will take over origin model and clip, the links
            follow outputs of them should be replaced by out model/clip of LoRA output.
         """

        origin_links = origin.links

        replaced_items = []
        for link in origin_links:
            replaced_items.append((origin, link.to))

            self._links.remove(link)
            origin_input = link.to
            link.unlink()
            self.link(replace, origin_input)

        return replaced_items

    def relink_addon(self, addon: Addon):
        """ Relink inputs/outputs of an addon, when an addon is added dynamically, it need
        to get it's inputs and make it's outputs to appropriate inputs.
        todo: maybe we need it works on common func.
        """

        inputs_to_link = addon.inputs_to_link
        for itl in inputs_to_link:
            output = self.get_func_output(itl.func_name, itl.func_output_name)
            if not output:
                logger.debug(f"Output of func: {itl.func_name} named: {itl.func_output_name} not found.")
                continue
            addon_input = addon.inputs.get(itl.addon_input_name)
            self.link(output, addon_input)

        outputs_to_replace = addon.outputs_to_replace
        for otr in outputs_to_replace:
            origin_output = self.get_func_output(otr.func_name, otr.func_output_name)
            if not origin_output:
                logger.debug(f"Output of func: {otr.func_name} named: {otr.func_output_name} not found.")
                continue
            addon_output = addon.outputs.get(otr.addon_output_name)

            replaced_items = self.replace_output(origin_output, addon_output)
            addon.replaced_items.extend(replaced_items)

    def unlink_addon(self, addon: Addon):
        """ Reverse process of relink_addon, take the addon out of card graph. """

        if addon not in self.func_list:
            return

        inputs_to_link = addon.inputs_to_link
        for itl in inputs_to_link:
            output = self.get_func_output(itl.func_name, itl.func_output_name)
            if not output:
                logger.debug(f"Output of func: {itl.func_name} named: {itl.func_output_name} not found.")
                continue
            addon_input = addon.inputs.get(itl.addon_input_name)
            self.unlink(output, addon_input)

        for output in addon.outputs.values():
            for link_ in output.links:
                self.unlink(link_.frm, link_.to)

        for replaced_item in addon.replaced_items:
            self.link(replaced_item[0], replaced_item[1])

        addon.replaced_items = []

    def get_func_successors(self, func: Func):

        def get_successor_funcs(func_: Func):
            successor_funcs = []

            linked_inputs = [link.to for output in func_.outputs.values() for link in output.links]
            func_indexes = [input_.pos.func_position for input_ in linked_inputs]
            linked_funcs = [self.func_list[idx] for idx in set(func_indexes)]

            if not linked_funcs:
                return []
            else:
                successor_funcs.extend(linked_funcs)
                for linked_func in linked_funcs:
                    successor_funcs.extend(get_successor_funcs(linked_func))

            return successor_funcs

        return list(set([func_.name for func_ in get_successor_funcs(func)]))

    def set_supported_addons(self, addon_names: [str]):
        """ Set supported addons of card, it will use default info of Addon, if you need custom them
            create the addon object yourself, then put the object in supported_addons, nothing different.
        """

        for addon_name in addon_names:
            addon_class = ADD_ON_CLASS_MAP[addon_name]
            if not addon_class:
                logger.error(f"Addon class: {addon_name} not found")
                continue

            self.supported_addons[addon_name] = addon_class()

    def add_supported_addon(self, addon: Addon):
        self.supported_addons[addon.name] = addon

    def flatten_funcs(self):
        funcs = []
        for func in self.func_list:
            if isinstance(func, Addon):
                _funcs = [func for comp in func.comp_list for func in comp.func_list]
                funcs.extend(_funcs)
            elif isinstance(func, Comp):
                funcs.extend(func.func_list)
            else:
                funcs.append(func)
        return funcs

    def map_pos_to_func_and_io_names(self, pos: ParamPos, is_output=True):
        """ Get func and corresponding IO name given pos. """

        func_pos = pos.func_position
        func_index = pos.func_index
        param_pos = pos.param_pos

        func = self.func_list[func_pos]
        func_name = func.name

        if isinstance(func, Comp):
            func = list(func.func_list)[func_index]

        if is_output:
            param_name = list(func.outputs.values())[param_pos].name
            return func_name, func_index, param_name
        else:
            param_name = list(func.inputs.values())[param_pos].name
            return func_name, func_index, param_name

    def get_ksampler_funcs(self):
        """ Get the kSampler func to preview. """

        k_samplers = []
        for func in self.flatten_funcs():
            if (isinstance(func, Func_KSampler)
                    or isinstance(func, Func_KSamplerAdvanced)
                    or isinstance(func, Func_SamplerCustomAdvanced)
            ):
                k_samplers.append(func)
        return k_samplers

    def print_debug_info(self):
        print("Func/Comp/Addon info:")
        for func in self.func_list:
            print(func)
        print("Link info:")
        for link in self._links:
            print(link)
