## Vanguard Args Interceptor for Windows

>  VGI-WIN64.py is a small Windows helper script that captures the live launch arguments from
> EVEVanguardClient-Win64-Shipping.exe (spawned by the official EVE Launcher) 
> and builds a desktop shortcut to start EVEVanguardClient.exe directly with the same arguments.

This is useful if you want to launch EVE Vanguard without relying on the Shipping bootstrap, while still preserving the correct runtime flags.

## Features

- Watches for EVEVanguardClient-Win64_Shipping.exe when you start Vanguard.

- Captures its exact command-line arguments.

- Creates a desktop shortcut (default: EVE Vanguard (Direct).lnk) that points to:
```
C:\CCP\EVE\eve-vanguard\live\WindowsClient\EVEVanguardClient.exe
```

- Uses a proper .lnk file if pywin32 is installed; otherwise falls back to a .bat file.

- Arguments are faithfully preserved.

## Requirements

- Windows 10/11

- Python 3.7+

- psutil
```
py -m pip install psutil
```

- pywin32
 (optional, for .lnk shortcut creation)
```
py -m pip install pywin32
```

#### NOTE: If pywin32 is not available, the script will create a .bat launcher instead.

## Usage

Make sure Python and dependencies are installed.

Download or clone this repo.

Run the script in a terminal:
```
py VGI-WIN64.py
```

Start EVE Vanguard from the official EVE Launcher.

Once the Shipping process is detected, the script will capture its arguments and create a shortcut on your desktop:

EVE Vanguard (Direct).lnk

Command-line Options
```
--target PATH         Path to EVEVanguardClient.exe 
                      (default: C:\CCP\EVE\eve-vanguard\live\WindowsClient\EVEVanguardClient.exe)
--timeout SECONDS     How long to wait for Shipping.exe (0 = forever, default: 0)
--shortcut-name NAME  File name of the created shortcut (default: "EVE Vanguard (Direct).lnk")
--proc-name NAME      Process name to watch (default: "EVEVanguardClient-Win64_Shipping.exe")
```

### Example:
`
py VGI-WIN64.py --timeout 120 --shortcut-name "Vanguard Direct.lnk"
`
Normal use:
`
py VGI-WIN64.py
`
## Notes

If you want to use a different client install path, pass it via --target.

The script only works on Windows.

If Easy Anti-Cheat or other protections are active, direct launch may not work for online play. This tool is intended for testing, and debugging use cases.


> **Disclaimer:** This tool does **not** modify CCP software. All trademarks and copyrights for EVE / EVE Vanguard belong to CCP hf.  
> This tool does not modify any CCP software. It only observes process arguments and generates a local shortcut on your system.
> This project is not affiliated with or officially endorsed by CCP Games. Use at your own risk; **do not** contact CCP for support.

