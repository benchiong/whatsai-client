from pathlib import Path

from core.abstracts.widget import Widget
from data_type.whatsai_model_info import ModelInfo
from misc.helpers import file_type_guess
from core.extras import tae_model_info_list


class TextWidget(Widget):
    def __init__(self, display_name, param_name, default_value=None):
        super().__init__(
            param_name=param_name,
            display_name=display_name,
            default_value=default_value,
            value_type=str,
        )

    def valid_input(self, param_value) -> str | None:
        return None


class IntWidget(Widget):
    def __init__(self, display_name, param_name, min, max, step, default_value=None):
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
            return f"Value: {param_value} of param: {self.param_name} must greater than min value: {self.min}, {str(self)}"

        if param_value > self.max:
            return f"Value: {param_value} of param: {self.param_name} must less than min value: {self.max}, {str(self)}"
        return None

    @property
    def info(self):
        return {
            **super().info,
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
            return "Value: {} of param: {} must greater than min value: {}, {}".format(
                param_value, self.param_name, self.min, str(self)
            )
        if param_value > self.max:
            return "Value: {} of param: {} must less than min value: {}, {}".format(
                param_value, self.param_name, self.max, str(self)
            )
        return None

    @property
    def info(self):
        return {
            **super().info,
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
            return "Seed value: {} must less than min value: {}, {}".format(param_value, self.max, str(self))
        if param_value < -1:
            return "Seed Value can only be -1."
        return None

    @property
    def info(self):
        return {
            **super().info,
            **{
                'max': int(self.max),
            }
        }


class ComboWidget(Widget):
    def __init__(self, display_name, param_name, values, value_type=str, default_value=None):

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
            return "Value: {} of param {}:  not in Combo values: {}, {}".format(param_value, self.param_name,
                                                                                self.values, str(self))

    @property
    def info(self):
        return {
            **super().info,
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
    def info(self):
        return {
            **super().info,
            **{
                'values_function_name': self.values_function_name,
                'values_function_params': self.values_function_params
            }
        }


class ModelComboWidget(DynamicComboWidget):
    def __init__(self, display_name, param_name, values_function_name, default_value, values_function_params=None):
        super().__init__(
            param_name=param_name,
            display_name=display_name,
            values_function_name=values_function_name,
            values_function_params=values_function_params,
            default_value=default_value,
            value_type=ModelInfo  # we don't verify it, so it's ok here.
        )

        # todo: fix values_function_params UI and deal logic

    @property
    def info(self):
        return {
            **super().info,
            **{
                'value': self.value,
            }
        }

    def valid_input(self, param_value) -> str | None:
        model_info = ModelInfo.get(param_value)
        if not model_info:
            return f"Model file: {param_value} not found, {str(self)}."

        local_path = model_info.local_path
        if not local_path or not Path(local_path).exists():
            return f"Model file not found: {local_path} of model: {param_value}"
        else:
            return None


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
            return "File type: {} mismatch, image expected, {}".format(mime, str(self))


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
            return "File type: {} mismatch, video expected, {}.".format(mime, str(self))


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
            return "File type: {} mismatch, audio expected, {}.".format(mime, str(self))


class GroupedWidgets(Widget):
    """ It exists in logic, but not used, Comp do the creation thing.
        See core.abstracts.comp.Comp.widgets_info for detail
     """

    def __init__(self, display_name, widgets, param_name, default_value, value_type):
        super().__init__(param_name, display_name, default_value, value_type)

    def valid_input(self, param_value) -> str | None:
        pass


def list_checkpoints(base_model: str | None = None):
    return ModelInfo.get_model_infos(model_type='checkpoint')


def list_clips():
    return ModelInfo.get_model_infos(model_type='clip')


def list_loras(base_model: str | None = None):
    return ModelInfo.get_model_infos(model_type='lora')


def list_vaes(approx_vaes: bool = True, base_model: str | None = None):
    vaes = ModelInfo.get_model_infos(model_type='vae')
    taesd_list = tae_model_info_list()
    if approx_vaes:
        vaes.extend(taesd_list)

    return vaes


def list_hypernets(base_model: str | None = None):
    return ModelInfo.get_model_infos(model_type='hypernet')


def list_upscalers():
    return ModelInfo.get_model_infos(model_type='upscaler')


def list_controlnets():
    return ModelInfo.get_model_infos(model_type='controlnet')


WIDGET_FUNCTION_MAP = {
    'list_checkpoints': list_checkpoints,
    'list_clips': list_clips,
    'list_loras': list_loras,
    'list_vaes': list_vaes,
    'list_hypernets': list_hypernets,
    'list_upscalers': list_upscalers,
    'list_controlnets': list_controlnets,
}
