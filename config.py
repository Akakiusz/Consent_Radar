# Consent Radar project settings
#
# This file locates tshark (Wireshark's CLI) and the network interface to
# listen on. Both are auto-detected so the project runs on other machines,
# with manual overrides available if detection picks wrong.
 
import os
 
# --- tshark location -------------------------------------------------------
# Set a path here to force a specific tshark.exe. Leave as None to auto-detect
# from the common install locations below.
TSHARK_PATH_OVERRIDE = None
 
# Common places Wireshark installs tshark.exe. First one that exists wins.
_TSHARK_CANDIDATES = [
    r"C:\Program Files\Wireshark\tshark.exe",
    r"C:\Program Files (x86)\Wireshark\tshark.exe",
    r"D:\Wireshark\tshark.exe",
    "/usr/bin/tshark",            # Linux
    "/opt/homebrew/bin/tshark",   # macOS (Apple Silicon)
    "/usr/local/bin/tshark",      # macOS (Intel)
]
 
 
def _find_tshark():
    """Return a tshark path that exists, or None to let pyshark search itself."""
    if TSHARK_PATH_OVERRIDE:
        return TSHARK_PATH_OVERRIDE
    for path in _TSHARK_CANDIDATES:
        if os.path.exists(path):
            return path
    return None  # pyshark will fall back to its own default search
 
 
# Resolved once at import so capture.py and get_interface() share it.
TSHARK_PATH = _find_tshark()
 
 
# --- Network interface -----------------------------------------------------
# Set a name here (as shown by `tshark -D`, e.g. "WiFi" or "Ethernet") to force
# a specific interface. Leave as None to auto-detect the one with live traffic.
CAPTURE_INTERFACE = None
 
 
def _interface_names():
    """All interface names tshark can see, in tshark -D order."""
    import pyshark
    try:
        return pyshark.tshark.tshark.get_all_tshark_interfaces_names(
            tshark_path=TSHARK_PATH
        )
    except Exception:
        return []
 
 
def _has_traffic(name, probe_seconds=2):
    """True if at least one packet is seen on `name` within probe_seconds."""
    import pyshark
    try:
        cap = pyshark.LiveCapture(interface=name, tshark_path=TSHARK_PATH)
        for _ in cap.sniff_continuously(packet_count=1):
            cap.close()
            return True
    except Exception:
        pass
    return False
 
 
def get_interface():
    """Return the interface to capture on.
 
    Order of preference:
      1. CAPTURE_INTERFACE if set manually.
      2. The first interface that actually shows live traffic (a quick probe).
      3. The first interface tshark lists (last-resort fallback).
    """
    if CAPTURE_INTERFACE:
        return CAPTURE_INTERFACE
 
    names = _interface_names()
    if not names:
        return None  # let pyshark decide
 
    # Probe each interface briefly; pick the first with traffic.
    for name in names:
        if _has_traffic(name):
            return name
 
    # Nothing had traffic in the probe window; fall back to the first listed.
    return names[0]
 
 
# --- Paths -----------------------------------------------------------------
DB_PATH = "data/captured.db"
TRACKERS_PATH = "data/trackers.txt"