from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from neo4j import GraphDatabase


ACTION_NAMES = ("view", "click", "add_to_cart")
USER_ID_PATTERN = re.compile(r"(?:user[_\s-]?id|user|khach|khách)\s*[:=]?\s*(\d+)", re.IGNORECASE)
PRODUCT_ID_PATTERN = re.compile(r"(?:product[_\s-]?id|product|san pham|sản phẩm)\s*[:=]?\s*(\d+)", re.IGNORECASE)
TOP_K_DEFAULT = 5


@dataclass
class GraphRAGConfig:
    uri: str = field(default_factory=lambda: os.getenv("NEO4J_URI", "bolt://localhost:7687"))
    user: str = field(default_factory=lambda: os.getenv("NEO4J_USER", "neo4j"))
    password: str = field(default_factory=lambda: os.getenv("NEO4J_PASSWORD", "neo4jpassword"))
    database: str = field(default_factory=lambda: os.getenv("NEO4J_DATABASE", "neo4j"))
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    openai_model: str = field(default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4o-mini"))


class KBGraphRAG:
    def __init__(self, config: GraphRAGConfig | None = None) -> None:
        self.config = config or GraphRAGConfig()
        self.driver = GraphDatabase.driver(
            self.config.uri,
            auth=(self.config.user, self.config.password),
        )

    def close(self) -> None:
        self.driver.close()

    def _run_query(self, query: str, **params: Any) -> list[dict[str, Any]]:
        with self.driver.session(database=self.config.database) as session:
            result = session.run(query, **params)
            return [record.data() for record in result]

    def extract_entities(self, question: str) -> dict[str, list[int] | list[str]]:
        user_ids = [int(match) for match in USER_ID_PATTERN.findall(question)]
        product_ids = [int(match) for match in PRODUCT_ID_PATTERN.findall(question)]
        actions = [action for action in ACTION_NAMES if re.search(rf"\b{action}\b", question, re.IGNORECASE)]
        return {
            "user_ids": user_ids,
            "product_ids": product_ids,
            "actions": actions,
        }

    def retrieve(self, question: str, top_k: int = TOP_K_DEFAULT) -> dict[str, Any]:
        entities = self.extract_entities(question)
        user_ids = entities["user_ids"]
        product_ids = entities["product_ids"]
        actions = entities["actions"]

        context: dict[str, Any] = {
            "entities": entities,
            "user_profiles": [],
            "product_profiles": [],
            "action_transitions": [],
            "hot_products": [],
            "hot_sessions": [],
            "similar_users": [],
            "recent_patterns": [],
        }

        if user_ids:
            context["user_profiles"] = self._run_query(
                """
                MATCH (u:User {user_id: $user_id})-[:HAS_SESSION]->(s:Session)<-[:IN_SESSION]-(e:Event)
                MATCH (e)-[:ON_PRODUCT]->(p:Product)
                MATCH (e)-[:OF_TYPE]->(a:ActionType)
                WITH u, s, e, p, a
                ORDER BY e.timestamp DESC
                RETURN
                    u.user_id AS user_id,
                    s.session_id AS session_id,
                    e.event_id AS event_id,
                    e.timestamp AS timestamp,
                    p.product_id AS product_id,
                    a.name AS action,
                    e.weight AS weight
                LIMIT $limit
                """,
                user_id=user_ids[0],
                limit=top_k * 3,
            )
            context["hot_sessions"] = self._run_query(
                """
                MATCH (u:User {user_id: $user_id})-[:HAS_SESSION]->(s:Session)<-[:IN_SESSION]-(e:Event)
                WITH s, count(e) AS event_count, sum(e.weight) AS intensity, min(e.timestamp) AS first_ts, max(e.timestamp) AS last_ts
                RETURN s.session_id AS session_id, event_count, intensity, first_ts, last_ts
                ORDER BY intensity DESC, event_count DESC
                LIMIT $limit
                """,
                user_id=user_ids[0],
                limit=top_k,
            )
            context["similar_users"] = self._run_query(
                """
                MATCH (u:User {user_id: $user_id})-[r:SIMILAR_TO]->(u2:User)
                RETURN u2.user_id AS similar_user_id, r.jaccard AS jaccard, r.common_products AS common_products
                ORDER BY r.jaccard DESC, r.common_products DESC
                LIMIT $limit
                """,
                user_id=user_ids[0],
                limit=top_k,
            )

        if product_ids:
            context["product_profiles"] = self._run_query(
                """
                MATCH (p:Product {product_id: $product_id})
                OPTIONAL MATCH (:User)-[r:INTERACTED_WITH]->(p)
                OPTIONAL MATCH (p)-[np:NEXT_PRODUCT]->(p2:Product)
                OPTIONAL MATCH (p1:Product)-[pp:NEXT_PRODUCT]->(p)
                WITH p,
                     coalesce(sum(r.preference_score), 0) AS popularity,
                     coalesce(sum(r.cart_count), 0) AS carts,
                     coalesce(sum(r.click_count), 0) AS clicks,
                     coalesce(sum(r.view_count), 0) AS views,
                     collect(DISTINCT {next_product_id: p2.product_id, count: np.count, user_count: np.user_count, avg_delta_min: np.avg_delta_min}) AS next_products,
                     collect(DISTINCT {prev_product_id: p1.product_id, count: pp.count, user_count: pp.user_count, avg_delta_min: pp.avg_delta_min}) AS prev_products
                RETURN p.product_id AS product_id, popularity, carts, clicks, views,
                       next_products[0..$limit] AS next_products,
                       prev_products[0..$limit] AS prev_products
                """,
                product_id=product_ids[0],
                limit=top_k,
            )

        if actions:
            context["action_transitions"] = self._run_query(
                """
                MATCH (a1:ActionType)-[r:TRANSITIONS_TO]->(a2:ActionType)
                WHERE a1.name IN $actions OR a2.name IN $actions
                RETURN a1.name AS from_action, a2.name AS to_action, r.count AS count, r.probability AS probability
                ORDER BY r.count DESC, r.probability DESC
                LIMIT $limit
                """,
                actions=actions,
                limit=top_k * 4,
            )

        if not user_ids and not product_ids and not actions:
            context["hot_products"] = self._run_query(
                """
                MATCH (:User)-[r:INTERACTED_WITH]->(p:Product)
                WITH p, sum(r.preference_score) AS popularity, sum(r.cart_count) AS carts, sum(r.click_count) AS clicks, sum(r.view_count) AS views
                ORDER BY popularity DESC
                LIMIT $limit
                RETURN p.product_id AS product_id, popularity, carts, clicks, views
                """,
                limit=top_k,
            )
            context["recent_patterns"] = self._run_query(
                """
                MATCH (u:User)-[:PERFORMED]->(e:Event)-[:OF_TYPE]->(a:ActionType)
                MATCH (e)-[:ON_PRODUCT]->(p:Product)
                RETURN u.user_id AS user_id, e.event_id AS event_id, e.timestamp AS timestamp, a.name AS action, p.product_id AS product_id
                ORDER BY e.timestamp DESC
                LIMIT $limit
                """,
                limit=top_k * 2,
            )

        return context

    def format_context(self, question: str, context: dict[str, Any]) -> str:
        parts: list[str] = []
        parts.append(f"Query time: {datetime.utcnow().isoformat()}Z")
        parts.append(f"User question: {question}")

        entities = context.get("entities", {})
        if entities:
            parts.append(f"Detected entities: {entities}")

        if context.get("user_profiles"):
            parts.append("User history:")
            for row in context["user_profiles"]:
                parts.append(
                    f"- user={row['user_id']} session={row['session_id']} time={row['timestamp']} product={row['product_id']} action={row['action']} weight={row['weight']}"
                )

        if context.get("hot_sessions"):
            parts.append("Session intensity:")
            for row in context["hot_sessions"]:
                parts.append(
                    f"- session={row['session_id']} event_count={row['event_count']} intensity={row['intensity']} first={row['first_ts']} last={row['last_ts']}"
                )

        if context.get("similar_users"):
            parts.append("Similar users:")
            for row in context["similar_users"]:
                parts.append(
                    f"- similar_user={row['similar_user_id']} jaccard={row['jaccard']} common_products={row['common_products']}"
                )

        if context.get("product_profiles"):
            parts.append("Product profile:")
            for row in context["product_profiles"]:
                parts.append(
                    f"- product={row['product_id']} popularity={row['popularity']} carts={row['carts']} clicks={row['clicks']} views={row['views']}"
                )
                if row.get("next_products"):
                    parts.append(f"  next_products={row['next_products']}")
                if row.get("prev_products"):
                    parts.append(f"  prev_products={row['prev_products']}")

        if context.get("action_transitions"):
            parts.append("Action transitions:")
            for row in context["action_transitions"]:
                parts.append(
                    f"- {row['from_action']} -> {row['to_action']} count={row['count']} probability={row['probability']}"
                )

        if context.get("hot_products"):
            parts.append("Hot products:")
            for row in context["hot_products"]:
                parts.append(
                    f"- product={row['product_id']} popularity={row['popularity']} carts={row['carts']} clicks={row['clicks']} views={row['views']}"
                )

        if context.get("recent_patterns"):
            parts.append("Recent patterns:")
            for row in context["recent_patterns"]:
                parts.append(
                    f"- user={row['user_id']} time={row['timestamp']} product={row['product_id']} action={row['action']}"
                )

        return "\n".join(parts)

    def answer(self, question: str, top_k: int = TOP_K_DEFAULT) -> dict[str, Any]:
        context = self.retrieve(question, top_k=top_k)
        context_text = self.format_context(question, context)
        answer_text = self._generate_answer(question, context_text, context)
        return {
            "answer": answer_text,
            "context_text": context_text,
            "context": context,
        }

    def _generate_answer(self, question: str, context_text: str, context: dict[str, Any]) -> str:
        if self.config.openai_api_key:
            try:
                from openai import OpenAI

                client = OpenAI(api_key=self.config.openai_api_key)
                response = client.chat.completions.create(
                    model=self.config.openai_model,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a strict e-commerce graph analyst. Answer only from the provided graph context. "
                                "Do not invent facts, do not extrapolate, and do not recommend items without graph evidence. "
                                "If evidence is weak or missing, say that the graph does not contain enough evidence. "
                                "Use Vietnamese if the user asks in Vietnamese. Keep the answer concise and structured."
                            ),
                        },
                        {
                            "role": "user",
                            "content": f"Context:\n{context_text}\n\nQuestion:\n{question}",
                        },
                    ],
                    temperature=0.2,
                )
                return response.choices[0].message.content.strip()
            except Exception as exc:  # pragma: no cover - fallback path
                return self._fallback_answer(question, context, error=str(exc))

        return self._fallback_answer(question, context)

    def _fallback_answer(self, question: str, context: dict[str, Any], error: str | None = None) -> str:
        lines: list[str] = []
        if error:
            lines.append(f"LLM fallback: {error}")
        lines.append("Dựa trên KB_Graph:")

        if context.get("user_profiles"):
            user_id = context["entities"].get("user_ids", [None])[0]
            lines.append(f"- Lịch sử gần nhất của user {user_id}:")
            for row in context["user_profiles"][:5]:
                lines.append(
                    f"  + {row['timestamp']} | product {row['product_id']} | {row['action']} | weight={row['weight']}"
                )

        if context.get("product_profiles"):
            row = context["product_profiles"][0]
            lines.append(f"- Product {row['product_id']} có popularity={row['popularity']}, carts={row['carts']}, clicks={row['clicks']}, views={row['views']}")
            if row.get("next_products"):
                lines.append(f"  + Sản phẩm thường đi tiếp: {row['next_products'][:3]}")

        if context.get("action_transitions"):
            best_transition = context["action_transitions"][0]
            lines.append(
                f"- Chuyển trạng thái nổi bật: {best_transition['from_action']} -> {best_transition['to_action']} (count={best_transition['count']}, probability={best_transition['probability']})"
            )

        if context.get("similar_users"):
            lines.append("- Người dùng tương tự:")
            for row in context["similar_users"][:3]:
                lines.append(
                    f"  + user {row['similar_user_id']} | jaccard={row['jaccard']} | common_products={row['common_products']}"
                )

        if not any(context.get(key) for key in ("user_profiles", "product_profiles", "action_transitions", "similar_users", "hot_products", "recent_patterns")):
            lines.append("- Tôi chưa nhận được thực thể cụ thể, nên đã lấy các pattern hot nhất trong graph.")
            for row in context.get("hot_products", [])[:5]:
                lines.append(
                    f"  + product {row['product_id']} | popularity={row['popularity']} | carts={row['carts']} | clicks={row['clicks']} | views={row['views']}"
                )

        lines.append("Kết luận: graph đủ để trả lời theo lịch sử user, product affinity, chuyển đổi hành vi và similarity.")
        return "\n".join(lines)
