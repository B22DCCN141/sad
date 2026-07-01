from __future__ import annotations

import csv
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path


OUTPUT_FILE = Path(__file__).with_name("data_user500.csv")
SEED = 42
USER_COUNT = 900
SESSION_COUNT_RANGE = (2, 4)
EVENTS_PER_SESSION_RANGE = (4, 7)
PRODUCT_ID_MIN = 1
PRODUCT_ID_MAX = 300
ACTION_CHOICES = ["view", "click", "add_to_cart"]
PERSONAS = {
    "browser": {
        "session_bias": 0.50,
        "action_weights": [0.80, 0.17, 0.03],
        "stay_probability": 0.76,
        "neighbor_probability": 0.18,
    },
    "researcher": {
        "session_bias": 0.74,
        "action_weights": [0.70, 0.24, 0.06],
        "stay_probability": 0.62,
        "neighbor_probability": 0.30,
    },
    "buyer": {
        "session_bias": 0.93,
        "action_weights": [0.45, 0.28, 0.27],
        "stay_probability": 0.48,
        "neighbor_probability": 0.35,
    },
    "loyal": {
        "session_bias": 0.87,
        "action_weights": [0.54, 0.29, 0.17],
        "stay_probability": 0.68,
        "neighbor_probability": 0.24,
    },
}
CLUSTER_SIZE = 10


def build_clusters() -> list[list[int]]:
    clusters: list[list[int]] = []
    for start in range(PRODUCT_ID_MIN, PRODUCT_ID_MAX + 1, CLUSTER_SIZE):
        clusters.append(list(range(start, min(start + CLUSTER_SIZE, PRODUCT_ID_MAX + 1))))
    return clusters


def choose_persona(rng: random.Random) -> str:
    return rng.choices(list(PERSONAS.keys()), weights=[0.40, 0.26, 0.19, 0.15], k=1)[0]


def pick_product(
    rng: random.Random,
    clusters: list[list[int]],
    primary_cluster: int,
    persona: str,
    last_product: int | None,
) -> int:
    config = PERSONAS[persona]
    if last_product is not None and rng.random() < config["stay_probability"]:
        return last_product

    cluster_candidates = [primary_cluster]
    if rng.random() < config["neighbor_probability"]:
        if primary_cluster > 0:
            cluster_candidates.append(primary_cluster - 1)
        if primary_cluster < len(clusters) - 1:
            cluster_candidates.append(primary_cluster + 1)

    chosen_cluster = rng.choice(cluster_candidates)
    return rng.choice(clusters[chosen_cluster])


def build_rows() -> list[dict[str, str]]:
    rng = random.Random(SEED)
    rows: list[dict[str, str]] = []
    base_timestamp = datetime(2026, 1, 1, 8, 0, 0, tzinfo=timezone.utc)
    clusters = build_clusters()

    for user_id in range(1, USER_COUNT + 1):
        persona = choose_persona(rng)
        config = PERSONAS[persona]
        primary_cluster = (user_id * 7 + rng.randint(0, len(clusters) - 1)) % len(clusters)
        current_timestamp = base_timestamp + timedelta(days=user_id % 30, minutes=user_id)
        session_count = rng.randint(*SESSION_COUNT_RANGE)
        if rng.random() < config["session_bias"]:
            session_count = min(SESSION_COUNT_RANGE[1], session_count + 1)

        for session_index in range(session_count):
            if session_index > 0:
                current_timestamp += timedelta(minutes=rng.randint(60, 360))

            event_count = rng.randint(*EVENTS_PER_SESSION_RANGE)
            last_product: int | None = None
            session_entry_product = rng.choice(clusters[primary_cluster])

            for event_index in range(event_count):
                if event_index > 0:
                    current_timestamp += timedelta(minutes=rng.randint(4, 45))

                if event_index == 0:
                    product_id = session_entry_product
                else:
                    product_id = pick_product(rng, clusters, primary_cluster, persona, last_product)

                action_weights = config["action_weights"]
                if event_index >= event_count - 2 and persona in {"buyer", "loyal"}:
                    action_weights = [0.35, 0.25, 0.40]
                elif event_index >= event_count - 1 and persona == "researcher":
                    action_weights = [0.55, 0.32, 0.13]

                action = rng.choices(ACTION_CHOICES, weights=action_weights, k=1)[0]
                if event_index > 0 and last_product == product_id and action == "view" and rng.random() < 0.50:
                    action = "click"

                rows.append(
                    {
                        "user_id": str(user_id),
                        "product_id": str(product_id),
                        "action": action,
                        "timestamp": current_timestamp.isoformat().replace("+00:00", "Z"),
                    }
                )
                last_product = product_id

    return rows


def write_csv(output_file: Path) -> None:
    rows = build_rows()
    with output_file.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["user_id", "product_id", "action", "timestamp"])
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    write_csv(OUTPUT_FILE)
    print(f"Generated {OUTPUT_FILE} with expanded synthetic sessions for {USER_COUNT} users")