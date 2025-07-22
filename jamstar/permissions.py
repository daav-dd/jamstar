import ctypes
import sys

from importlib.util import find_spec
from pathlib import Path

from loguru import logger

from .exceptions import AdminRightsError
from .models import ExecutionMode


class EnvironmentManager:
    @staticmethod
    def get_venv_path() -> Path | None:
        return Path(sys.prefix).resolve() if sys.prefix != sys.base_prefix else None

    @staticmethod
    def get_python_executable(venv_path: Path | None = None) -> Path:
        if venv_path:
            return venv_path / "Scripts" / "python.exe"
        return Path(sys.executable).resolve()

    @staticmethod
    def is_package_installed(package_name: str) -> bool:
        try:
            return find_spec(package_name) is not None
        except Exception as e:
            logger.warning(f"Failed to check if {package_name} is installed: {e!r}")
            return False

    @staticmethod
    def get_execution_mode(package_name: str, force_installed: bool = False) -> tuple[ExecutionMode, Path | None]:
        venv_path = EnvironmentManager.get_venv_path()
        is_installed = EnvironmentManager.is_package_installed(package_name)

        if venv_path and not force_installed:
            return ExecutionMode.VENV_SOURCE, venv_path
        elif is_installed:
            return ExecutionMode.INSTALLED_PACKAGE, None
        else:
            raise AdminRightsError(f"Package '{package_name}' is not installed.")


class AdminRightsManager:
    @staticmethod
    def is_admin() -> bool:
        try:
            return bool(ctypes.windll.shell32.IsUserAnAdmin())
        except Exception as e:
            logger.warning(f"Failed to check admin rights: {e!r}")
            return False

    @staticmethod
    def request_elevation() -> bool:
        print("This application needs to run with elevated rights.")
        response = input("Request for elevated rights? [y/(n)]: ")
        return response.strip().lower() == "y"

    @classmethod
    def restart_with_admin(cls, package_name: str, force_installed: bool = False) -> None:
        """
        Args:
            package_name: The name of the package
            force_installed: If True, forces using the installed package even in a venv
        """

        args = " ".join(sys.argv[1:])
        execution_mode, venv_path = EnvironmentManager.get_execution_mode(package_name, force_installed)
        executable = EnvironmentManager.get_python_executable(venv_path)

        if execution_mode == ExecutionMode.VENV_SOURCE:
            source_path = Path(__file__).resolve().parent.name
            cmd = f"-m {source_path} {args}"
        elif execution_mode == ExecutionMode.INSTALLED_PACKAGE:
            cmd = f"-m {package_name} {args}"
        else:
            raise AdminRightsError(f"Unsupported execution mode: {execution_mode}")

        try:
            logger.info(f"Executing with elevated rights: {executable} {cmd}")
            ctypes.windll.shell32.ShellExecuteW(None, "runas", str(executable), cmd, None, 1)

            sys.exit(0)
        except Exception as e:
            raise AdminRightsError(f"Failed to restart with admin rights: {e!r}") from None


def check_admin_rights(package_name: str = "jamstar", force_installed: bool = False) -> None:
    if AdminRightsManager.is_admin():
        return

    if AdminRightsManager.request_elevation():
        logger.info("Requesting administrator privileges...")
        AdminRightsManager.restart_with_admin(package_name, force_installed)
    else:
        print("Operation cancelled. Exiting...")
        sys.exit(0)


if __name__ == "__main__":
    check_admin_rights()
