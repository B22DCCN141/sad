from __future__ import annotations

import os
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path
from typing import Any

import pandas as pd
from neo4j import GraphDatabase


CSV_FILE = Path(__file__).with_name("data_user500.csv")
ACTION_WEIGHT = {
    "view": 1,
    "click": 3,
    "add_to_cart": 6,
}
SESSION_GAP_MINUTES = 45
SIMILARITY_MIN_JACCARD = 0.18
SIMILARITY_MIN_COMMON_PRODUCTS = 2
SIMILAR_USERS_PER_SOURCE = 8
MIN_PRODUCT_TRANSITION_COUNT = 2
MIN_PRODUCT_TRANSITION_USERS = 2


@dataclass
class Neo4jConfig:
    uri: str
    user: str
    password: str
    database: str


def get_config() -> Neo4jConfig:
    return Neo4jConfig(
        uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        user=os.getenv("NEO4J_USER", "neo4j"),
        password=os.getenv("NEO4J_PASSWORD", "neo4jpassword"),
        database=os.getenv("NEO4J_DATABASE", "neo4j"),
    )


def load_data(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df = df.sort_values(["user_id", "timestamp"]).reset_index(drop=True)

    df["seq"] = df.groupby("user_id").cumcount() + 1
    df["event_id"] = (
        "EV_"
        + df["user_id"].astype(str)
        + "_"
        + df["seq"].astype(str).str.zfill(3)
        + "_"
        + df["timestamp"].dt.strftime("%Y%m%d%H%M%S")
    )

    df["date"] = df["timestamp"].dt.strftime("%Y-%m-%d")
    df["day_name"] = df["timestamp"].dt.day_name()
    df["weekday"] = df["timestamp"].dt.weekday
    df["hour"] = df["timestamp"].dt.hour
    df["hour_bucket"] = (df["hour"] // 3 * 3).map(lambda h: f"{h:02d}-{(h + 2):02d}")
    df["weight"] = df["action"].map(ACTION_WEIGHT).fillna(1).astype(int)

    # Sessionization by user with configurable time gap.
    df["delta_min"] = (
        df.groupby("user_id")["timestamp"].diff().dt.total_seconds().div(60)
    )
    df["is_new_session"] = (
        df["delta_min"].isna() | (df["delta_min"] > SESSION_GAP_MINUTES)
    )
    df["session_index"] = df.groupby("user_id")["is_new_session"].cumsum().astype(int)
    df["session_id"] = "S_" + df["user_id"].astype(str) + "_" + df["session_index"].astype(str)

    return df


def chunk_records(records: list[dict[str, Any]], chunk_size: int = 500) -> list[list[dict[str, Any]]]:
    return [records[i : i + chunk_size] for i in range(0, len(records), chunk_size)]


def build_base_nodes_and_events(tx, rows: list[dict[str, Any]]) -> None:
    tx.run(
        """
        UNWIND $rows AS row
        MERGE (u:User {user_id: row.user_id})

        MERGE (p:Product {product_id: row.product_id})

        MERGE (a:ActionType {name: row.action})

        MERGE (d:Day {date: row.date})
        ON CREATE SET d.day_name = row.day_name, d.weekday = row.weekday

        MERGE (h:HourBucket {name: row.hour_bucket})

        MERGE (s:Session {session_id: row.session_id})
        ON CREATE SET s.user_id = row.user_id
        MERGE (u)-[:HAS_SESSION]->(s)

        MERGE (e:Event {event_id: row.event_id})
        SET e.timestamp = datetime(row.timestamp),
            e.seq = row.seq,
            e.weight = row.weight

        MERGE (u)-[:PERFORMED]->(e)
        MERGE (e)-[:ON_PRODUCT]->(p)
        MERGE (e)-[:OF_TYPE]->(a)
        MERGE (e)-[:ON_DAY]->(d)
        MERGE (e)-[:IN_HOUR]->(h)
        MERGE (e)-[:IN_SESSION]->(s)
        """,
        rows=rows,
    )


def build_event_sequence_edges(tx, rows: list[dict[str, Any]]) -> None:
    tx.run(
        """
        UNWIND $rows AS row
        MATCH (e1:Event {event_id: row.from_event_id})
        MATCH (e2:Event {event_id: row.to_event_id})
        MERGE (e1)-[r:NEXT]->(e2)
        SET r.delta_min = row.delta_min
        """,
        rows=rows,
    )


def build_user_product_aggregates(tx, rows: list[dict[str, Any]]) -> None:
    tx.run(
        """
        UNWIND $rows AS row
        MATCH (u:User {user_id: row.user_id})
        MATCH (p:Product {product_id: row.product_id})
        MERGE (u)-[r:INTERACTED_WITH]->(p)
        SET r.total_count = row.total_count,
            r.view_count = row.view_count,
            r.click_count = row.click_count,
            r.cart_count = row.cart_count,
            r.preference_score = row.preference_score,
            r.last_seen = datetime(row.last_seen)
        """,
        rows=rows,
    )


def build_product_transition_edges(tx, rows: list[dict[str, Any]]) -> None:
    tx.run(
        """
        UNWIND $rows AS row
        MATCH (p1:Product {product_id: row.from_product_id})
        MATCH (p2:Product {product_id: row.to_product_id})
        MERGE (p1)-[r:NEXT_PRODUCT]->(p2)
        SET r.count = row.count,
            r.user_count = row.user_count,
            r.avg_delta_min = row.avg_delta_min
        """,
        rows=rows,
    )


def build_action_transition_edges(tx, rows: list[dict[str, Any]]) -> None:
    tx.run(
        """
        UNWIND $rows AS row
        MATCH (a1:ActionType {name: row.from_action})
        MATCH (a2:ActionType {name: row.to_action})
        MERGE (a1)-[r:TRANSITIONS_TO]->(a2)
        SET r.count = row.count,
            r.probability = row.probability
        """,
        rows=rows,
    )


def build_user_similarity_edges(tx, rows: list[dict[str, Any]]) -> None:
    tx.run(
        """
        UNWIND $rows AS row
        MATCH (u1:User {user_id: row.user1_id})
        MATCH (u2:User {user_id: row.user2_id})
        MERGE (u1)-[r:SIMILAR_TO]->(u2)
        SET r.jaccard = row.jaccard,
            r.common_products = row.common_products
        """,
        rows=rows,
    )


def add_constraints_and_indexes(tx) -> None:
    tx.run("CREATE CONSTRAINT user_id_unique IF NOT EXISTS FOR (u:User) REQUIRE u.user_id IS UNIQUE")
    tx.run("CREATE CONSTRAINT product_id_unique IF NOT EXISTS FOR (p:Product) REQUIRE p.product_id IS UNIQUE")
    tx.run("CREATE CONSTRAINT event_id_unique IF NOT EXISTS FOR (e:Event) REQUIRE e.event_id IS UNIQUE")
    tx.run("CREATE CONSTRAINT session_id_unique IF NOT EXISTS FOR (s:Session) REQUIRE s.session_id IS UNIQUE")
    tx.run("CREATE CONSTRAINT day_date_unique IF NOT EXISTS FOR (d:Day) REQUIRE d.date IS UNIQUE")
    tx.run("CREATE CONSTRAINT action_name_unique IF NOT EXISTS FOR (a:ActionType) REQUIRE a.name IS UNIQUE")
    tx.run("CREATE CONSTRAINT hour_name_unique IF NOT EXISTS FOR (h:HourBucket) REQUIRE h.name IS UNIQUE")


def clear_graph(tx) -> None:
    tx.run("MATCH (n) DETACH DELETE n")


def create_event_sequences(df: pd.DataFrame) -> pd.DataFrame:
    next_df = df.copy()
    next_df["next_event_id"] = next_df.groupby("user_id")["event_id"].shift(-1)
    next_df["next_product_id"] = next_df.groupby("user_id")["product_id"].shift(-1)
    next_df["next_action"] = next_df.groupby("user_id")["action"].shift(-1)
    next_df["next_timestamp"] = next_df.groupby("user_id")["timestamp"].shift(-1)

    seq = next_df.dropna(subset=["next_event_id"]).copy()
    seq["delta_min_to_next"] = (
        (seq["next_timestamp"] - seq["timestamp"]).dt.total_seconds() / 60
    ).round(2)
    return seq


def prepare_user_product_aggregates(df: pd.DataFrame) -> pd.DataFrame:
    agg = (
        df.groupby(["user_id", "product_id"])
        .agg(
            total_count=("action", "count"),
            view_count=("action", lambda s: int((s == "view").sum())),
            click_count=("action", lambda s: int((s == "click").sum())),
            cart_count=("action", lambda s: int((s == "add_to_cart").sum())),
            last_seen=("timestamp", "max"),
        )
        .reset_index()
    )
    agg["preference_score"] = (
        agg["view_count"] * ACTION_WEIGHT["view"]
        + agg["click_count"] * ACTION_WEIGHT["click"]
        + agg["cart_count"] * ACTION_WEIGHT["add_to_cart"]
    )
    agg["last_seen"] = agg["last_seen"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    return agg


def prepare_product_transitions(seq_df: pd.DataFrame) -> pd.DataFrame:
    agg = (
        seq_df.groupby(["product_id", "next_product_id"])
        .agg(
            count=("event_id", "count"),
            user_count=("user_id", "nunique"),
            avg_delta_min=("delta_min_to_next", "mean"),
        )
        .reset_index()
    )
    agg = agg[agg["product_id"] != agg["next_product_id"]]
    agg = agg[(agg["count"] >= MIN_PRODUCT_TRANSITION_COUNT) & (agg["user_count"] >= MIN_PRODUCT_TRANSITION_USERS)]
    agg["avg_delta_min"] = agg["avg_delta_min"].round(2)
    return agg


def prepare_action_transitions(seq_df: pd.DataFrame) -> pd.DataFrame:
    agg = (
        seq_df.groupby(["action", "next_action"])
        .size()
        .reset_index(name="count")
        .rename(columns={"action": "from_action", "next_action": "to_action"})
    )
    total_per_action = agg.groupby("from_action")["count"].transform("sum")
    agg["probability"] = (agg["count"] / total_per_action).round(4)
    return agg


def prepare_user_similarity(df: pd.DataFrame) -> pd.DataFrame:
    user_products = df.groupby("user_id")["product_id"].apply(set).to_dict()

    rows: list[dict[str, Any]] = []
    user_ids = sorted(user_products.keys())
    for u1, u2 in combinations(user_ids, 2):
        p1 = user_products[u1]
        p2 = user_products[u2]
        inter = p1.intersection(p2)
        if len(inter) < SIMILARITY_MIN_COMMON_PRODUCTS:
            continue

        union = p1.union(p2)
        jaccard = len(inter) / len(union)
        if jaccard < SIMILARITY_MIN_JACCARD:
            continue

        rows.append(
            {
                "user1_id": int(u1),
                "user2_id": int(u2),
                "jaccard": round(jaccard, 4),
                "common_products": int(len(inter)),
            }
        )
        rows.append(
            {
                "user1_id": int(u2),
                "user2_id": int(u1),
                "jaccard": round(jaccard, 4),
                "common_products": int(len(inter)),
            }
        )

    if not rows:
        return pd.DataFrame(rows)

    similarity_df = pd.DataFrame(rows)
    similarity_df = similarity_df.sort_values(
        ["user1_id", "jaccard", "common_products", "user2_id"],
        ascending=[True, False, False, True],
    )
    similarity_df = similarity_df.groupby("user1_id", group_keys=False).head(SIMILAR_USERS_PER_SOURCE)
    return similarity_df.reset_index(drop=True)


def print_summary(df: pd.DataFrame, seq_df: pd.DataFrame, up_df: pd.DataFrame, pt_df: pd.DataFrame, at_df: pd.DataFrame, us_df: pd.DataFrame) -> None:
    print("=" * 90)
    print("KB_GRAPH BUILD SUMMARY")
    print("=" * 90)
    print(f"Total rows: {len(df)}")
    print(f"Users: {df['user_id'].nunique()}")
    print(f"Products: {df['product_id'].nunique()}")
    print(f"Events: {len(df)}")
    print(f"Sessions: {df['session_id'].nunique()}")
    print(f"Days: {df['date'].nunique()}")
    print(f"Hour buckets: {df['hour_bucket'].nunique()}")
    print(f"Action transitions: {len(at_df)}")
    print(f"Event NEXT edges: {len(seq_df)}")
    print(f"Product NEXT_PRODUCT edges: {len(pt_df)}")
    print(f"User-Product INTERACTED_WITH edges: {len(up_df)}")
    print(f"User SIMILAR_TO edges (directed top-k): {len(us_df)}")
    print("=" * 90)


def main() -> None:
    config = get_config()
    if not CSV_FILE.exists():
        raise FileNotFoundError(f"CSV not found: {CSV_FILE}")

    print("Loading and transforming CSV...")
    df = load_data(CSV_FILE)
    seq_df = create_event_sequences(df)
    user_product_df = prepare_user_product_aggregates(df)
    product_transition_df = prepare_product_transitions(seq_df)
    action_transition_df = prepare_action_transitions(seq_df)
    user_similarity_df = prepare_user_similarity(df)

    event_rows = []
    for row in df.to_dict(orient="records"):
        event_rows.append(
            {
                "event_id": row["event_id"],
                "user_id": int(row["user_id"]),
                "product_id": int(row["product_id"]),
                "action": row["action"],
                "timestamp": row["timestamp"].strftime("%Y-%m-%dT%H:%M:%SZ"),
                "seq": int(row["seq"]),
                "date": row["date"],
                "day_name": row["day_name"],
                "weekday": int(row["weekday"]),
                "hour_bucket": row["hour_bucket"],
                "weight": int(row["weight"]),
                "session_id": row["session_id"],
            }
        )

    seq_rows = []
    for row in seq_df.to_dict(orient="records"):
        seq_rows.append(
            {
                "from_event_id": row["event_id"],
                "to_event_id": row["next_event_id"],
                "delta_min": float(row["delta_min_to_next"]),
            }
        )

    up_rows = []
    for row in user_product_df.to_dict(orient="records"):
        up_rows.append(
            {
                "user_id": int(row["user_id"]),
                "product_id": int(row["product_id"]),
                "total_count": int(row["total_count"]),
                "view_count": int(row["view_count"]),
                "click_count": int(row["click_count"]),
                "cart_count": int(row["cart_count"]),
                "preference_score": int(row["preference_score"]),
                "last_seen": row["last_seen"],
            }
        )

    pt_rows = []
    for row in product_transition_df.to_dict(orient="records"):
        pt_rows.append(
            {
                "from_product_id": int(row["product_id"]),
                "to_product_id": int(row["next_product_id"]),
                "count": int(row["count"]),
                "user_count": int(row["user_count"]),
                "avg_delta_min": float(row["avg_delta_min"]),
            }
        )

    at_rows = []
    for row in action_transition_df.to_dict(orient="records"):
        at_rows.append(
            {
                "from_action": row["from_action"],
                "to_action": row["to_action"],
                "count": int(row["count"]),
                "probability": float(row["probability"]),
            }
        )

    us_rows = []
    if not user_similarity_df.empty:
        for row in user_similarity_df.to_dict(orient="records"):
            us_rows.append(
                {
                    "user1_id": int(row["user1_id"]),
                    "user2_id": int(row["user2_id"]),
                    "jaccard": float(row["jaccard"]),
                    "common_products": int(row["common_products"]),
                }
            )

    print("Connecting to Neo4j and loading graph...")
    driver = GraphDatabase.driver(config.uri, auth=(config.user, config.password))
    try:
        with driver.session(database=config.database) as session:
            session.execute_write(clear_graph)
            session.execute_write(add_constraints_and_indexes)

            for batch in chunk_records(event_rows, 400):
                session.execute_write(build_base_nodes_and_events, batch)

            for batch in chunk_records(seq_rows, 700):
                session.execute_write(build_event_sequence_edges, batch)

            for batch in chunk_records(up_rows, 600):
                session.execute_write(build_user_product_aggregates, batch)

            for batch in chunk_records(pt_rows, 600):
                session.execute_write(build_product_transition_edges, batch)

            for batch in chunk_records(at_rows, 100):
                session.execute_write(build_action_transition_edges, batch)

            if us_rows:
                for batch in chunk_records(us_rows, 600):
                    session.execute_write(build_user_similarity_edges, batch)

        print_summary(df, seq_df, user_product_df, product_transition_df, action_transition_df, user_similarity_df)
        print("KB_Graph build completed successfully.")
        print("Tip: open Neo4j Browser and run queries from kb_graph_queries.cypher")
    finally:
        driver.close()


if __name__ == "__main__":
    main()


