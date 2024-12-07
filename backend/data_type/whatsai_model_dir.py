import json
from contextlib import closing
from pathlib import Path

from misc.constants import comfyui_model_dirs_map, webui_model_dirs_map, supported_pt_extensions
from misc.helpers import get_model_files_in_dir
from misc.whatsai_dirs import model_base_dir_name
from data_type.base_data_model import PyDBModel
from data_type.whatsai_model_type import ModelType


class ModelDir(PyDBModel):
    model_type: str
    dirs: list[str] = []
    default_dir: str
    counts: list[int] = []

    @classmethod
    def create_table(cls):
        conn = cls.conn()
        with closing(conn.cursor()) as cur:
            cur.execute(
                """CREATE TABLE IF NOT EXISTS model_dir
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                        model_type TEXT UNIQUE,
                        dirs TEXT,
                        default_dir TEXT,
                        counts TEXT
                        )"""
            )
            cur.execute("CREATE INDEX IF NOT EXISTS model_dir_idx_model_type ON model_dir(model_type)")

            conn.commit()

    @classmethod
    def init(cls):
        cls.create_table()
        all_model_types = ModelType.get_all_model_types()
        model_dirs = []
        for model_type in all_model_types:
            dir_path = model_base_dir_name / model_type.lower()
            dir_path.mkdir(exist_ok=True, parents=True)
            model_dir = cls(model_type=model_type, dirs=[str(dir_path)], default_dir=str(dir_path), counts=[0])
            model_dirs.append(model_dir)
        cls.insert_many(model_dirs)

    @classmethod
    def add_model_dir(cls, model_type, model_dir, set_as_default=False):
        """Add model path record of model type, because we don't know where user stores models,
        it must be told by the user, it is used under this situation, the model_dir must exist before adding.
        """
        model_type_registered = ModelType.is_model_type_registered(model_type)
        if not model_type_registered:
            return False, 'Model type: {} not exits.'.format(model_type), None

        # check model dir is right
        if not Path(model_dir).exists():
            return False, 'Path: {} not exists.'.format(model_dir), None
        if not Path(model_dir).is_dir():
            return False, 'Path: {} must be dir to store model files.'.format(model_dir), None

        model_dir_obj = cls.get(model_type)
        if not model_dir_obj:
            model_dir_obj = cls(model_type=model_type, dirs=[model_dir], default_dir=model_dir)
        else:
            if model_dir not in model_dir_obj.dirs:
                model_dir_obj.dirs.append(model_dir)
            if set_as_default:
                model_dir_obj.default_dir = model_dir
        model_dir_obj.save()
        model_dir_obj.update_counts()
        return True, None, model_dir_obj

    @classmethod
    def remove_model_dir(cls, model_type, model_dir):
        model_dir_obj = cls.get(model_type)
        if not model_dir_obj:
            return False, "No record found.", None
        dirs = model_dir_obj.dirs
        if model_dir in dirs:
            model_dir_obj.dirs.remove(model_dir)
        if model_dir_obj.default_dir == model_dir:
            model_dir_obj.default_dir = model_dir_obj.dirs[-1] if len(model_dir_obj.dirs) > 0 else ''
        model_dir_obj.save()
        return True, None, model_dir_obj.model_dump()

    @classmethod
    def set_default_model_dir(cls, model_type, model_dir):
        model_dir_obj = cls.get(model_type)
        if not model_dir_obj:
            return False, "No record found.", None
        if not model_dir in model_dir_obj.dirs:
            return False, f"{model_dir} not in existed dirs {model_dir_obj.dirs}", None
        model_dir_obj.default_dir = model_dir
        model_dir_obj.save()
        return True, None, model_dir_obj

    def save(self):
        conn = self.conn()
        with closing(conn.cursor()) as cur:
            cur.execute(
                "INSERT OR REPLACE INTO model_dir (id, model_type, dirs, default_dir, counts) VALUES (?, ?, ?, ?, ?)",
                self.to_tuple(with_id=True),
            )
            self.id = cur.lastrowid
            conn.commit()

    def update_counts(self):
        dirs = self.dirs
        counts = []
        for dir in dirs:
            count = len(get_model_files_in_dir(dir))
            counts.append(count)
        self.counts = counts
        self.save()

    @classmethod
    def get(cls, id_or_model_type):
        conn = cls.conn()
        with closing(conn.cursor()) as cur:
            cur.execute(
                "SELECT * FROM model_dir where id = ? or model_type = ?", (id_or_model_type, id_or_model_type)
            )
            row = cur.fetchone()
            if row is None:
                return None
            else:
                return cls.from_row(row)

    @classmethod
    def get_dirs(cls, model_type):
        obj = cls.get(model_type)
        return obj.dirs if obj else None

    @classmethod
    def get_all(cls):
        conn = cls.conn()
        with closing(conn.cursor()) as cur:
            cur.execute("SELECT * FROM model_dir")
            rows = cur.fetchall()
            return [cls.from_row(row) for row in rows]

    @classmethod
    def insert_many(cls, model_dirs):
        conn = cls.conn()
        model_tuples = []
        for model_dir in model_dirs:
            model_tuples.append(model_dir.to_tuple())
        with closing(conn.cursor()) as cur:
            cur.executemany("""
                         INSERT OR IGNORE INTO model_dir (model_type, dirs, default_dir, counts) VALUES (?, ?, ?, ?)
                        """, model_tuples)
            conn.commit()

    def to_tuple(self, with_id=False):
        model_dict = self.model_dump()
        model_dict['dirs'] = json.dumps(model_dict.get('dirs', []))  # save list as a str, decode when map to object.
        model_dict['counts'] = json.dumps(model_dict.get('counts', []))

        if with_id:
            return tuple(model_dict.values())
        else:
            model_dict.pop('id')
            return tuple(model_dict.values())

    @classmethod
    def from_row(cls, row: tuple):
        model_dir = cls(
            id=row[0],
            model_type=row[1],
            dirs=json.loads(row[2]),
            default_dir=row[3],
            counts=json.loads(row[4])
        )
        return model_dir

    # ----
    # todo: may somewhere else to put them is better?
    # ----

    @classmethod
    def get_model_files(cls, model_type):
        if not model_type:
            model_dir_objs = ModelDir.get_all()

        else:
            model_dir_obj = ModelDir.get(model_type)
            model_dir_objs = [model_dir_obj] if model_dir_obj else []

        model_file_paths = []
        for model_dir_obj in model_dir_objs:
            model_type, dirs = model_dir_obj.model_type, model_dir_obj.dirs
            for dir_path in dirs:
                files_in_dir = get_model_files_in_dir(dir_path)
                model_file_paths.extend(files_in_dir)
        return model_file_paths

    @classmethod
    def _add_other_ui_dirs(cls, ui_base_dir: str, map_file: dict, set_as_default: bool):
        ui_base_dir = Path(ui_base_dir)
        if not ui_base_dir.exists():
            return [], 'Dir path: {} not exists.'.format(str(ui_base_dir))

        appended_dirs = []
        for model_type, model_dir_name_or_name_list in map_file.items():
            if isinstance(model_dir_name_or_name_list, list):
                for model_dir_name in model_dir_name_or_name_list:
                    model_dir = ui_base_dir / model_dir_name
                    success, _, _ = cls.add_model_dir(model_type, str(model_dir), set_as_default)
                    if success:
                        appended_dirs.append((model_type, str(model_dir)))
            else:
                model_dir = ui_base_dir / model_dir_name_or_name_list
                success, _, _ = cls.add_model_dir(model_type, str(model_dir), set_as_default)
                if success:
                    appended_dirs.append((model_type, str(model_dir)))
        return appended_dirs, None

    @classmethod
    def add_comfy_dirs(cls, comfy_base_dir: str, set_as_default: bool):
        return cls._add_other_ui_dirs(comfy_base_dir, comfyui_model_dirs_map, set_as_default)

    @classmethod
    def add_webui_dirs(cls, webui_base_dir, set_as_default: bool):
        return cls._add_other_ui_dirs(webui_base_dir, webui_model_dirs_map, set_as_default)

