from typing import Literal

from data_type.whatsai_model_info import ModelInfo

SortType = Literal[
    'created',
    'created_reverse',
    'order_num',
    'order_num_reverse'
]


def sort_model_info(models: list[ModelInfo], sort: SortType = 'created_reverse'):
    if type(models) is not list:
        return models

    if sort == 'created':  # timestamp inc
        sorted_models = sorted(models, key=lambda r: r.created_time_stamp)
    elif sort == 'created_reverse':  # timestamp desc
        sorted_models = sorted(models, key=lambda r: r.created_time_stamp, reverse=True)
    elif sort == 'order_num':  # order_num inc
        sorted_models = sorted(models, key=lambda r: r.order_num)
    elif sort == 'order_num_reverse':  # order_num desc
        sorted_models = sorted(models, key=lambda r: r.order_num, reverse=True)
    else:
        sorted_models = models

    return sorted_models
