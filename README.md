# Jamstar

A Windows utility to control GTA5's network access using Windows Firewall rules. This tool allows you to quickly block and unblock network access for GTA5, useful for certain scenarios.

## Installation

**Requirements:** Python 3.12 or higher

```bash
pip install git+https://github.com/daav-dd/jamstar.git
```

## Usage

### Quick Start

```bash
# Run in interactive mode (recommended for first-time users)
jamstar

# Or use command-line options directly
jamstar --block    # Block network access
jamstar --unblock  # Restore network access
```

### Command Line

```bash
jamstar -h
usage: __main__.py [-h] [-b | -u | -i]

GTA5 Network Control Utility

options:
  -h, --help         show this help message and exit
  -b, --block        Block network access for GTA5
  -u, --unblock      Restore network access for GTA5
  -i, --interactive  Run in interactive mode with global hotkeys
```

### Interactive Mode

When running `jamstar` without arguments, you'll enter interactive mode with:
- Real-time network status display
- Visual feedback for all operations

**Global Hotkeys:**
- `Ctrl+Shift+F1`: Block network access
- `Ctrl+Shift+F2`: Restore network access
- `Ctrl+Shift+Q`: Quit application

## Prerequisites

- **Python Version**: 3.12 or higher
- **Permissions**: Administrator privileges (required for firewall modifications)
- **Game**: Grand Theft Auto V running

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Safety Note

This tool modifies Windows Firewall rules. Use at your own risk.