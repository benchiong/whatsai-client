from tiny_db.card_info import CardModelTable
from tiny_db.model_dir import ModelDirTable
from tiny_db.model_type import ModelTypeTable


async def initialize_dbs():
    await ModelTypeTable.init()
    await ModelDirTable.init()
    await CardModelTable.init()
