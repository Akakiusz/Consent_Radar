"""Stage 1: traffic capture (DNS/SNI) — extract domains from live traffic."""

# Import pyshark for packet capture and analysis
import pyshark

import config
import storage

def _extract_dns(packet) -> str | None:
    """Return the queried domain from a DNS packet, or None."""
    try:
        return packet.dns.qry_name
    except AttributeError:
        return None


def _extract_sni(packet) -> str | None:
    """Return the SNI hostname from a TLS ClientHello, or None."""
    # Field name is often tls.handshake.extensions_server_name;
    # pyshark exposes it with underscores. VERIFY on your system.
    try:
        return packet.tls.handshake_extensions_server_name
    except AttributeError:
        return None

def run(packet_limit: int | None = None):
    """Capture live traffic and store observed domains.

    packet_limit: stop after N packets (None = run until interrupted).
    """
    storage.init_db()

    capture = pyshark.LiveCapture(
        interface=config.CAPTURE_INTERFACE,
        display_filter="dns or tls.handshake.type == 1",
    )

    print(f"Listening on {config.CAPTURE_INTERFACE} … Ctrl+C to stop.")

    count = 0
    try:
        for packet in capture.sniff_continuously(packet_count=packet_limit):
            domain = _extract_dns(packet)
            if domain:
                storage.insert_domain(domain, source="dns")
                print(f"[dns] {domain}")

            sni = _extract_sni(packet)
            if sni:
                storage.insert_domain(sni, source="sni")
                print(f"[sni] {sni}")

            count += 1
    except KeyboardInterrupt:
        print(f"\nStopped. Captured {count} packets.")


if __name__ == "__main__":
    run()