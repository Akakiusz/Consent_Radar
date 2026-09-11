"""Stage 1: traffic capture (DNS/SNI). To be implemented."""

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