#!/usr/bin/env python3
import argparse
import os
import platform
import sys
import time
import subprocess

# psutil is the most reliable way to get another process's command line
try:
    import psutil
except ImportError:
    print("ERROR: This script requires 'psutil'. Install with: pip install psutil", file=sys.stderr)
    sys.exit(1)

try:
    from win32com.client import Dispatch
    HAVE_WIN32 = True
except Exception:
    Dispatch = None
    HAVE_WIN32 = False


DEFAULT_TARGET = r"C:\CCP\EVE\eve-vanguard\live\WindowsClient\EVEVanguardClient.exe"
SHIPPING_EXE = "EVEVanguardClient-Win64-Shipping.exe"


def windows_desktop() -> str:
    userprofile = os.environ.get("USERPROFILE") or os.path.expanduser("~")
    return os.path.join(userprofile, "Desktop")


def list2cmdline(args_list):
    return subprocess.list2cmdline(args_list)


def find_shipping_cmdline(proc_name: str, timeout: int, poll_sec: float = 1.0):
    """
    Wait up to `timeout` seconds for a process with name `proc_name`.
    Return its full cmdline list (argv[0] ... argv[n]) when found.
    """
    deadline = time.time() + timeout if timeout > 0 else None
    while True:

        for p in psutil.process_iter(attrs=["name", "cmdline"]):
            try:
                if p.info["name"] and p.info["name"].lower() == proc_name.lower():
                    cmdline = p.info["cmdline"] or []

                    if cmdline:
                        return cmdline
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if deadline and time.time() > deadline:
            return None
        time.sleep(poll_sec)


def create_lnk(shortcut_path: str, target: str, args_str: str, working_dir: str, icon_path: str = None):
        shell = Dispatch("WScript.Shell")
        shortcut = shell.CreateShortcut(shortcut_path)
        shortcut.TargetPath = target
        shortcut.Arguments = args_str
        shortcut.WorkingDirectory = working_dir
        if icon_path and os.path.exists(icon_path):
            shortcut.IconLocation = icon_path
        shortcut.Save()


def create_bat(fpath: str, target: str, args_str: str, working_dir: str):

    with open(fpath, "w", encoding="utf-8") as f:
        f.write("@echo off\n")
        f.write(f'pushd "{working_dir}"\n')
        f.write(f'start "" "{target}" {args_str}\n')


def main():
    if platform.system() != "Windows":
        print("This script is Windows-only.", file=sys.stderr)
        sys.exit(2)

    ap = argparse.ArgumentParser(
        description="Capture live Vanguard Shipping.exe launch args and make a desktop shortcut to EVEVanguardClient.exe with them."
    )
    ap.add_argument("--target", default=DEFAULT_TARGET,
                    help=f'Path to EVEVanguardClient.exe (default: "{DEFAULT_TARGET}")')
    ap.add_argument("--timeout", type=int, default=0,
                    help="Seconds to wait for Shipping.exe (0 = wait forever).")
    ap.add_argument("--shortcut-name", default="EVE Vanguard (Direct).lnk",
                    help='Shortcut file name (default: "EVE Vanguard (Direct).lnk").')
    ap.add_argument("--proc-name", default=SHIPPING_EXE,
                    help=f'Process name to watch (default: "{SHIPPING_EXE}")')

    args = ap.parse_args()

    target_exe = os.path.abspath(args.target)
    if not os.path.isfile(target_exe):
        print(f'ERROR: Target not found: "{target_exe}"', file=sys.stderr)
        sys.exit(3)

    print(f'Watching for process: {args.proc_name}')
    cmdline = find_shipping_cmdline(args.proc_name, timeout=args.timeout)

    if not cmdline:
        print("ERROR: Timed out waiting for Shipping.exe. Launch Vanguard from the EVE Launcher first.", file=sys.stderr)
        sys.exit(4)

    passthrough_args = cmdline[1:] if len(cmdline) >= 2 else []

    args_str = list2cmdline(passthrough_args)
    print("Captured arguments:")
    print(args_str if args_str else "(none)")

    desktop = windows_desktop()
    os.makedirs(desktop, exist_ok=True)

    working_dir = os.path.dirname(target_exe)
    icon_path = target_exe
    shortcut_name = args.shortcut_name
    shortcut_path = os.path.join(desktop, shortcut_name)

    if HAVE_WIN32 and shortcut_path.lower().endswith(".lnk"):
        try:
            create_lnk(shortcut_path, target_exe, args_str, working_dir, icon_path)
            print(f'Shortcut created: {shortcut_path}')
        except Exception as e:
            print(f"Failed to create .lnk ({e}), falling back to .bat…")
            bat_path = os.path.splitext(shortcut_path)[0] + ".bat"
            create_bat(bat_path, target_exe, args_str, working_dir)
            print(f'Launcher created: {bat_path}')
    else:
        # Either pywin32 missing or user requested non-.lnk name; write a .bat instead
        if not shortcut_path.lower().endswith(".bat"):
            shortcut_path = os.path.splitext(shortcut_path)[0] + ".bat"
        create_bat(shortcut_path, target_exe, args_str, working_dir)
        print(f'Launcher created: {shortcut_path}')

    print("Done.")


if __name__ == "__main__":
    main()
