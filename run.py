
Run · PY
"""Consent Radar entry point.
 
Runs the full pipeline end-to-end so one command does everything:
 
    capture  ->  enrich (label trackers)  ->  classify (score anomalies)  ->  dashboard
 
By default it captures a fixed number of packets, then opens the dashboard in
your browser. Press Ctrl+C during capture to stop early and still see results.
"""
 
import webbrowser
 
import capture
import enrich
import classify
 
# How many packets to capture before analysing.
# None = capture until the user presses Ctrl+C.
PACKET_LIMIT = 500
 
DASHBOARD_HOST = "127.0.0.1"
DASHBOARD_PORT = 8050
 
 
def main():
    print("=" * 60)
    print(" Consent Radar — capturing your network traffic")
    print("=" * 60)
    print("Use your apps / browser normally while this runs.")
    print(f"Capturing up to {PACKET_LIMIT} packets (Ctrl+C to stop early).\n")
 
    # Stage 1: capture live traffic into the database.
    try:
        capture.run(packet_limit=PACKET_LIMIT)
    except KeyboardInterrupt:
        print("\nCapture stopped by user.")
 
    # Stage 2: label domains against tracker lists.
    print("\n[2/3] Labelling tracker domains …")
    enrich.write_categories()
 
    # Stage 3: score domains by behaviour (needs >= 3 domains).
    print("[3/3] Scoring domain behaviour …")
    classify.write_scores()
 
    # Stage 4: launch the dashboard.
    url = f"http://{DASHBOARD_HOST}:{DASHBOARD_PORT}"
    print(f"\nOpening dashboard at {url}")
    print("Leave this window open. Press Ctrl+C here to quit.\n")
 
    # Import here so a capture-only run doesn't pay Dash's import cost upfront.
    from dashboard import app
    try:
        webbrowser.open(url)
    except Exception:
        pass
    # debug=False so it runs cleanly as a launched app (no reloader/double-run).
    app.run(host=DASHBOARD_HOST, port=DASHBOARD_PORT, debug=False)
 
 
if __name__ == "__main__":
    main()