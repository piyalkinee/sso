import os
import sys
import uuid
import inspect
import importlib
import traceback

from loguru import logger
from functools import wraps
from ..exceptions import http


def get_classes_from_module(module):
    cl_list = inspect.getmembers(module, inspect.isclass)
    return cl_list


def inspect_modules_in_directory(dir_path: str) -> dict:
    module_errors = {}
    for root, _, files in os.walk(dir_path):
        for file in files:
            if file.endswith(".py") and file not in ("__init__.py", "endpoint_errors.py"):
                module_name = file[:-3]
                root_dir_name = os.getcwd().split("/")[-1]
                module_full_name = f"{root_dir_name}.exceptions.{module_name}"
                try:
                    module = importlib.import_module(module_full_name)
                    module_errors[module_name] = get_classes_from_module(module)
                except Exception as e:
                    logger.debug("In inspect modules [middleware/exceptions.py]")
                    logger.error(f"Failed to import module {module_full_name}: {e}")
    return module_errors


def exception_handler(function):

    @wraps(function)
    async def inner_wrapper(*args, **kwargs):
        try:
            logger.debug("Error executor handler")
            res = await function(*args, **kwargs)
            return res
        except BaseException as e:
            # Take error info
            exc_type, exc_value, exc_traceback = sys.exc_info()
            q = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            error_doc = exc_type.__doc__
            error_name = exc_type.__name__
            error_module = exc_type.__module__

            x_code = str(uuid.uuid4())
            msg = f"Error {x_code}: {error_name}/{error_doc} {exc_value}"
            logger.error(f"In {function.__module__}/{function.__name__} \n{msg}\n{q}")

            # Check error in exceptions module
            error_modules = inspect_modules_in_directory("exceptions")
            for module_name, module in error_modules.items():
                if error_module.split(".")[-1] == module_name:
                    for class_name, class_obj in module:
                        if error_name == class_name:
                            raise e

            # Raise 500 error if module is not found
            raise http.HTTPInternalError(
                detail=dict(
                    message=str(exc_value), x_code=x_code, name=error_name, doc=str(error_doc)
                )
            ) from e

    return inner_wrapper