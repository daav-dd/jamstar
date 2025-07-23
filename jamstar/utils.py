from collections.abc import Callable
from functools import wraps
from inspect import signature
from typing import Any

from loguru import logger

from .models import LogLevel


logger.level(LogLevel.SILENT_EXC, no=15, color="<yellow>")


type A = dict[str, Any]


def func_params[T, **P](func: Callable[P, T]) -> Callable[P, A]:
    sig = signature(func)

    @wraps(func_params)
    def inner(*args: P.args, **kwargs: P.kwargs) -> A:
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()
        return dict(bound_args.arguments)

    return inner


type R[T, D] = T | D | None


def catch[T, D, V, **P](
    level: str = LogLevel.SILENT_EXC,
    exc_type: type[BaseException] = Exception,
    reraise: bool = False,
    log_traceback: bool = False,
    default: D | None = None,
    message: str | None = None,
) -> Callable[[Callable[P, T]], Callable[P, R[T, D]]]:
    def decorator(func: Callable[P, T]) -> Callable[P, R[T, D]]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R[T, D]:
            try:
                return func(*args, **kwargs)
            except exc_type as e:
                if message:
                    format_dict: dict[str, Any] = {
                        **func_params(func)(*args, **kwargs),
                        "function_name": func.__name__,
                        "exception": repr(e),
                    }
                    try:
                        log_message = message.format(**format_dict)
                    except KeyError as ke:
                        log_message = (
                            f"Invalid template for {func.__name__}: {message} (missing: {ke}). Exception: {e!r}"
                        )
                    logger.log(level, log_message)

                if reraise:
                    raise

                if log_traceback:
                    logger.exception(f"Exception in {func.__name__}: {e!r}")

                return default

        return wrapper

    return decorator
