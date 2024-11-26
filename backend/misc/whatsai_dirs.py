from pathlib import Path

from data_type.whatsai_artwork import MediaType

base_dir = Path.home() / 'whatsai'
""" The data dir of whatsai, we need it because python exe file need it outside the project. """


db_path_dir = base_dir / '_db_files__do_not_remove_me__'
model_info_images_dir = base_dir / 'files' / 'model_info_images'
media_files_dir = base_dir / 'files' / 'media_files'
cache_dir = base_dir / '_whatsai_cache'
model_base_dir_name = base_dir / 'models'

output_dir = base_dir / 'output'
img_dir = output_dir / 'images'
video_dir = output_dir / 'videos'
audio_dir = output_dir / 'audios'
other_dir = output_dir / 'others'

file_paths_to_init = [
    db_path_dir,
    model_info_images_dir,
    media_files_dir,
    model_base_dir_name,
    cache_dir,
    img_dir,
    video_dir,
    audio_dir,
    other_dir
]


def init_file_paths():
    global file_paths_to_init
    for file_path in file_paths_to_init:
        file_path.mkdir(exist_ok=True, parents=True)
    print("dirs inited")


def get_dir_of_media_type(media_type: MediaType):
    if media_type == 'image':
        return img_dir
    elif media_type == 'video':
        return video_dir
    elif media_type == 'audio':
        return audio_dir
    else:
        return other_dir

