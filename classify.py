"""Stage 3: behavioural analysis — surface telemetry-like domains by how they
behave (frequency, time-span, regularity), not by blocklist membership.
"""
# Import standard libraries
from datetime import datetime

import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

import storage

# Parse ISO timestamp strings into datetime objects.
def _parse(ts):
    """Parse an ISO timestamp string to a datetime."""
    return datetime.fromisoformat(ts)

# Extract behavioural features from captured rows.
def extract_features():
    """Turn captured rows into per-domain behavioural features.

    Returns (domains, feature_matrix) where each row is:
      [count, span_seconds, rate_per_min, regularity]
    - count:       total contacts
    - span:        seconds between first and last contact
    - rate:        contacts per minute over that span
    - regularity:  1 / (1 + std of gaps between contacts); higher = steadier.
                   A regular heartbeat scores high; a single burst scores low.
    """
    rows = storage.fetch_all()

    # group timestamps by domain
    by_domain = {}
    for ts, domain, _source, _cat in rows:
        by_domain.setdefault(domain, []).append(_parse(ts))

    domains, feats = [], []
    for domain, times in by_domain.items():
        times.sort()
        count = len(times)
        span = (times[-1] - times[0]).total_seconds()
        # rate is only meaningful over a real time window; sub-second spans
        # produce misleading spikes, so treat them as "no meaningful rate"
        rate = count / (span / 60) if span >= 1.0 else 0.0

        # regularity from gaps between consecutive contacts
        if count > 2 and span > 0:
            gaps = np.diff([t.timestamp() for t in times])
            regularity = 1.0 / (1.0 + np.std(gaps))
        else:
            regularity = 0.0  # too few points / no span to judge

        domains.append(domain)
        feats.append([count, span, rate, regularity])

    return domains, np.array(feats, dtype=float)

# Option B: anomaly score per domain (higher = more outlier-like).
def run_isolation_forest(features):
    """Anomaly score per domain (higher = more outlier-like)."""
    X = StandardScaler().fit_transform(features)
    model = IsolationForest(random_state=42, contamination="auto")
    model.fit(X)
    # score_samples: lower = more anomalous. Negate so higher = more anomalous.
    return -model.score_samples(X)

# Option A: behavioural cluster label per domain.
def run_clustering(features, n_clusters=3):
    """Cluster label per domain. With few domains, treat as illustrative."""
    X = StandardScaler().fit_transform(features)
    k = min(n_clusters, len(features))  # can't have more clusters than points
    model = KMeans(n_clusters=k, random_state=42, n_init=10)
    return model.fit_predict(X)

# Print a summary of anomaly scores and clusters, sorted by anomaly.
def main():
    domains, features = extract_features()
    if len(domains) < 3:
        print("Not enough domains for meaningful analysis.")
        return

    anomaly = run_isolation_forest(features)
    clusters = run_clustering(features)

    # sort by anomaly score, most anomalous first
    order = np.argsort(-anomaly)

    print(f"{'domain':45} {'count':>6} {'span_s':>8} "
          f"{'rate/m':>7} {'reg':>5} {'anom':>6} {'clust':>5}")
    print("-" * 90)
    for i in order:
        c, s, r, reg = features[i]
        print(f"{domains[i]:45} {int(c):>6} {s:>8.0f} "
              f"{r:>7.1f} {reg:>5.2f} {anomaly[i]:>6.2f} {clusters[i]:>5}")

    print("\nNote: 'anom' = review-priority (higher = more unusual pattern). "
          "'clust' = behavioural group. Small sample — triage aid, not a verdict.")

# Persist anomaly scores to the DB so the dashboard can read them.
def write_scores():
    """Save each domain's anomaly score to the database."""
    domains, features = extract_features()
    if len(domains) < 3:
        print("Not enough domains to score.")
        return
    anomaly = run_isolation_forest(features)
    for domain, score in zip(domains, anomaly):
        storage.update_score(domain, float(score))
    print(f"Saved anomaly scores for {len(domains)} domains.")


if __name__ == "__main__":
    main()
    write_scores()