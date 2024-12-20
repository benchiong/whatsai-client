import os
import shutil
import socket
import time
import traceback
from pathlib import Path

import httpx

from common import tmp_dir, update_backend_install_progress_info


async def async_get(url, headers=None, timeout=10, retry=3):
    while retry > 0:
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                return await client.get(url, headers=headers)
        except Exception as e:
            time.sleep(3)
            retry -= 1
            print("async_get error")
            traceback.print_exc()
    return None


async def async_post(url, headers=None, timeout=10, retry=3):
    while retry > 0:
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                return await client.post(url, headers=headers)
        except Exception as e:
            time.sleep(3)
            retry -= 1
            print("async_post error")
            traceback.print_exc()


async def download_file(url, destination, callback=None):
    destination_path = Path(destination)
    if destination_path.exists():
        print(f"File: {destination} already downloaded")
        return True

    filename = destination_path.name
    downloading_file = destination + '.downloading'

    try:
        async with httpx.AsyncClient() as client:
            # Initiate the request
            with open(downloading_file, "wb") as f:
                async with client.stream("GET", url) as response:
                    response.raise_for_status()  # Raise an exception for bad status codes

                    # Get the total file size from headers
                    total_size = int(response.headers.get("Content-Length", 0))
                    print(f"total_size to download: {total_size / 1024 / 1024:.1f} MB")
                    downloaded_size = 0

                    # Read chunks of the file and write to destination
                    async for chunk in response.aiter_bytes(chunk_size=1024):
                        f.write(chunk)
                        downloaded_size += len(chunk)

                        # Update progress
                        if total_size > 0:
                            percent = (downloaded_size / total_size) * 100
                            print(
                                f"\rDownloading {filename}: {percent:.2f}% ({downloaded_size / 1024 / 1024:.1f}/{total_size / 1024 / 1024:.1f} Mb)",
                                end="")

                            if callback:
                                callback(percent, downloaded_size, total_size)
                        else:
                            if callback:
                                print(
                                    f"\rDownloading {filename}: {downloaded_size / 1024 / 1024:.1f} Mb)",
                                    end="")
                                callback(None, downloaded_size, None)

                    os.rename(downloading_file, destination)
                    print("Download complete.")
                    update_backend_install_progress_info(stage='Python file downloaded, preparing venv...',
                                                         info='',
                                                        )
                    return True
    except Exception as e:
        print(e)
        update_backend_install_progress_info(stage='Fail to download python file, retry may help',
                                             info=f'error: {e}',
                                             )
        traceback.print_exc()
        return False


def write_to_file(file_path: str, content: str):
    try:
        with open(file_path, 'w') as file:
            file.write(content)
            return True
    except Exception as e:
        print("write_to_file error:", e)
        return False


def read_from_file(file_path: str):
    try:
        with open(file_path, 'r') as file:
            content = file.read()
        return content
    except Exception as e:
        print("read_from_file error:", e)
        return None


def clear_directory(folder_path):
    assert isinstance(folder_path, str)
    folder_path = Path(folder_path)

    if folder_path.exists() and folder_path.is_dir():
        for file_path in folder_path.iterdir():
            try:
                if file_path.is_dir():
                    shutil.rmtree(file_path)
                else:
                    file_path.unlink()
            except Exception as e:
                print(f"Failed to delete file: {file_path}: {e}")
    else:
        print(f"Dir not exists: {folder_path}")


def clear_tmp():
    clear_directory(tmp_dir.__str__())


def copy_folder(src, dest):
    try:
        shutil.copytree(src, dest, dirs_exist_ok=True)
    except FileExistsError:
        shutil.rmtree(dest)
        shutil.copytree(src, dest)

def is_folder_exists_and_not_empty(folder_path):
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        return len(os.listdir(folder_path)) > 0
    else:
        return False
def find_available_port(start_port: int, max_port: int = 65535) -> int | None:
    for port in range(start_port, max_port + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    return None
