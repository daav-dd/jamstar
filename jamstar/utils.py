from collections.abc import Callable
from functools import wraps
from inspect import signature
from typing import Any

from loguru import logger

from .models import LogLevels


def catch[T, DefaultT, **P](
    level: str = LogLevels.SILENT_EXC,
    default: DefaultT | None = None,
    message: str | None = None,
) -> Callable[[Callable[P, T]], Callable[P, T | DefaultT | None]]:
    def decorator(func: Callable[P, T]) -> Callable[P, T | DefaultT | None]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T | DefaultT | None:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if not message:
                    return default

                sig = signature(func)
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()
                params = dict(bound_args.arguments)

                format_dict: dict[str, Any] = {
                    **params,
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
