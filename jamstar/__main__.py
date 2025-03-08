import argparse
import signal
import sys
import threading
import tkinter as tk
from typing import Optional

import keyboard
import psutil
import pythoncom
import win32com.client
from loguru import logger

from .permissions import check_admin_rights


class FirewallController:
    def __init__(self):
        self.fw_policy = None

    def __enter__(self):
        pythoncom.CoInitialize()
        self.fw_policy = win32com.client.Dispatch("HNetCfg.FwPolicy2")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pythoncom.CoUninitialize()

    def rule_exists(self, rule_name: str) -> bool:
        try:
            self.fw_policy.Rules.Item(rule_name)
            return True
        except Exception:
            return False

    def create_block_rule(
        self,
        rule_name: str,
        description: str,
        # application_path: str = "",
        blocked_ip: str = "192.81.241.171",
    ):
        rule = win32com.client.Dispatch("HNetCfg.FwRule")
        rule.Name = rule_name
        rule.Description = description
        # rule.ApplicationName = application_path
        rule.Action = 0  # block
        rule.Direction = 2  # outbound
        rule.Enabled = True
        rule.RemoteAddresses = blocked_ip
        self.fw_policy.Rules.Add(rule)

    def remove_rule(self, rule_name: str):
        if self.rule_exists(rule_name):
            self.fw_policy.Rules.Remove(rule_name)


class NotificationWindow:
    def __init__(self):
        self.window: Optional[tk.Tk] = None
        self.label: Optional[tk.Label] = None

    def create_window(self, message: str = ""):
        if self.window:
            try:
                self.window.destroy()
            except tk.TclError:
                pass

        self.window = tk.Tk()
        self.window.overrideredirect(True)
        self.window.geometry("+0+0")

        self.window.wm_attributes("-topmost", True)

        self.label = tk.Label(self.window, text=message, font=("Arial", 12), fg="black")
        self.label.pack()

    def show(self, message: str):
        if not self.window:
            self.create_window(message)

        try:
            # cancel all pending withdraw timers
            for after_id in self.window.tk.call("after", "info"):
                self.window.after_cancel(after_id)

            self.window.deiconify()
            self.label.config(text=message)
            self.window.after(5000, self.window.withdraw)
        except (tk.TclError, AttributeError):
            self.create_window(message)

    def destroy(self):
        if self.window:
            self.window.destroy()


class NetworkController:
    PROCS_NAMES = "GTA5.exe", "GTA5_Enhanced.exe"
    RULE_NAME = "Block_GTA5_Network"

    def __init__(self):
        self.notification = NotificationWindow()
        self.is_blocked: bool = False
        self.hotkey_thread: Optional[threading.Thread] = None

    def _find_process(self) -> Optional[psutil.Process]:
        for proc in psutil.process_iter(["name", "exe"]):
            try:
                if all(proc.info["name"].lower() != name.lower() for name in self.PROCS_NAMES):
                    continue
                return proc
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

    def block_network_access(self):
        process = self._find_process()
        if not process:
            self.notification.show("GTA5 is not running")
            logger.warning("GTA5 is not running")
            return

        with FirewallController() as fw:
            if fw.rule_exists(self.RULE_NAME):
                self.notification.show("Network already blocked")
                logger.info("Firewall rule already exists")
                return

            fw.create_block_rule(rule_name=self.RULE_NAME, description="Block network access for GTA5")

        self.is_blocked = True
        self.notification.show("Network blocked successfully")
        logger.success("Network access blocked successfully")

    def restore_network_access(self):
        with FirewallController() as fw:
            if not fw.rule_exists(self.RULE_NAME):
                self.notification.show("No matching firewall rule found")
                logger.info("No matching firewall rule found")
                return

            fw.remove_rule(self.RULE_NAME)

        self.is_blocked = False
        self.notification.show("Network restored successfully")
        logger.success("Network access restored successfully")

    def setup_hotkeys(self):
        keyboard.add_hotkey("ctrl+shift+f1", self.block_network_access)
        keyboard.add_hotkey("ctrl+shift+f2", self.restore_network_access)
        keyboard.add_hotkey("ctrl+shift+q", self.cleanup)
        keyboard.wait()

    def cleanup(self):
        logger.info("Cleaning up...")
        try:
            keyboard.unhook_all()

            if self.notification:
                self.notification.destroy()

            if self.is_blocked:
                self.restore_network_access()

            if self.hotkey_thread:
                self.hotkey_thread.join(timeout=1.0)

        except Exception as e:
            logger.error(f"Error during cleanup: {e!r}")
        finally:
            signal.raise_signal(signal.SIGTERM)

    def run_interactive(self):
        logger.info("Starting interactive mode")
        self.notification.show("Ctrl+Shift+\nF1 to block\nF2 to unblock\nQ to exit")
        logger.info("Global hotkeys: Ctrl+Shift+<F1> to block, <F2> to unblock, <Q> to exit")

        self.hotkey_thread = threading.Thread(target=self.setup_hotkeys, daemon=True)
        self.hotkey_thread.start()

        if self.notification.window:
            self.notification.window.mainloop()


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="GTA5 Network Control Utility")

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-b",
        "--block",
        action="store_true",
        help="Block network access for GTA5",
    )
    group.add_argument(
        "-u",
        "--unblock",
        action="store_true",
        help="Restore network access for GTA5",
    )
    group.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Run in interactive mode with global hotkeys",
    )

    return parser.parse_args()


def main():
    args = parse_arguments()
    check_admin_rights(force_installed=True)

    controller = NetworkController()

    try:
        if args.block:
            controller.block_network_access()
        elif args.unblock:
            controller.restore_network_access()
        else:
            controller.run_interactive()
    except Exception as e:
        logger.exception(f"An error occurred: {e!r}")
        sys.exit(1)


if __name__ == "__main__":
    main()
