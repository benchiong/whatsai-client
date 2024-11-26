from pathlib import Path

from core.abstracts import Widget
from tiny_db.model_info import ModelInfoTable
from misc.helpers import file_type_guess
from core.extras import tae_model_info_list

class TextWidget(Widget):
    def __init__(self,  display_name, param_name, default_value=None):
        super().__init__(
            param_name=param_name,
            display_name=display_name,
            default_value=default_value,
            value_type=str,
        )
    def valid_input(self, param_value) -> str | None:
        return None

class IntWidget(Widget):
    def __init__(self,  display_name, param_name, min, max, step, default_value=None):
        super().__init__(
            param_name=param_name,
            display_name=display_name,
            default_value=default_value,
            value_type=int,
        )
        self.min = min
        self.max = max
        self.step = step

    def valid_input(self, param_value) -> str | None:
        if self.optional and param_value is None:
            return None

        if param_value < self.min:
            return "Value: {} of param: {} must greater than min value: {}".format(param_value, self.param_name, self.min)
        if param_value > self.max:
            return "Value: {} of param: {} must less than min value: {}".format(param_value, self.param_name, self.max)
        return None

    @property
    def dict(self):
        return {
            **super().dict,
            **{
                'min': self.min,
                'max': self.max,
                'step': self.step,
            }
        }

class FloatWidget(Widget):
    def __init__(self, display_name, param_name, min, max, step, round, default_value=None):
        super().__init__(
            param_name=param_name,
            display_name=display_name,
            default_value=default_value,
            value_type=float,
        )
        self.min = min
        self.max = max
        self.step = step
        self.round = round

    def valid_input(self, param_value) -> str | None:
        if self.optional and param_value is None:
            return None

        if param_value < self.min:
            return "Value: {} of param: {} must greater than min value: {}".format(param_value, self.param_name, self.min)
        if param_value > self.max:
            return "Value: {} of param: {} must less than min value: {}".format(param_value, self.param_name, self.max)
        return None

    @property
    def dict(self):
        return {
            **super().dict,
            **{
                'min': self.min,
                'max': self.max,
                'step': self.step,
                'round': self.round
            }
        }

class SeedWidget(Widget):
    def __init__(self, display_name, param_name, max=0xffffffffffffffff, default_value=None):
        super().__init__(
            param_name=param_name,
            display_name=display_name,
            default_value=default_value,
            value_type=int,
        )
        self.max = max

    def valid_input(self, param_value) -> str | None:
        if self.optional and param_value is None:
            return None

        if param_value > self.max:
            return "Seed value: {} must less than min value: {}".format(param_value, self.max)
        if param_value < -1:
            return "Seed Value can only be -1."
        return None

    @property
    def dict(self):
        return {
            **super().dict,
            **{
                'max': int(self.max),
            }
        }

class ComboWidget(Widget):
    def __init__(self,  display_name, param_name, values, value_type=str, default_value=None):

        if not default_value and values:
            default_value = values[0]

        super().__init__(
            param_name=param_name,
            display_name=display_name,
            default_value=default_value,
            value_type=value_type,
        )
        self.values = values if values else []

    def valid_input(self, param_value) -> str | None:
        if self.optional and param_value is None:
            return None

        if param_value in self.values:
            return None
        else:
            return "Value: {} of param {}:  not in Combo values: {}".format(param_value,self.param_name, self.values)

    @property
    def dict(self):
        return {
            **super().dict,
            **{
                'values': self.values,
            }
        }

class WidgetFunctionNotFoundException(Exception):
    pass

class EmptyComboValuesException(Exception):
    pass

class DynamicComboWidget(ComboWidget):
    def __init__(self,
                 display_name,
                 param_name,
                 values_function_name,
                 values_function_params=None,
                 value_type=str,
                 default_value=None
                 ):
        values_function = WIDGET_FUNCTION_MAP.get(values_function_name)
        if not values_function:
            raise WidgetFunctionNotFoundException('Function: {} not found.'.format(values_function_name))

        super().__init__(
            param_name=param_name,
            display_name=display_name,
            default_value=default_value,
            value_type=value_type,
            values=[]
        )
        self.widget_name = 'DynamicComboWidget'
        self.values_function_name = values_function_name
        self.values_function_params = values_function_params

    def valid_input(self, param_value) -> str | None:
        return None

    @property
    def dict(self):
        return {
            **super().dict,
            **{
                'values_function_name': self.values_function_name,
                'values_function_params': self.values_function_params
            }
        }

class ModelComboWidget(DynamicComboWidget):
    def __init__(self,  display_name, param_name, values_function_name, default_value, values_function_params=None):
        super().__init__(
            param_name=param_name,
            display_name=display_name,
            values_function_name=values_function_name,
            values_function_params=values_function_params,
            default_value=default_value,
            value_type=ModelInfoTable.DataModel  # we don't verify it, so it's ok here.
        )

        #todo: fix values_function_params UI and deal logic

    @property
    def dict(self):
        return {
            **super().dict,
            **{
                'value': self.value,
            }
        }

    def valid_input(self, param_value) -> str | None:
        return None

    @property
    def default_value_info(self):
        return {
            'checkpoint': {
                'model_name': self.value.get('file_name') if self.value else None,
                'sha_256': self.value.get('sha_256') if self.value else None
            }
        }

class FileWidget(Widget):
    def __init__(self, param_name, display_name="File Select", value_type=str, default_value=None):
        super().__init__(
            param_name=param_name,
            display_name=display_name,
            default_value=default_value,
            value_type=value_type,
        )
        self.widget_name = "FileWidget"

    # todo: finish remote url logic
    def valid_input(self, param_value) -> str | None:
        if self.optional and param_value is None:
            return None

        if not param_value:
            return "File required."

        if not Path(param_value).exists():
            return "File not exists."

        return None

class ImageWidget(FileWidget):
    def __init__(self, param_name, display_name="Image Select", value_type=str, default_value=None):
        super().__init__(
            param_name=param_name,
            display_name=display_name,
            default_value=default_value,
            value_type=value_type,
        )

    def valid_input(self, param_value) -> str | None:
        if self.optional and (param_value is None or param_value == 'None'):
            return None
        print(self.optional, param_value, type(param_value))
        mime = file_type_guess(param_value)
        if mime.startswith('image'):
            return None
        else:
            return "File type: {} mismatch, image expected.".format(mime)

class VideoWidget(FileWidget):
    def __init__(self, param_name, display_name="Image Select", value_type=str, default_value=None):
        super().__init__(
            param_name=param_name,
            display_name=display_name,
            default_value=default_value,
            value_type=value_type,
        )

    def valid_input(self, param_value) -> str | None:
        if self.optional and param_value is None:
            return None

        mime = file_type_guess(param_value)
        if mime.startswith('video'):
            return None
        else:
            return "File type: {} mismatch, video expected.".format(mime)


class AudioWidget(FileWidget):
    def __init__(self, param_name, display_name="Image Select", value_type=str, default_value=None):
        super().__init__(
            param_name=param_name,
            display_name=display_name,
            default_value=default_value,
            value_type=value_type,
        )

    def valid_input(self, param_value) -> str | None:
        if self.optional and param_value is None:
            return None

        mime = file_type_guess(param_value)
        if mime.startswith('audio'):
            return None
        else:
            return "File type: {} mismatch, audio expected.".format(mime)

class GroupedWidgets(Widget):
    """ It exists in logic, but not used, Comp do the creation thing.
        See core.abstracts.comp.Comp.widgets_dict_grouped_widgets_considered for detail
     """
    def __init__(self, display_name, widgets, param_name, default_value, value_type):
        super().__init__(param_name, display_name, default_value, value_type)

    def valid_input(self, param_value) -> str | None:
        pass


def list_checkpoints(base_model: str | None = None):
    checkpoints = ModelInfoTable.sync_get_model_info_by_model_type('checkpoint', base_model=base_model)
    return checkpoints

def list_loras(base_model: str | None = None):
    loras = ModelInfoTable.sync_get_model_info_by_model_type('lora', base_model=base_model)
    return loras

def list_vaes(approx_vaes: bool = True, base_model: str | None = None):
    vae_records = ModelInfoTable.sync_get_model_info_by_model_type("vae", base_model=base_model)

    taesd_list = tae_model_info_list()
    if approx_vaes:
        vae_records.extend(taesd_list)

    return vae_records

def list_hypernets(base_model: str | None = None):
    hypernets = ModelInfoTable.sync_get_model_info_by_model_type('hypernet', base_model=base_model)
    return hypernets

def list_upscalers():
    return ModelInfoTable.sync_get_model_info_by_model_type('upscaler')

def list_controlnets():
    return ModelInfoTable.sync_get_model_info_by_model_type('controlnet')

WIDGET_FUNCTION_MAP = {
    'list_checkpoints': list_checkpoints,
    'list_loras': list_loras,
    'list_vaes': list_vaes,
    'list_hypernets': list_hypernets,
    'list_upscalers': list_upscalers,
    'list_controlnets': list_controlnets,
}
