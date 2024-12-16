from importlib import import_module
from pathlib import Path
from sys import path
from typing import Optional, Union

from src.base.logger import logger


class WithSystemPath:
    def __init__(self, module_path: Union[Path, str]) -> None:
        if isinstance(module_path, str):
            self._module_path = Path(module_path)
        else:
            self._module_path = module_path

    def __enter__(self):
        path.append(str(self._module_path))
        return self._module_path

    def __exit__(self, exc_type, exc_val, exc_tb):
        path.remove(str(self._module_path))
        if exc_tb:
            logger.error(exc_val)


def dynamic_import_all(module_path: str, expect_module_name: Optional[list[str]] = None) -> None:
    if expect_module_name is None:
        expect_module_name = []

    with WithSystemPath(module_path) as module_dir:
        if not module_dir.is_dir():
            logger.error(f"The path {module_path} is not a valid directory.")
            return
        py_files = module_dir.glob('*.py')
        for py_file in py_files:
            module_name = py_file.stem
            if module_name == "__init__" or py_file.name in expect_module_name or module_name in expect_module_name:
                continue
            try:
                import_module(module_name)
                logger.success(f"Successfully imported {module_name}")
            except ModuleNotFoundError:
                logger.error(f"Module {module_name} not found")
            except ImportError as e:
                logger.error(f"Failed to import {module_name}: {e}")
