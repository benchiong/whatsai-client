"""
 Mostly from: https://github.com/frier-sam/pypi_multi_versions/tree/main , modified.
"""

import os
import sys
import subprocess
from pathlib import Path
from contextlib import contextmanager
from typing import NamedTuple

from misc.whatsai_dirs import base_dir
from misc.logger import logger

base_dir = base_dir / 'custom_dependencies'

def install_version(package_name, version):
    """
    Installs a specific version of a package into the specified directory.
    todo: not perfect yet. some problems:
        1. some package version not showing. eg. tinydb
        2. some package failed, e.g. scipy:  Failed to build installable wheels for some pyproject.toml based projects (numpy)
    """

    try:
        full_package_name = f"{package_name}=={version}"
        path = base_dir / package_name / version
        path.mkdir(parents=True, exist_ok=True)
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", full_package_name, "--target={}".format(path)])
    except subprocess.CalledProcessError as e:
        logger.debug(f"Installation failed: {e}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")

class Dependency(NamedTuple):
    package_name: str
    version: str

@contextmanager
def import_helper(dependencies: list[Dependency]):
    """
    Context manager to temporarily add a package version to sys.path.
    """
    original_sys_path = sys.path.copy()

    for dependency in dependencies:
        package_name = dependency.package_name
        version = dependency.version

        package_path = base_dir / package_name / version
        if not package_path.exists():
            install_version(package_name, version)

        sys.modules.pop(package_name)
        sys.path.insert(0, package_path.__str__())
        print(package_path, sys.path)

    for m in sys.modules:
        if m.startswith('tinydb'):
            print(m)
    try:
        yield
    finally:
        sys.path = original_sys_path

