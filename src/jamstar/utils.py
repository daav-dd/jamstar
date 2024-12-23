import ctypes
import os
import sys
from pathlib import Path

from loguru import logger

from .exceptions import AdminRightsError


def restart_with_admin():
    try:
        try:
            import jamstar

            package_path = Path(jamstar.__file__).parent
            is_installed = "site-packages" in str(package_path)
        except ImportError:
            is_installed = False

        if is_installed:
            executable = sys.executable
            cmd = f'-m jamstar {" ".join(sys.argv[1:])}'
        else:
            # running in development
            if "VIRTUAL_ENV" not in os.environ:
                raise RuntimeError(
                    "Enter venv before running the script in development mode"
                )

            venv = Path(os.environ.get("VIRTUAL_ENV")).resolve()
            executable = str(venv / "Scripts" / "python.exe")
            script_path = Path(sys.argv[0]).resolve()
            cmd = f'"{script_path}" {" ".join(sys.argv[1:])}'

        ctypes.windll.shell32.ShellExecuteW(None, "runas", executable, cmd, None, 1)
        sys.exit(0)

    except Exception as e:
        raise AdminRightsError(f"Failed to restart with admin rights: {e!r}")


def check_admin_rights():
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        is_admin = False

    if is_admin:
        return

    print("This application needs to run with elevated rights.")
    while True:
        response = input("Request for elevated rights? [y/(n)]: ").strip().lower()
        if response == "y":
            logger.info("Requesting administrator privileges...")
            restart_with_admin()
        else:
            print("Operation cancelled. Exiting...")
            sys.exit(0)
