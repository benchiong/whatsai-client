import collections
import inspect
from abc import ABC, abstractmethod
from types import UnionType
from typing import Literal, get_origin, get_args

import torch

from misc.logger import logger

class ParameterValidationException(Exception):
    pass

class Func(ABC):
    def __init__(self, name=None, cache_out=True, valid_inputs=True):
        self._name = name
        """ We need it when multiple Func of same type in parent(Card/Addon). """

        self.cache_out = cache_out
        self._valid_inputs = valid_inputs

        self.last_inputs = None
        self.last_out = None

    @abstractmethod
    def run(self, *args, **kwargs) -> any:
        pass

    def __call__(self, *args, **kwargs):
        if self.cache_out and self._inputs_unchanged(*args, **kwargs):
            return self.last_out

        if self._valid_inputs:
            self.valid_inputs(*args, **kwargs)

        out = self.run(*args, **kwargs)

        if self.cache_out:
            self.last_inputs = args, kwargs
            self.last_out = out

        return out

    @property
    def name(self):
        return self._name if self._name else self.__class__.__name__

    @property
    def param_names(self):
        names = inspect.signature(self.run).parameters.keys()
        return tuple(names)

    def valid_inputs(self, *args, **kwargs):
        def valid_type(value, expected_type):
            origin_type = get_origin(expected_type)
            args_type = get_args(expected_type)
            if origin_type is None or origin_type is collections.abc.Callable:
                return isinstance(value, expected_type)
            if origin_type is Literal:
                return value in args_type
            if origin_type is UnionType:
                return any([valid_type(value, arg_type) for arg_type in args_type])
            if not isinstance(value, origin_type):
                return False
            if origin_type is list or origin_type is tuple:
                return len(value) > 0 and all(valid_type(v, args_type[0]) for v in value)
            if origin_type is dict:
                not_empty = len(value) > 0
                keys_valid = all(valid_type(k, args_type[0]) for k in value.keys())
                values_valid = all(valid_type(v, args_type[1]) for v in value.values())
                return not_empty and keys_valid and values_valid
            return False

        valid_infos = []
        signature = inspect.signature(self.run)
        for i, param in enumerate(signature.parameters.values()):
            param_name = param.name
            param_type = param.annotation
            param_value = args[i] if i < len(args) else kwargs.get(param_name)
            if param_type is inspect._empty or valid_type(param_value, param_type):
                continue
            else:
                valid_infos.append('Input value: {} of param: {} mismatch, expect type {}, but got {}.'.format(
                    param_value, param_name, param_type, type(param_value)))

        if valid_infos:
            raise ParameterValidationException(str(valid_infos))

    def _inputs_unchanged(self, *args, **kwargs) -> bool:
        if not self.last_inputs:
            return False

        last_args, last_kwargs = self.last_inputs

        def equals(a, b):
            if not type(b) == type(a):
                return False

            if isinstance(a, (tuple, list)):
                if not len(a) == len(b):
                    return False

                result = []
                for _a, _b in zip(a, b):
                    result.append(equals(_a, _b))
                return all(result)

            elif isinstance(a, dict):
                a_values = tuple(a.values())
                b_values = tuple(b.values())
                a_keys = tuple(a.keys())
                b_keys = tuple(b.keys())
                return equals(a_values, b_values) and equals(a_keys, b_keys)
            elif torch.is_tensor(a) and torch.is_tensor(b):
                return torch.equal(a, b)
            else:
                if torch.is_tensor(a) or torch.is_tensor(b):
                    return False

                try:
                    return a == b
                except Exception as e:
                    logger.debug("Equal func exception:", e, 'a:', a, 'b:', b)
                    return False

        return equals(args, last_args) and equals(kwargs, last_kwargs)