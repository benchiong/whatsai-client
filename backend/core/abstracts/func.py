from abc import ABC, abstractmethod
from typing import Literal

from box import Box

from core.abstracts.cache import OutputsCache
from data_type.whatsai_card import Prompt
from misc.logger import logger

# todo: add param optional support?

InputSource = Literal['widget', 'func']
""" Input Source of a func param, widget means it comes from use input, other func otherwise. """


class FuncPos:
    """ Two dimension position, one for where it locates in cards, and the other is the index of the position,
        Then we can register a Comp or Addon with multiple Funcs in one slot of Card without losing the accurate
        location.
    """

    def __init__(self):
        self.position: int | None = None
        """ Func/Comp/Addon locates in Card. """

        self.index: int = 0
        """ Func locates in Comp or Addon, it's 0 if a Func hold it. """

    def __repr__(self):
        return f"Func pos: _{self.position}_ |{self.index}|)"

    def __eq__(self, other):
        return self.position == other.position and self.index == other.index


class ParamPos:
    """ A Fun's param position, position of the Func in Card and position of param of the func consist of it.
        It's three dimension.
     """

    def __init__(self):
        self.func_pos: FuncPos = FuncPos()
        self.param_pos = 0
        """ Param position in a Func/Comp/Addon, used to locate an Input or an Output. """

    @property
    def func_position(self):
        return self.func_pos.position

    @property
    def func_index(self):
        return self.func_pos.index

    def __repr__(self):
        return f"(_{self.func_position}_,|{self.func_index}|,-{self.param_pos}-)"

    def __eq__(self, other):
        return self.func_pos == other.func_pos and self.param_pos == other.param_pos


class IOInfo:
    """ Simple info of Input/Output to create the Input/Object, just for easy using. """

    def __init__(self, name, data_type):
        self.name: str = name
        self.data_type: str = data_type


class FuncIO:
    """ The abstract of FuncInput and FuncOutput."""

    def __init__(self, name: str, data_type: str):
        self.name = name
        """ Name of the Input/Output, can be used as an index key. """

        self.mapped_name = name
        """ The upstream change param name to solve multiple same Func in one parent. """

        self.data_type = data_type
        """ Data type of IO, it strictly follow ComfyUI's Datatypes
            https://docs.comfy.org/essentials/custom_node_datatypes#datatypes
        """

        self.pos = ParamPos()

    @classmethod
    def from_param(cls, param: IOInfo):
        """ This method can make the creation of FuncInput/FuncOutput a bit easier when we manually create them. """
        return cls(name=param.name, data_type=param.data_type)

    def set_func_position(self, func_position):
        """ Set the func position in Card. """
        self.pos.func_pos.position = func_position

    def set_func_index(self, func_index):
        """ Set the func index in a Comp or Addon. """
        self.pos.func_pos.index = func_index

    def set_param_pos(self, param_pos):
        """ Set the param position of func. """
        self.pos.param_pos = param_pos


class Link:
    """ Take this as the link between Nodes in ComfyUI, we create it manully. """

    def __init__(self, frm: 'FuncOutput', to: 'FuncInput'):
        assert isinstance(frm, FuncOutput), f"Link must start from a func output, got {frm}."
        assert isinstance(to, FuncInput), f"Link must end with a func output, got {to}."

        self.frm = frm
        self.to = to

    @classmethod
    def link(cls, frm: 'FuncOutput', to: 'FuncInput'):
        """ Make a link of frm and to, update the link to frm and to, then return the link. """
        link = cls(frm=frm, to=to)
        to.set_link(link)
        frm.add_link(link)
        return link

    def unlink(self):
        """ Clear the link store in input and output. """
        self.frm.remove_link(self)
        self.to.link = None

    def __repr__(self):
        return f"Link: {self.frm} -- {self.to}"

    def __eq__(self, other):
        return self.frm == other.frm and self.to == other.to


class FuncInput(FuncIO):
    def __init__(self, name, data_type, source: InputSource = 'func'):
        super().__init__(name, data_type)

        self.source = source
        """ Set source default to 'func', when comp add a widget to it, change it to 'widget'. """

        self.link: Link | None = None

    def set_link(self, link: Link):
        self.link = link

    @property
    def is_from_widget(self):
        return self.source == 'widget'

    @property
    def is_from_func(self):
        return not self.is_from_widget

    def __repr__(self):
        if self.is_from_widget:
            return f"Widget input: [{self.name}], type: {self.data_type}, @{self.pos}."
        else:
            return f"Func input: [{self.name}], type: {self.data_type}, @{self.pos}."


class FuncOutput(FuncIO):
    def __init__(self, name, data_type):
        super().__init__(name, data_type)

        self.links: list[Link] = []

    def add_link(self, link: Link):
        if link not in self.links:
            self.links.append(link)

    def remove_link(self, link: Link):
        self.links.remove(link)

    def __repr__(self):
        return f"Func Output: [{self.name}], type: {self.data_type}, @{self.pos}"


class Func(ABC):
    def __init__(self, name=None):
        self.name = name

        self.position = None
        """ The position of the Func or Comp in Card. """

        self.index = 0
        """ The index of the Func in Comp or Addon, it is 0 if it's a func. """

        self._inputs: Box = Box()
        self._outputs: Box = Box()
        """ Use Box just for dot access: SomeFunc.inputs.some_param_name for easy use. """

        self.prompt: Prompt | None = None

    @property
    def inputs(self):
        return self._inputs

    @property
    def input_names(self):
        return self._inputs.keys()

    @property
    def I(self):
        """ Just simple access to self.inputs. """
        return self._inputs

    @property
    def outputs(self):
        return self._outputs

    @property
    def output_names(self):
        return self._outputs.keys()

    @property
    def neat_outputs(self):
        output_values = list(self._outputs.values())
        if len(output_values) == 1:
            return output_values[0]
        return output_values

    @property
    def O(self):
        """ Just simple access to self.outputs. """
        return self._outputs

    def set_inputs(self, *input_params: IOInfo):
        """ Used when a Func is created, with Output, Input are very important concept in whatsAI,
        input is where link points to, and then card will be executed following links, as ComfyUI's graph.

        demo:
        >>> self.set_inputs(
        >>>      IOInfo(name='checkpoint_id', data_type='STRING')
        >>>  )

        the codes should be put in Func.__init__() method, define what inputs the Func have
        """
        for index, input_param in enumerate(input_params):
            func_input = FuncInput.from_param(input_param)
            func_input.set_param_pos(index)
            self._inputs[input_param.name] = func_input

    def set_inputs_with_dict(self, inputs: dict):
        self._inputs = Box(inputs)

    def set_outputs(self, *output_params: IOInfo):
        """ Used when a Func is created, with Input, Output are very important concept in whatsAI,
        out is where link starts, and then card will be executed following links, as ComfyUI's graph.

        >>> self.set_outputs(
        >>>    IOInfo(name='model', data_type='MODEL'),
        >>>    IOInfo(name='clip', data_type='CLIP'),
        >>>    IOInfo(name='vae', data_type='VAE'),
        >>> )

                the codes should be put in Func.__init__() method, define what outputs the Func have
        """
        for index, output_param in enumerate(output_params):
            func_output = FuncOutput.from_param(output_param)
            func_output.set_param_pos(index)
            self._outputs[func_output.name] = func_output

    def set_outputs_with_dict(self, outputs: dict):
        self._outputs = Box(outputs)

    def set_position_in_card(self, position):
        """ Set the position of the Func in card, happens when it is registered to card.
        It also set the position of its outputs.
        """

        self.position = position
        for out in self._outputs.values():
            out.set_func_position(position)

        for input_ in self._inputs.values():
            input_.set_func_position(position)

    def set_index_in_comp(self, index):
        """ Set the index of the Func in Comp/Addon. """

        self.index = index
        for out in self._outputs.values():
            out.pos.func_pos.index = index

        for input_ in self._inputs.values():
            input_.pos.func_pos.index = index

    def set_prompt(self, prompt):
        """ Every Func/Comp/Addon holds the prompt, like ComfyUI's hidden input. """
        self.prompt = prompt

    def set_input_name(self, origin_name, name):
        """ origin_name is set when the Func defined,
        you can change the name in input and the origin_name as the key to index.
        """
        _input = self._inputs[origin_name]
        _input.name = name
        self._inputs[origin_name] = _input

    def share_io(self, other_func):
        """ Shallow copy of inputs and outputs, so the func shares the same inputs/outputs with the other_func,
            If one changes, other will follow.
        """

        assert isinstance(other_func.inputs, Box), f"Type of inputs of other func: {other_func} must be Box"
        assert isinstance(other_func.outputs, Box), f"Type of outputs of other func: {other_func} must be Box"

        self._inputs = other_func.inputs
        self._outputs = other_func.outputs

    def share_inputs(self, other_func):
        """ Shallow copy of inputs. """

        assert isinstance(other_func.inputs, Box), f"Type of inputs of other func: {other_func} must be Box"
        self._inputs = other_func.inputs

    def share_outputs(self, other_func):
        """ Shallow copy of outputs. """

        assert isinstance(other_func.outputs, Box), f"Type of outputs of other func: {other_func} must be Box"
        self._outputs = other_func.outputs

    def get_func_inputs(self, inputs: dict, cached_outputs: OutputsCache, card):
        input_values = {}
        for name, input_ in self._inputs.items():
            if input_.is_from_widget:
                input_value = inputs.get(input_.mapped_name)
                input_values[input_.name] = input_value
            else:
                frm_pos = input_.link.frm.pos
                func_name, func_idx, param_name = card.map_pos_to_func_and_io_names(pos=frm_pos, is_output=True)
                logger.debug(f"{func_name} {func_idx} {param_name} {cached_outputs}")
                input_value = cached_outputs.get_param_output(func_name, func_idx, param_name)
                assert input_value is not None, f"Input value of {func_name}:{param_name} must be ready here."
                input_values[input_.name] = input_value

        return input_values

    def transform_outputs(self, executed_outputs):
        """ Transform executed outputs to key/value can be cached. """

        assert len(self.outputs) == len(executed_outputs)

        func_outputs = {}
        for (output, executed_output) in zip(self.outputs.values(), executed_outputs):
            func_outputs[output.name] = executed_output

        return func_outputs

    def execute(self, inputs: dict, cached_outputs: OutputsCache, card, func_name):
        """ :param inputs: the inputs from user, can be got by Comp's widget param name, can also be the addon's
            inputs but mapped to the inputs' structure;
            :param cached_outputs: the outputs of upstream funcs, can be Comp/Addon inner cache aside with card's
            cache;
            :param card: the card executing, we need it because we need the graph it holds and get responding output's
            func_name, func_index, param_name through output's position;
            :param func_name: the Func/Comp/Addon is executing, we need it because when an Addon has Comp, the Comp lose
            the info of Addon's name, which should be used as cache index.
        """

        inputs = self.get_func_inputs(inputs, cached_outputs, card)
        executed_outputs = self.run(**inputs)
        return self.transform_outputs(executed_outputs)

    def run(self, *args, **kwargs):
        raise NotImplementedError()

    def __eq__(self, other):
        return self.name == other.name

    def __repr__(self):
        formatted_inputs = "    --" + "\n    --".join(f"{k}: {v}" for k, v in self.inputs.items())
        formatted_outputs = "    --" + "\n    --".join(f"{k}: {v}" for k, v in self.outputs.items())

        return (f"{self.position}::{self.__class__.__name__}: [{self.name}] @position:{self.position} in card: \n"
                f"  Inputs:\n"
                f"{formatted_inputs}\n"
                f"  Outputs:\n"
                f"{formatted_outputs}")
