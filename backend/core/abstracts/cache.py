class OutputsCache:
    """ The cache of outputs of a Func/Comp/Addon, used by prompt worker as a global outputs cache,
        and can also be used as an inner cache of Comp/Addon as a tmp storage for consistency.
        Its form is three level nesting keys .

        cache data format:
        {
            'func_name/comp_name/addon_name':  {
                index_of_func: {
                    param_name: value
                    ...
                }
                ...
            }
            ...
        }

    """

    def __init__(self):
        self.cache = {}

    def cached_keys(self):
        return self.cache.keys()

    def cache_func_outputs(self, func_name: str, func_idx: int, outputs: dict):
        if not self.get_func_outputs(func_name):
            self.cache[func_name] = {}

        self.cache[func_name][func_idx] = outputs

    def clear_func_outputs(self, func_name: str):
        if func_name in self.cache.keys():
            d = self.cache.pop(func_name)
            del d

    def clear_all(self):
        tmp = self.cache
        self.cache = {}
        del tmp

    def get_func_outputs(self, func_name: str):
        return self.cache.get(func_name)

    def get_param_output(self, func_name: str, func_idx: int, param_name: str):
        func_outputs = self.get_func_outputs(func_name)
        if not func_outputs:
            return None
        outputs_at_idx = func_outputs.get(func_idx)
        if not outputs_at_idx:
            return None
        return outputs_at_idx.get(param_name)

    def sync_cache(self, other_cache):
        self.cache = {**other_cache.cache}
