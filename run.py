"""Consent Radar entry point.

Runs the full pipeline end-to-end so one command does everything:
    capture -> enrich -> classify -> dashboard
"""

import webbrowser

import capture
import enrich
import classify

PACKET_LIMIT = 500
DASHBOARD_HOST = "127.0.0.1"
DASHBOARD_PORT = 8050


def main():
    print("=" * 60)
    print(" Consent Radar - capturing your network traffic")
    print("=" * 60)
    print("Use your apps / browser normally while this runs.")
    print(f"Capturing up to {PACKET_LIMIT} packets (Ctrl+C to stop early).\n")

    try:
        capture.run(packet_limit=PACKET_LIMIT)
    except KeyboardInterrupt:
        print("\nCapture stopped by user.")

    print("\n[2/3] Labelling tracker domains ...")
    enrich.write_categories()

    print("[3/3] Scoring domain behaviour ...")
    classify.write_scores()

    url = f"http://{DASHBOARD_HOST}:{DASHBOARD_PORT}"
    print(f"\nOpening dashboard at {url}")
    print("Leave this window open. Press Ctrl+C here to quit.\n")

    from dashboard import app
    try:
        webbrowser.open(url)
    except Exception:
        pass
    app.run(host=DASHBOARD_HOST, port=DASHBOARD_PORT, debug=False)


if __name__ == "__main__":
    main()
