from enum import Enum, auto


class ExecutionMode(Enum):
    VENV_SOURCE = auto()
    INSTALLED_PACKAGE = auto()
