# Consent Radar project settings

# Network interface to listen on (verify the name on your system:
# on macOS it's usually en0; check with `ifconfig` or in tshark)
CAPTURE_INTERFACE = None  # None means auto-detect

# Path to tshark.exe (Wireshark's command-line tool).
# Needed on this machine because Wireshark is installed on D:, not in the
# default C:\Program Files location where pyshark looks.
# Set to None to let pyshark find tshark automatically (default install).
TSHARK_PATH = r"D:\Wireshark\tshark.exe"


def get_interface():
    """Return the configured interface, or auto-detect the first live one.

    Falls back to None (pyshark's own default) if detection is unavailable.
    """
    if CAPTURE_INTERFACE:
        return CAPTURE_INTERFACE
    try:
        import pyshark
        # tshark -D equivalent: list interfaces pyshark/tshark can see.
        interfaces = pyshark.tshark.tshark.get_tshark_interfaces(
            tshark_path=TSHARK_PATH
        )
        if interfaces:
            return interfaces[0]
    except Exception:
        pass
    return None  # let pyshark decide


# Paths
DB_PATH = "data/captured.db"
TRACKERS_PATH = "data/trackers.txt"
