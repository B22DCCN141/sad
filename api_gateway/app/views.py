from __future__ import annotations

import os
import json
import logging
import re
import unicodedata

import requests
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .kb_graph_rag import GraphRAGConfig, KBGraphRAG

logger = logging.getLogger(__name__)


_RAG_SINGLETON: KBGraphRAG | None = None


def _remove_accents(text: str) -> str:
    if not text:
        return ""
    nfkd_form = unicodedata.normalize('NFKD', text)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)]).lower()
SEARCH_KEYWORDS = (
    "laptop",
    "gaming",
    "game",
    "pubg",
    "lol",
    "điện thoại",
    "phone",
    "tai nghe",
    "sách",
)


def get_rag() -> KBGraphRAG:
    global _RAG_SINGLETON
    if _RAG_SINGLETON is None:
        _RAG_SINGLETON = KBGraphRAG(GraphRAGConfig())
    return _RAG_SINGLETON


def normalize_product_cards(rows, source_label: str):
    cards = []
    seen = set()
    for index, row in enumerate(rows):
        product_id = row.get("product_id") or row.get("next_product_id") or row.get("prev_product_id")
        if product_id is None:
            continue
        product_id = int(product_id)
        if product_id in seen:
            continue
        seen.add(product_id)
        score = float(row.get("popularity") or row.get("score") or row.get("count") or row.get("jaccard") or 0)
        cards.append(
            {
                "product_id": product_id,
                "score": round(score, 4),
                "reason": row.get("reason") or source_label,
                "rank": index + 1,
                "meta": {k: v for k, v in row.items() if k not in {"product_id", "next_product_id", "prev_product_id"}},
            }
        )
    return cards


def merge_ranked_cards(*card_lists, limit: int = 8):
    merged = {}
    for card_list in card_lists:
        for card in card_list:
            pid = int(card["product_id"])
            current = merged.get(pid)
            if current is None or card["score"] > current["score"]:
                merged[pid] = card

    ranked = sorted(merged.values(), key=lambda item: (-item["score"], item["rank"], item["product_id"]))
    return ranked[:limit]


def build_search_cards(rag: KBGraphRAG, question: str, limit: int):
    context = rag.retrieve(question, top_k=limit)
    cards = []

    if context.get("product_profiles"):
        for row in context["product_profiles"]:
            cards.append(
                {
                    "product_id": int(row["product_id"]),
                    "score": float(row.get("popularity") or 0),
                    "reason": "Product profile từ graph",
                    "rank": 1,
                    "meta": row,
                }
            )

    if context.get("hot_products"):
        cards.extend(normalize_product_cards(context["hot_products"], "Hot products"))

    if context.get("recent_patterns"):
        recent = []
        for row in context["recent_patterns"]:
            recent.append(
                {
                    "product_id": int(row["product_id"]),
                    "score": 1.0,
                    "reason": f"Recent pattern user {row['user_id']} · {row['action']}",
                    "rank": 1,
                    "meta": row,
                }
            )
        cards.extend(recent)
    return context, merge_ranked_cards(cards, limit=limit)


def _parse_budget_vnd(question: str) -> int | None:
    if not question:
        return None

    text = question.lower()
    
    # 1. Matches "tr", "triệu", "m"
    m = re.search(r"(\d+(?:[\.,]\d+)?)\s*(tr|triệu|trieu|m)(?:\b|\s|$)", text)
    if m:
        num_str = m.group(1).replace(",", ".")
        if num_str.count(".") > 1:
            num_str = num_str.replace(".", "")
        try:
            return int(float(num_str) * 1_000_000)
        except ValueError:
            pass

    # 2. Matches "k", "nghìn", "ngàn"
    m = re.search(r"(\d+(?:[\.,]\d+)?)\s*(k|nghìn|ngàn|ngan)(?:\b|\s|$)", text)
    if m:
        num_str = m.group(1).replace(",", ".")
        if num_str.count(".") > 1:
            num_str = num_str.replace(".", "")
        try:
            return int(float(num_str) * 1_000)
        except ValueError:
            pass

    # 3. Matches numbers with dots/commas like "80.000", "80,000", "15.000.000"
    matches = re.findall(r"\b\d+(?:[\.,]\d+)+\b", text)
    for match in matches:
        cleaned = match.replace(".", "").replace(",", "")
        try:
            val = int(cleaned)
            if 1000 <= val <= 999999999:
                return val
        except ValueError:
            pass

    # 4. Matches clean numbers without separators but 4 to 9 digits long (e.g. 80000, 15000000)
    matches = re.findall(r"\b\d{4,9}\b", text)
    for match in matches:
        try:
            val = int(match)
            return val
        except ValueError:
            pass

    return None


def _extract_keywords(question: str) -> list[str]:
    text = (question or "").lower()
    return [kw for kw in SEARCH_KEYWORDS if kw in text]


def _fetch_product_catalog() -> list[dict]:
    try:
        response = requests.get("http://product-service:8000/products/", timeout=4)
        if not response.ok:
            return []
        payload = response.json()
        if isinstance(payload, list):
            return payload
        if isinstance(payload, dict) and isinstance(payload.get("results"), list):
            return payload["results"]
        return []
    except Exception:
        return []


def _call_gemini_api(question: str, catalog: list[dict], top_k: int) -> dict | None:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None

    # Compact catalog to avoid wasting too many tokens
    catalog_brief = []
    for item in catalog:
        try:
            pid = int(item.get("id"))
        except (TypeError, ValueError):
            continue

        catalog_brief.append({
            "id": pid,
            "name": item.get("name"),
            "price": float(item.get("price") or 0),
            "description": item.get("description", ""),
            "category": item.get("category_name", ""),
            "attributes": item.get("attributes", {})
        })

    # Prepare prompt
    prompt = f"""
Bạn là một trợ lý bán hàng AI tại cửa hàng sách & đồ công nghệ/gia dụng. Hãy trả lời câu hỏi của khách hàng bằng tiếng Việt một cách thân thiện và gợi ý tối đa {top_k} sản phẩm phù hợp nhất từ danh sách sản phẩm thực tế của cửa hàng được cung cấp dưới đây.

Danh sách sản phẩm cửa hàng hiện có:
{json.dumps(catalog_brief, ensure_ascii=False, indent=2)}

Yêu cầu khách hàng: "{question}"

Yêu cầu phản hồi:
Chỉ đề xuất các sản phẩm có thực trong danh sách trên bằng cách trả về ID sản phẩm tương ứng. Nếu không có sản phẩm nào phù hợp, hãy ghi nhận và trả về mảng product_ids rỗng.

Hãy trả về phản hồi DUY NHẤT dưới dạng JSON với cấu trúc chính xác như sau (không được bao quanh bởi bất kỳ từ nào ngoài JSON sạch):
{{
  "answer": "Câu trả lời của bạn gửi đến khách hàng bằng tiếng Việt, giải thích vì sao chọn sản phẩm và mức giá của chúng nếu có.",
  "product_ids": [danh sách các ID của sản phẩm được chọn]
}}
"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "responseMimeType": "application/json"
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        if not response.ok:
            logger.error(f"Gemini API error: HTTP {response.status_code} - {response.text}")
            return None

        response_data = response.json()
        text_response = response_data["candidates"][0]["content"]["parts"][0]["text"].strip()
        
        # Parse JSON from response
        try:
            parsed = json.loads(text_response)
            return parsed
        except json.JSONDecodeError:
            # Try to extract JSON if it was returned with markdown formatting
            match = re.search(r"```json\s*(.*?)\s*```", text_response, re.DOTALL)
            if match:
                parsed = json.loads(match.group(1).strip())
                return parsed
            raise
    except Exception as e:
        logger.error(f"Failed to call Gemini API or parse response: {e}")
        return None


def _rank_catalog_items(question: str, limit: int) -> list[dict]:
    catalog = _fetch_product_catalog()
    if not catalog:
        return []

    q_normalized = _remove_accents(question)
    budget = _parse_budget_vnd(question)
    
    STOP_WORDS = {
        "toi", "can", "xem", "cac", "san", "pham", "cua", "cho", "muon", "mua", 
        "tim", "co", "la", "va", "nay", "tam", "gia", "khoang", "duoi", "tren", 
        "trong", "de", "voi", "trieu", "tr", "k", "tram", "dong"
    }
    
    # Exclude numeric or format words (e.g. digits, k, tr) from q_words to get only pure text tokens
    q_words = []
    for w in q_normalized.split():
        if w in STOP_WORDS or len(w) < 2:
            continue
        cleaned_word = w.replace(".", "").replace(",", "")
        if cleaned_word.isdigit() or w in ("tr", "k"):
            continue
        q_words.append(w)
    
    ranked = []
    for item in catalog:
        try:
            product_id = int(item.get("id"))
        except (TypeError, ValueError):
            continue

        if not item.get("is_active", True):
            continue

        try:
            price = float(item.get("price") or 0)
        except (TypeError, ValueError):
            price = 0

        if price <= 0:
            continue

        name = item.get("name") or ""
        brand = item.get("brand_name") or ""
        category = item.get("category_name") or ""
        description = item.get("description") or ""

        # Normalize fields
        name_norm = _remove_accents(name)
        brand_norm = _remove_accents(brand)
        cat_norm = _remove_accents(category)
        desc_norm = _remove_accents(description)

        name_words = name_norm.split()
        brand_words = brand_norm.split()
        cat_words = cat_norm.split()
        desc_words = desc_norm.split()

        word_match_score = 0.0
        
        # Word and substring matching
        for word in q_words:
            # Check exact word match (highest priority)
            if word in name_words:
                word_match_score += 4.0
            elif word in name_norm: # substring
                word_match_score += 1.0
                
            if word in brand_words:
                word_match_score += 5.0
            elif word in brand_norm:
                word_match_score += 1.5
                
            if word in cat_words:
                word_match_score += 4.5
            elif word in cat_norm:
                word_match_score += 1.5
                
            if word in desc_words:
                word_match_score += 1.0
            elif word in desc_norm:
                word_match_score += 0.3

        # Skip completely irrelevant products if user specified textual keywords
        if q_words and word_match_score == 0:
            continue

        score = word_match_score

        # Specific keyword heuristics (like "gaming", "game", "lol", "pubg")
        wants_gaming = any(w in q_normalized for w in ("game", "gaming", "lol", "pubg"))
        if wants_gaming:
            text_blob = " ".join([name_norm, cat_norm, brand_norm, desc_norm])
            if any(token in text_blob for token in ("rtx", "gaming", "rog", "geforce")):
                score += 4.0

        # Specific budget check
        if budget:
            is_under = any(w in q_normalized for w in ("duoi", "thap hon", "it hon", "nho hon", "re hon"))
            is_above = any(w in q_normalized for w in ("tren", "cao hon", "lon hon", "dat hon"))
            if is_under:
                if price > budget:
                    continue
                score += 4.0
            elif is_above:
                if price < budget:
                    continue
                score += 4.0
            else:
                # Around budget
                diff_ratio = abs(price - budget) / budget
                if diff_ratio <= 0.25:
                    score += 4.0
                elif diff_ratio <= 0.4:
                    score += 2.0
                # Hard limit: if price is too high above budget, exclude or penalize heavily
                if price > budget * 1.35:
                    continue
                if price < budget * 0.45:
                    score -= 1.0

        if score > 0:
            ranked.append(
                (
                    score,
                    abs(price - budget) if budget else 0,
                    {
                        "product_id": product_id,
                        "score": round(score, 4),
                        "reason": f"Match: {brand} · {category}",
                        "rank": 1,
                        "meta": {
                            "price": price,
                            "name": name,
                            "category_name": category,
                        },
                    },
                )
            )

    ranked.sort(key=lambda x: (-x[0], x[1]))
    return [card for _, __, card in ranked[:limit]]


def _filter_zero_or_unknown_cards(cards: list[dict]) -> list[dict]:
    if not cards:
        return []
    catalog = _fetch_product_catalog()
    if not catalog:
        return cards

    price_by_id: dict[int, float] = {}
    for item in catalog:
        try:
            pid = int(item.get("id"))
            price_by_id[pid] = float(item.get("price") or 0)
        except (TypeError, ValueError):
            continue

    filtered = []
    for card in cards:
        pid = int(card.get("product_id") or 0)
        if pid and price_by_id.get(pid, 0) > 0:
            filtered.append(card)
    return filtered


def build_cart_cards(rag: KBGraphRAG, user_id: int | None, product_ids: list[int], limit: int):
    recommendation_rows = []
    transition_rows = []

    if product_ids:
        transition_rows = rag._run_query(  # noqa: SLF001 - used inside API gateway
            """
            UNWIND $product_ids AS pid
            MATCH (p:Product {product_id: pid})-[r:NEXT_PRODUCT]->(p2:Product)
            RETURN p2.product_id AS product_id,
                   sum(r.count) AS count,
                   sum(r.user_count) AS user_count,
                   avg(r.avg_delta_min) AS avg_delta_min
            ORDER BY count DESC, user_count DESC
            LIMIT $limit
            """,
            product_ids=product_ids,
            limit=limit * 2,
        )

    if user_id is not None:
        recommendation_rows = rag._run_query(  # noqa: SLF001 - used inside API gateway
            """
            MATCH (u:User {user_id: $user_id})-[r:INTERACTED_WITH]->(p:Product)
            RETURN p.product_id AS product_id,
                   r.preference_score AS score,
                   r.total_count AS count,
                   r.view_count AS view_count,
                   r.click_count AS click_count,
                   r.cart_count AS cart_count
            ORDER BY r.preference_score DESC, r.total_count DESC
            LIMIT $limit
            """,
            user_id=user_id,
            limit=limit,
        )

    hot_rows = rag._run_query(
        """
        MATCH (:User)-[r:INTERACTED_WITH]->(p:Product)
        WITH p, sum(r.preference_score) AS popularity, sum(r.cart_count) AS carts, sum(r.click_count) AS clicks, sum(r.view_count) AS views
        RETURN p.product_id AS product_id, popularity, carts, clicks, views
        ORDER BY popularity DESC
        LIMIT $limit
        """,
        limit=limit,
    )

    profile_cards = normalize_product_cards(recommendation_rows, "User cart profile")
    transition_cards = normalize_product_cards(transition_rows, "Next-product flow")
    hot_cards = normalize_product_cards(hot_rows, "Hot products")

    return merge_ranked_cards(profile_cards, transition_cards, hot_cards, limit=limit)


class AIHealthView(APIView):
    def get(self, request):
        rag = get_rag()
        return Response(
            {
                "status": "ok",
                "neo4j_uri": rag.config.uri,
                "database": rag.config.database,
                "chat_model": rag.config.openai_model if rag.config.openai_api_key else "fallback",
            }
        )


class AIChatView(APIView):
    def post(self, request):
        rag = get_rag()
        question = (request.data.get("message") or request.data.get("question") or "").strip()
        top_k = int(request.data.get("top_k") or 6)
        if not question:
            return Response({"error": "message is required"}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Fetch entire catalog first
        catalog = _fetch_product_catalog()

        # 2. Try calling Gemini
        gemini_response = None
        if os.getenv("GEMINI_API_KEY"):
            gemini_response = _call_gemini_api(question, catalog, top_k)

        if gemini_response and isinstance(gemini_response, dict):
            answer = gemini_response.get("answer", "")
            product_ids = gemini_response.get("product_ids") or []
            
            # Map product_ids back to cards format
            cards = []
            seen_ids = set()
            for idx, pid in enumerate(product_ids):
                try:
                    pid = int(pid)
                except (TypeError, ValueError):
                    continue
                if pid in seen_ids:
                    continue
                seen_ids.add(pid)
                
                # Find product in catalog to construct card meta
                item = next((x for x in catalog if int(x.get("id")) == pid), None)
                if item:
                    cards.append({
                        "product_id": pid,
                        "score": round(1.0 - (idx * 0.05), 4),  # Descending scores for ranking display
                        "reason": "Gợi ý từ Gemini AI",
                        "rank": idx + 1,
                        "meta": {
                            "price": float(item.get("price") or 0),
                            "name": item.get("name"),
                            "category_name": item.get("category_name"),
                        }
                    })
            
            # Still get context and entities from Neo4j for the UI expander insights
            result = rag.answer(question, top_k=top_k)
            context = result.get("context", {})
            context_text = result.get("context_text", "")
            entities = context.get("entities", {})
        else:
            # Fallback to current implementation
            result = rag.answer(question, top_k=top_k)
            context = result.get("context", {})
            context_text = result.get("context_text", "")
            entities = context.get("entities", {})
            
            _, cards = build_search_cards(rag, question, top_k)
            cards = _filter_zero_or_unknown_cards(cards)
            if not cards or all("hot" in str(card.get("reason", "")).lower() for card in cards):
                catalog_cards = _rank_catalog_items(question, top_k)
                if catalog_cards:
                    cards = catalog_cards
            answer = result["answer"]

        return Response(
            {
                "answer": answer,
                "cards": cards,
                "context_text": context_text,
                "entities": entities,
            }
        )


class AISearchView(APIView):
    def get(self, request):
        rag = get_rag()
        query = (request.query_params.get("q") or request.query_params.get("query") or "").strip()
        top_k = int(request.query_params.get("limit") or 8)

        context, cards = build_search_cards(rag, query or "hot products", top_k)
        cards = _filter_zero_or_unknown_cards(cards)

        # With natural-language queries (e.g. laptop ~20tr), avoid falling back to generic hot products.
        if query and (not cards or all("hot" in str(card.get("reason", "")).lower() for card in cards)):
            catalog_cards = _rank_catalog_items(query, top_k)
            if catalog_cards:
                cards = catalog_cards
        insights = []
        if context.get("action_transitions"):
            first_transition = context["action_transitions"][0]
            insights.append(
                f"{first_transition['from_action']} -> {first_transition['to_action']} xuất hiện {first_transition['count']} lần"
            )
        if context.get("similar_users"):
            top_similar = context["similar_users"][0]
            insights.append(
                f"User tương tự gần nhất: {top_similar['similar_user_id']} (Jaccard {top_similar['jaccard']})"
            )
        budget = _parse_budget_vnd(query)
        if budget:
            insights.append(f"Đã ưu tiên theo mức giá khoảng {budget:,}đ".replace(",", "."))

        return Response(
            {
                "query": query,
                "cards": cards,
                "insights": insights,
                "context_text": rag.format_context(query or "hot products", context),
            }
        )


class AICartView(APIView):
    def post(self, request):
        rag = get_rag()
        user_id = request.data.get("user_id")
        items = request.data.get("items") or []
        product_ids = request.data.get("product_ids") or [item.get("product_id") for item in items if isinstance(item, dict)]
        product_ids = [int(pid) for pid in product_ids if pid is not None]
        top_k = int(request.data.get("limit") or 8)

        cards = build_cart_cards(rag, int(user_id) if user_id is not None else None, product_ids, top_k)
        insights = []

        if product_ids:
            insights.append(f"KB_Graph đang theo dõi {len(product_ids)} sản phẩm trong giỏ hàng.")
        if user_id is not None:
            insights.append(f"User {user_id} có lịch sử tương tác được gắn vào graph.")

        return Response(
            {
                "user_id": user_id,
                "product_ids": product_ids,
                "cards": cards,
                "insights": insights,
            }
        )


class GatewayView(APIView):
    """
    API Gateway xử lý điều hướng yêu cầu đến 11 Microservices.
    """
    # Bản đồ các service chạy trong Docker
    SERVICE_MAP = {
        'staff': 'http://staff-service:8000/staff/',
        'manager': 'http://manager-service:8000/manager/',
        'customers': 'http://customer-service:8000/customers/',
        'catalog': 'http://catalog-service:8000/catalog/',
        'books': 'http://book-service:8000/books/',
        'products': 'http://product-service:8000/products/',
        'carts': 'http://cart-service:8000/carts/',
        'orders': 'http://order-service:8000/orders/',
        'ship': 'http://ship-service:8000/shipping/',
        'pay': 'http://pay-service:8000/payments/',
        'ratings': 'http://comment-rate-service:8000/ratings/',
        'recommend': 'http://recommender-ai-service:8000/recommend/',
        # ── New services ──
        'electronics': 'http://electronic-service:8000/electronics/',
        'clothes': 'http://clothe-service:8000/clothes/',
    }

    def handle_request(self, request, service_name, path=None):
        base_url = self.SERVICE_MAP.get(service_name)
        if not base_url:
            return Response({"error": "Service not found"}, status=404)

        # 1. Tạo URL gốc sạch (ví dụ: http://cart-service:8000/carts/)
        url = base_url.rstrip('/') + '/'

        # 2. Nối phần path (ví dụ: 3/items/1)
        if path:
            # strip('/') để dọn dẹp dấu gạch chéo thừa, sau đó thêm / ở cuối
            url += str(path).strip('/') + '/'

        # Log để Dũng xem link cuối cùng trong Docker terminal
        print(f"\n[GATEWAY] Forwarding to: {url}")

        try:
            method = request.method.lower()
            request_kwargs = {
                "method": method,
                "url": url,
                "params": request.GET,
                "timeout": 10
            }
            if method in ['post', 'put', 'patch', 'delete'] and request.data:
                request_kwargs["json"] = request.data

            resp = requests.request(**request_kwargs)

            if resp.status_code == 204 or not resp.text.strip():
                return Response(None, status=resp.status_code)

            try:
                return Response(resp.json(), status=resp.status_code)
            except ValueError:
                return Response({"detail": "Not JSON", "raw": resp.text[:100]}, status=resp.status_code)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    # Chấp nhận mọi phương thức
    def get(self, request, service_name, path=None):
        return self.handle_request(request, service_name, path)

    def post(self, request, service_name, path=None):
        return self.handle_request(request, service_name, path)

    def put(self, request, service_name, path=None):
        return self.handle_request(request, service_name, path)

    def delete(self, request, service_name, path=None):
        return self.handle_request(request, service_name, path)