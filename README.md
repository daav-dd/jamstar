# Jamstar

A Windows utility to control GTA5's network access using Windows Firewall rules. This tool allows you to quickly block and unblock network access for GTA5, useful for certain scenarios.

## Installation

```bash
pip install git+https://github.com/daav-dd/jamstar.git
```

## Usage

### Command Line

```bash
# Interactive mode (default)
jamstar

# Block network access
jamstar -b

# Unblock network access
jamstar -u

# Show help
jamstar -h
```

### Hotkeys

When running in interactive mode:
- `Ctrl+Shift+F1`: Block network access
- `Ctrl+Shift+F2`: Restore network access
- `Ctrl+Shift+Q`: Quit application

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Safety Note

This tool modifies Windows Firewall rules. Use at your own risk.