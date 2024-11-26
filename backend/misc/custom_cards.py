import importlib
import os
import sys
import traceback

from misc.logger import logger

custom_card_map = {}

def download_from_github(url):
    pass

def get_module_name(module_path: str) -> str:
    """
    Returns the module name based on the given module path.
    Examples:
        get_module_name("C:/Users/username/ComfyUI/custom_nodes/my_custom_node.py") -> "my_custom_node"
        get_module_name("C:/Users/username/ComfyUI/custom_nodes/my_custom_node") -> "my_custom_node"
        get_module_name("C:/Users/username/ComfyUI/custom_nodes/my_custom_node/") -> "my_custom_node"
        get_module_name("C:/Users/username/ComfyUI/custom_nodes/my_custom_node/__init__.py") -> "my_custom_node"
        get_module_name("C:/Users/username/ComfyUI/custom_nodes/my_custom_node/__init__") -> "my_custom_node"
        get_module_name("C:/Users/username/ComfyUI/custom_nodes/my_custom_node/__init__/") -> "my_custom_node"
        get_module_name("C:/Users/username/ComfyUI/custom_nodes/my_custom_node.disabled") -> "custom_nodes
    Args:
        module_path (str): The path of the module.
    Returns:
        str: The module name.
    """
    base_path = os.path.basename(module_path)
    if os.path.isfile(module_path):
        base_path = os.path.splitext(base_path)[0]
    return base_path


def load_custom_card(module_path: str, ignore=set()) -> list:
    module_name = os.path.basename(module_path)
    if os.path.isfile(module_path):
        sp = os.path.splitext(module_path)
        module_name = sp[0]
    try:
        logger.debug("Trying to load custom node {}".format(module_path))
        if os.path.isfile(module_path):
            module_spec = importlib.util.spec_from_file_location(module_name, module_path)
        else:
            module_spec = importlib.util.spec_from_file_location(module_name, os.path.join(module_path, "__init__.py"))

        module = importlib.util.module_from_spec(module_spec)
        sys.modules[module_name] = module
        module_spec.loader.exec_module(module)

        loaded_card_names = []
        if hasattr(module, "CUSTOM_CARDS_MAP") and getattr(module, "CUSTOM_CARDS_MAP") is not None:
            for name, card_cls in module.CUSTOM_CARDS_MAP.items():
                if name not in ignore:
                    custom_card_map[name] = card_cls
                    loaded_card_names.append(name)
            return loaded_card_names
        else:
            logger.warning(f"Skip {module_path} module for custom cards due to the lack of CUSTOM_CARDS_MAP.")
            return []
    except Exception as e:
        logger.warning(traceback.format_exc())
        logger.warning(f"Cannot import {module_path} module for custom card: {e}")
        return []

