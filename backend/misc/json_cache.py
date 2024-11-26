import json
import os
import time
import traceback
from pathlib import Path

from misc.logger import logger
from misc.whatsai_dirs import cache_dir

class JsonCache:

    default_expire_time_in_seconds = 60 * 60 * 24 * 30  # one month

    @classmethod
    def add(cls, file: str, key: str, value: any, expire_time: int = None):
        """ file: the first level key of cache, every file map a json file in cache dir
            key: a unique key under first level
            value: the json data to cache
            expire_time: the cache expired time, if none use default one month.
        """
        cached_result = cls.read_json(file)
        if not cached_result:
            json_to_add = {
                key: {
                    'value': value,
                    'expire_time': expire_time if expire_time else cls.default_expire_time_in_seconds,
                    'time': time.time()
                }
            }
        else:
            json_to_add = {
                **cached_result,
                key: {
                    'value': value,
                    'expire_time': expire_time if expire_time else cls.default_expire_time_in_seconds,
                    'time': time.time()
                }
            }

        cls.write_json(file.__str__(), json_to_add)

    @classmethod
    def get(cls, file: str, key: str, valid_expire_time=True):
        cached = cls.read_json(file)
        result = cached.get(key, None)

        if result and valid_expire_time:
            cached_time = result.get('time')
            expire_time = result.get('expire_time')
            now = time.time()

            if now - cached_time > expire_time:
                cls.remove(file, key)
                return None
            else:
                return result.get('value', None)

        return result

    @classmethod
    def remove(cls, file: str, key: str):
        origin_cache = cls.read_json(file)

        cached_value = origin_cache.get(key, None)
        if not cached_value:
            return
        else:
            origin_cache.pop(key)
            cls.write_json(file, origin_cache)

    @classmethod
    def file_path(cls, file: str):
        file_name_path = Path(file)

        assert file_name_path.parent == Path('.'), "Only file name without parent supported."

        # make sure it is a json file name
        if file_name_path.suffix != '.json':
            file_name = file + '.json'
        else:
            file_name = file

        return cache_dir / file_name

    @classmethod
    def read_json(cls, file: str):
        file_path = cls.file_path(file)

        if not file_path.exists():
            return {}

        # it's empty
        if os.path.getsize(file_path.__str__()) == 0:
            return {}

        try:
            with open(file_path.__str__(), "r") as cache_file:
                return json.loads(json.load(cache_file))
        except Exception as e:
            logger.error("read json file error:", e)
            return {}

    @classmethod
    def write_json(cls, file: str, json_content: dict):
        file_path = cls.file_path(file)

        if not file_path.exists():
            file_path.touch()

        try:
            with open(file_path.__str__(), "w", encoding='utf-8') as f:
                json.dump(json.dumps(json_content), f, indent=4)
                return True
        except Exception as e:
            traceback.print_exc()
            logger.error("write json file error:", e, 'content:', json_content)
            return False

