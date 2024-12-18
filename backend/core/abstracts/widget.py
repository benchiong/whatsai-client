import traceback
from abc import ABC, abstractmethod
from typing import Type

from misc.logger import logger


class Widget(ABC):
    """ One widget for one param value, make it be the smallest unit. Take it as the bridge of frontend and backend. """

    def __init__(self, param_name, display_name, default_value, value_type: Type, optional=False):
        self.param_name = param_name
        self.display_name = display_name
        self.value = default_value
        self.value_type = value_type
        self.optional = optional

        # todo: make sure we need them, remove if don't.
        self._origin_to_new_param_name_map = {}
        self._current_to_origin_param_name_map = {}

    def set_optional(self, optional):
        self.optional = optional

    @abstractmethod
    def valid_input(self, param_value) -> str | None:
        """ Used to valid the values from frontend.
            :param param_value: value of the param.
            :return: error info if fails else None.
        """
        pass

    def make_type_right(self, param_value):
        """
            Make the value from frontend the right type, as the data from frontend is
            in json form, transform it to corresponding type like ComfyUI do.
            https://github.com/comfyanonymous/ComfyUI/blob/master/execution.py#L633
            Do not raise exception, return origin value if failed.
            Override this method if you have custom logic.

            :param param_value: value of the param.
            :return: the value after correction
        """
        try:
            if param_value == 'None' or param_value is None:
                return None

            if self.value_type in [int, str, bool, float]:
                return self.value_type(param_value)
            else:
                return param_value

        except Exception as e:
            logger.debug(f"make_type_right error: {e}")
            traceback.print_exc()

            return param_value

    @property
    def info(self):
        """ Used to tell frontend how to render UI by backend. """

        return {
            'display_name': self.display_name,
            'param_name': self.param_name,
            'value': self.value,
            'optional': self.optional,
            'widget_type': self.__class__.__name__,
        }

    def __repr__(self):
        return f"{self.__class__.__name__}: {self.param_name}:{self.value} in type:{self.value_type}"
