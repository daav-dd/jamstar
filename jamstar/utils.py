from collections.abc import Callable
from functools import wraps
from inspect import signature
from typing import Any

from loguru import logger

from .models import LogLevel


type R = dict[str, Any]


def func_params[T, **P](func: Callable[P, T]) -> Callable[P, R]:
    sig = signature(func)

    def inner(*args: P.args, **kwargs: P.kwargs) -> R:
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()
        return dict(bound_args.arguments)

    return inner


def catch[T, **P](
    level: str = LogLevel.SILENT_EXC,
    default: T | None = None,
    message: str | None = None,
) -> Callable[[Callable[P, T]], Callable[P, T | None]]:
    def decorator(func: Callable[P, T]) -> Callable[P, T | None]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T | None:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if not message:
                    return default

                format_dict: dict[str, Any] = {
                    **func_params(func)(*args, **kwargs),
                    "function_name": func.__name__,
                    "exception": repr(e),
                }
                try:
                    log_message = message.format(**format_dict)
                except KeyError as ke:
                    log_message = f"Invalid template for {func.__name__}: {message} (missing: {ke}). Exception: {e!r}"
                logger.log(level, log_message)

                return default

        return wrapper

    return decorator
