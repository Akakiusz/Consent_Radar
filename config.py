# Consent Radar project settings
# Locates tshark and the network interface to listen on. Both auto-detect,
# with manual overrides available if detection picks wrong.

import os

# --- tshark location ---
TSHARK_PATH_OVERRIDE = None

_TSHARK_CANDIDATES = [
    r"C:\Program Files\Wireshark\tshark.exe",
    r"C:\Program Files (x86)\Wireshark\tshark.exe",
    r"D:\Wireshark\tshark.exe",
    "/usr/bin/tshark",
    "/opt/homebrew/bin/tshark",
    "/usr/local/bin/tshark",
]


def _find_tshark():
    if TSHARK_PATH_OVERRIDE:
        return TSHARK_PATH_OVERRIDE
    for path in _TSHARK_CANDIDATES:
        if os.path.exists(path):
            return path
    return None


TSHARK_PATH = _find_tshark()

# --- Network interface ---
CAPTURE_INTERFACE = None
_PROBE_SECONDS = 3

_UNLIKELY_FRAGMENTS = (
    "local area connection*",
    "loopback",
    "bluetooth",
    "vmware",
    "virtualbox",
    "vethernet",
    "npcap loopback",
)


def _interface_names():
    import pyshark
    try:
        return pyshark.tshark.tshark.get_all_tshark_interfaces_names(
            tshark_path=TSHARK_PATH
        )
    except Exception:
        return []


def _looks_unlikely(name):
    low = name.lower()
    return any(frag in low for frag in _UNLIKELY_FRAGMENTS)


def _has_traffic(name, probe_seconds=_PROBE_SECONDS):
    import pyshark
    cap = None
    try:
        cap = pyshark.LiveCapture(interface=name, tshark_path=TSHARK_PATH)
        cap.sniff(timeout=probe_seconds, packet_count=1)
        return len(cap) > 0
    except Exception:
        return False
    finally:
        if cap is not None:
            try:
                cap.close()
            except Exception:
                pass


def get_interface():
    if CAPTURE_INTERFACE:
        return CAPTURE_INTERFACE

    names = _interface_names()
    if not names:
        return None

    likely = [n for n in names if not _looks_unlikely(n)]
    unlikely = [n for n in names if _looks_unlikely(n)]
    ordered = likely + unlikely

    print("Detecting your network interface (a few seconds)...", flush=True)
    for name in ordered:
        if _has_traffic(name):
            print(f"  -> using {name}", flush=True)
            return name

    fallback = likely[0] if likely else names[0]
    print(f"  -> no traffic seen while probing; trying {fallback}", flush=True)
    return fallback


# --- Paths ---
DB_PATH = "data/captured.db"
TRACKERS_PATH = "data/trackers.txt"
