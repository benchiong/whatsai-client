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
        sorted_models = sorted(models, key=lambda r: r.get('created_time_stamp'))
    elif sort == 'created_reverse':  # timestamp desc
        sorted_models = sorted(models, key=lambda r: r.get('created_time_stamp'), reverse=True)
    elif sort == 'order_num':  # order_num inc
        sorted_models = sorted(models, key=lambda r: r.get('order_num'))
    elif sort == 'order_num_reverse':  # order_num desc
        sorted_models = sorted(models, key=lambda r: r.get('order_num'), reverse=True)
    else:
        sorted_models = models

    return sorted_models


def fill_id(id_field: str | None, results):
    filled_results = []
    id_field = id_field if id_field else 'id'
    for result in results:
        result = {
            **result,
            id_field: result.doc_id
        }
        filled_results.append(result)
    return filled_results

