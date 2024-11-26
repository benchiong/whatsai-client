from tinydb import Query


class BaseTable:
    table_name = None
    """ the json file path to store the data."""

    DataModel = None
    """ Data type defined used pydantic. """

    Q = Query()

    @classmethod
    async def init(cls):
        pass


