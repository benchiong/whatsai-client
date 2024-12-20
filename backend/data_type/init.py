from data_type.whatsai_artwork import Artwork
from data_type.whatsai_card import CardDataModel
from data_type.whatsai_input_file import InputFile
from data_type.whatsai_model_dir import ModelDir
from data_type.whatsai_model_download_task import ModelDownloadTask
from data_type.whatsai_model_downloading_info import ModelDownloadingInfo
from data_type.whatsai_model_info import ModelInfo
from data_type.civitai_model_version import CivitaiModelVersion
from data_type.whatsai_model_type import ModelType
from data_type.whatsai_task import Task


def initialize_dbs():
    ModelType.init()
    ModelDir.init()
    ModelInfo.init()
    CivitaiModelVersion.init()
    ModelDownloadTask.init()
    ModelDownloadingInfo.init()
    Task.init()
    CardDataModel.init()
    InputFile.init()
    Artwork.init()
