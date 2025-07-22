from enum import Enum, StrEnum, auto


class ExecutionMode(Enum):
    VENV_SOURCE = auto()
    INSTALLED_PACKAGE = auto()


class LogLevel(StrEnum):
    SILENT_EXC = "SILENT_EXC"
