"""Stage 2: tracker enrichment — flag each domain against public tracker lists."""

# Import standard libraries
import config
import storage

# Load a public tracker list from a hosts-style file into a set of domains.
def load_trackers(path="data/trackers_raw.txt"):
    """Parse a hosts-style blocklist into a set of tracker domains.

    Expected line format: '0.0.0.0 tracker.example.com'
    Lines that are comments (#) or blank are skipped.
    """
    trackers = set()
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            # hosts format: <ip> <domain>. Take the domain if present.
            if len(parts) >= 2:
                trackers.add(parts[1].lower())
    return trackers

# Check if a domain or any of its parent domains are in the tracker set.
def is_tracker(domain, trackers):
    """True if the domain, or any parent domain, is in the tracker set.

    e.g. 'mobile.events.data.microsoft.com' matches if
    'events.data.microsoft.com' is listed.
    """
    domain = domain.lower()
    parts = domain.split(".")
    # check the full domain and each parent suffix
    for i in range(len(parts) - 1):
        candidate = ".".join(parts[i:])
        if candidate in trackers:
            return True
    return False

# Categorise a domain as 'tracker' or 'other' based on the tracker list.
def categorise(domain, trackers):
    """Return a simple category label for a domain."""
    return "tracker" if is_tracker(domain, trackers) else "other"

# Enrich all captured domains, categorise them, and print a summary.
def enrich_all():
    """Read distinct captured domains, label them, print a summary."""
    trackers = load_trackers()
    rows = storage.fetch_all()

    seen = {}
    for _ts, domain, _source, _cat in rows:
        if domain not in seen:
            seen[domain] = categorise(domain, trackers)

    tracker_count = sum(1 for c in seen.values() if c == "tracker")
    print(f"Loaded {len(trackers)} tracker domains.")
    print(f"Distinct domains seen: {len(seen)}")
    print(f"Flagged as tracker:    {tracker_count}")
    print()
    for domain, cat in sorted(seen.items(), key=lambda x: x[1]):
        mark = "🚩" if cat == "tracker" else "  "
        print(f"{mark} [{cat:7}] {domain}")

# Persist tracker/other labels back into the database.
def write_categories():
    """Label every distinct captured domain and save it to the DB."""
    trackers = load_trackers()
    rows = storage.fetch_all()
    seen = {domain: categorise(domain, trackers)
            for _ts, domain, _source, _cat in rows}
    for domain, cat in seen.items():
        storage.update_category(domain, cat)
    print(f"Updated categories for {len(seen)} distinct domains.")

# Run the enrichment process if this script is executed directly.
if __name__ == "__main__":
    enrich_all()
    write_categories()