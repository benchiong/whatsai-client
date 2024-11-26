from pathlib import Path

from aiotinydb import AIOTinyDB
from tinydb import Query, TinyDB

from data_type.whatsai_model_dir import ModelDir
from misc.constants import supported_pt_extensions, comfyui_model_dirs_map, \
    webui_model_dirs_map
from misc.whatsai_dirs import db_path_dir, model_base_dir_name
from misc.helpers import get_files_in_dir
from tiny_db.base_table import BaseTable
from tiny_db.model_type import ModelTypeTable

class ModelDirTable(BaseTable):
    table_name = db_path_dir / 'model_dir.json'
    DataModel = ModelDir

    @classmethod
    async def init(cls):
        # do not add init recorder logic here, in case the dir is deleted by user not intentionally.
        all_model_types = await ModelTypeTable.all_model_types()
        for model_type in all_model_types:
            dir_path = model_base_dir_name / model_type.lower()
            dir_path.mkdir(exist_ok=True, parents=True)
            dir_path_str = dir_path.__str__()
            await cls.add_model_dir(model_type, dir_path_str)

    @classmethod
    async def add_model_dir(cls,
                            model_type: str,
                            model_dir: str,
                            register_model_type_if_not_exists: bool = False,
                            set_as_default: bool = False,
                            ):
        """
            Add model path record of model type, because we don't know where user stores models, it must be told
            by the user, it is used under this situation, the model_dir must exist before adding.

            :param model_type: used to tell which type the dir belongs, one model_type may have multiple dirs.
            :param model_dir: user's local dir for the model type, can be whatsai created or other UI or user created.
            :param register_model_type_if_not_exists: if set True, will register model type automatic,
                force existed otherwise.
            :param set_as_default: if set True, models in this type will be downloaded to this dir.
            :return: (success, error_info)
        """

        assert model_type, "model_type required."
        assert model_dir, "model_dir required."

        # check model type registered or not
        model_type_registered = await ModelTypeTable.is_model_type_registered(model_type)
        if not model_type_registered:
            if register_model_type_if_not_exists:
                await ModelTypeTable.register_model_type(model_type, source='custom')
            else:
                return False, 'Model type: {} not exits.'.format(model_type), None

        # check model dir is right
        if not Path(model_dir).exists():
            return False, 'Path: {} not exists.'.format(model_dir), None
        if not Path(model_dir).is_dir():
            return False, 'Path: {} must be dir to store model files.'.format(model_dir), None

        # check the record in db exits or not, create one if not exits, update it otherwise.
        model_dir_records = await cls.get_model_dir_records(model_type)
        if not model_dir_records:
            async with AIOTinyDB(cls.table_name) as db:
                data_model = cls.DataModel(model_type=model_type, dirs=[model_dir], default_dir=model_dir)
                db.insert(data_model.model_dump())
                return True, None, data_model
        else:
            record = model_dir_records[0]
            dirs = record.get('dirs')
            if dirs and model_dir not in dirs:
                dirs.append(model_dir)
                async with AIOTinyDB(cls.table_name) as db:
                    if set_as_default:
                        db.update({
                            'dirs': dirs,
                            'default_dir': model_dir
                        }, doc_ids=[record.doc_id])
                    else:
                        db.update({
                            'dirs': dirs
                        }, doc_ids=[record.doc_id])

                    Q = Query()
                    updated_records = db.search(Q.model_type == model_type)
                    return True, None, updated_records[0]
            else:
                return True, None, record

    @classmethod
    async def remove_model_dir(cls,
                               model_type: str,
                               model_dir: str,
                               ):
        model_dir_records = await cls.get_model_dir_records(model_type)
        if not model_dir_records:
            return False, "No record found.", model_dir_records[0]
        else:
            record = model_dir_records[0]
            dirs = record.get('dirs')
            if dirs and model_dir in dirs:
                dirs.remove(model_dir)
                async with AIOTinyDB(cls.table_name) as db:
                    db.update({
                        'dirs': dirs
                    }, doc_ids=[record.doc_id])

                    Q = Query()
                    updated_records = db.search(Q.model_type == model_type)
                    return True, None, updated_records[0]
            else:
                return False, "Dir not in record", record

    @classmethod
    async def set_default_model_dir(cls, model_type: str, model_dir: str):
        model_dir_records = await cls.get_model_dir_records(model_type)
        if not model_dir_records:
            return False, "No record found.", None
        record = model_dir_records[0]
        dirs = record.get('dirs')
        if not dirs or model_dir not in dirs:
            return False, "{} not in dirs".format(model_dir), record

        async with AIOTinyDB(cls.table_name) as db:

            db.update({
                'default_dir': model_dir
            }, doc_ids=[record.doc_id])

            Q = Query()
            updated_records = db.search(Q.model_type == model_type)
            return True, None, updated_records[0]

    @classmethod
    async def model_dir_recorded(cls, model_type: str, model_dir: str):
        dirs_of_model_type = await cls.get_model_dirs(model_type)
        return model_dir in dirs_of_model_type

    @classmethod
    async def get_model_dir_records(cls, model_type: str):
        async with AIOTinyDB(cls.table_name) as db:
            Q = Query()
            return db.search(Q.model_type == model_type)

    @classmethod
    async def get_single_model_dir_record(cls, model_type: str):
        records = await cls.get_model_dir_records(model_type)
        if not records:
            return None
        return records[0]

    @classmethod
    async def get_all_model_dir_records(cls):
        async with AIOTinyDB(cls.table_name) as db:
            return db.all()

    @classmethod
    def sync_get_all_model_dir_records(cls):
        db = TinyDB(cls.table_name)
        return db.all()

    @classmethod
    async def get_model_dirs(cls, model_type: str):
        records = await cls.get_model_dir_records(model_type)
        if records:
            return records[0].get('dirs')
        else:
            return []

    @classmethod
    def sync_get_model_dirs(cls, model_type: str):
        db = TinyDB(cls.table_name)
        Q = Query()
        records = db.search(Q.model_type == model_type)
        if records:
            return records[0].get('dirs')
        else:
            return []

    @classmethod
    def sync_get_model_files_in_dir(cls, dir_path: str):
        files_in_dir = get_files_in_dir(dir_path)

        model_files = []
        for file in files_in_dir:  # filter by suffix and file name.
            name = file.name
            ext = file.suffix
            if not name.startswith(('.', '_')) and ext in supported_pt_extensions:
                model_files.append(str(file.absolute()))

        return model_files

    @classmethod
    async def add_comfy_dirs(cls, comfy_base_dir: str, set_as_default: bool):
        return await cls._add_other_ui_dirs(comfy_base_dir, comfyui_model_dirs_map, set_as_default)

    @classmethod
    async def add_webui_dirs(cls, webui_base_dir, set_as_default: bool):
        return await cls._add_other_ui_dirs(webui_base_dir, webui_model_dirs_map, set_as_default)

    @classmethod
    async def _add_other_ui_dirs(cls, ui_base_dir: str, map_file: dict, set_as_default: bool):
        ui_base_dir = Path(ui_base_dir)
        if not ui_base_dir.exists():
            return [], 'Dir path: {} not exists.'.format(ui_base_dir)

        async def add_single_dir(_base_dir, _dir_name, _appended_dirs):
            model_dir = _base_dir / _dir_name
            if model_dir.exists():
                await cls.add_model_dir(
                    model_type=model_type,
                    model_dir=model_dir.__str__(),
                    set_as_default=set_as_default
                )
                _appended_dirs.append((model_type, model_dir))

        appended_dirs = []
        for model_type, model_dir_name_or_name_list in map_file.items():
            if isinstance(model_dir_name_or_name_list, list):
                for model_dir_name in model_dir_name_or_name_list:
                    await add_single_dir(ui_base_dir, model_dir_name, appended_dirs)
            else:
                await add_single_dir(ui_base_dir, model_dir_name_or_name_list, appended_dirs)
        return appended_dirs, None


