# from https://github.com/zanllp/sd-webui-infinite-image-browsing, thanks

import threading
import re
from sqlite3 import Connection, connect
from typing import Optional

from pydantic import BaseModel, ConfigDict

from misc.arg_parser import is_prod
from misc.whatsai_dirs import sqlite_dir

sqlite_db_path = sqlite_dir / 'sqlite.db'

class DB:
    local = threading.local()

    _initing = False

    num = 0

    path = str(sqlite_db_path)
    sqlite_db_path.touch(exist_ok=True)

    @classmethod
    def get_conn(clz) -> Connection:
        # for : sqlite3.ProgrammingError: SQLite objects created in a thread can only be used in that same thread
        if hasattr(clz.local, "conn"):
            return clz.local.conn
        else:
            conn = clz.init()
            clz.local.conn = conn

            return conn

    @classmethod
    def get_db_file_path(clz):
        return clz.path

    @classmethod
    def init(clz):
        conn = connect(clz.get_db_file_path())

        def regexp(expr, item):
            if not isinstance(item, str):
                return False
            reg = re.compile(expr, flags=re.IGNORECASE | re.MULTILINE | re.DOTALL)
            return reg.search(item) is not None

        conn.create_function("regexp", 2, regexp)
        clz.num += 1
        if not is_prod:
            print(f"Connection count: {clz.num}")
        return conn

class PyDBModel(BaseModel):
    id: Optional[int] = None

    @classmethod
    def conn(cls):
        return DB.get_conn()

    @classmethod
    def to_tuples(cls, objs):
        tuples = []
        for obj in objs:
            tuples.append(obj.to_tuple())
        return tuples

    def to_tuple(self, with_id=False):
        if with_id:
            return tuple(self.model_dump().values())
        else:
            d = self.model_dump()
            d.pop('id')
            return tuple(d.values())

    # fix annoying warning:  Field "model_type" in DataModel has conflict with protected namespace "model_".
    model_config = ConfigDict(protected_namespaces=())
