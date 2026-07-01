from __future__ import annotations

import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from kb_graph_rag import KBGraphRAG, GraphRAGConfig


APP_TITLE = "KB_Graph RAG Chat"
APP_SUBTITLE = "Chat trực tiếp trên Neo4j knowledge graph từ data_user500.csv"


def apply_custom_styles() -> None:
    st.markdown(
        """
        <style>
            .stApp {
                background:
                    radial-gradient(circle at top left, rgba(255, 205, 112, 0.20), transparent 30%),
                    radial-gradient(circle at top right, rgba(106, 169, 255, 0.18), transparent 28%),
                    linear-gradient(180deg, #0b1020 0%, #11182b 100%);
                color: #f5f7fb;
            }
            .block-container {
                max-width: 1180px;
                padding-top: 1.25rem;
                padding-bottom: 2rem;
            }
            h1, h2, h3, p, label, .stMarkdown, .stText {
                color: #f5f7fb !important;
            }
            .hero {
                padding: 1.25rem 1.5rem;
                border: 1px solid rgba(255,255,255,0.12);
                border-radius: 22px;
                background: rgba(9, 14, 30, 0.72);
                box-shadow: 0 18px 50px rgba(0,0,0,0.30);
                backdrop-filter: blur(8px);
                margin-bottom: 1rem;
            }
            .metric-card {
                padding: 0.9rem 1rem;
                border-radius: 18px;
                background: rgba(255,255,255,0.06);
                border: 1px solid rgba(255,255,255,0.08);
            }
            .stChatMessage {
                border-radius: 18px;
            }
            div[data-testid="stSidebar"] {
                background: linear-gradient(180deg, rgba(11,16,32,0.96), rgba(17,24,43,0.96));
                border-right: 1px solid rgba(255,255,255,0.08);
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def init_state() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "Tôi đã kết nối KB_Graph. Bạn có thể hỏi về user, product, action transitions, "
                    "similar users hoặc xu hướng mua hàng."
                ),
            }
        ]


@st.cache_resource(show_spinner=False)
def get_rag() -> KBGraphRAG:
    load_dotenv()
    return KBGraphRAG(GraphRAGConfig())


def render_sidebar(rag: KBGraphRAG) -> None:
    st.sidebar.title("Thiết lập")
    st.sidebar.caption("Kết nối Neo4j + RAG")

    st.sidebar.markdown("### Neo4j")
    st.sidebar.code(
        f"URI: {rag.config.uri}\nDB: {rag.config.database}\nUser: {rag.config.user}",
        language="text",
    )

    st.sidebar.markdown("### Tùy chọn")
    top_k = st.sidebar.slider("Số context lấy ra", 3, 12, 6)
    show_context = st.sidebar.toggle("Hiển thị context gốc", value=False)
    use_llm = st.sidebar.toggle(
        "Dùng OpenAI nếu có OPENAI_API_KEY",
        value=bool(rag.config.openai_api_key),
    )

    st.sidebar.markdown("### Mẫu câu hỏi")
    st.sidebar.info(
        "Ví dụ: user 42 đang quan tâm gì?\n"
        "Product 58 có liên hệ với sản phẩm nào?\n"
        "Hành vi nào chuyển từ click sang add_to_cart?\n"
        "User nào tương tự user 18?"
    )

    return top_k, show_context, use_llm


def render_header() -> None:
    st.markdown(
        f"""
        <div class="hero">
            <h1 style="margin-bottom:0.25rem;">{APP_TITLE}</h1>
            <p style="margin-bottom:0; opacity:0.9;">{APP_SUBTITLE}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metrics(rag: KBGraphRAG) -> None:
    with st.container():
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown('<div class="metric-card"><strong>Source</strong><br/>Neo4j KB_Graph</div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="metric-card"><strong>Model</strong><br/>{rag.config.openai_model if rag.config.openai_api_key else "Rule-based fallback"}</div>', unsafe_allow_html=True)
        c3.markdown('<div class="metric-card"><strong>Nodes</strong><br/>User / Session / Event / Product</div>', unsafe_allow_html=True)
        c4.markdown('<div class="metric-card"><strong>RAG</strong><br/>Retrieve + Answer</div>', unsafe_allow_html=True)


def main() -> None:
    st.set_page_config(page_title=APP_TITLE, page_icon="🧠", layout="wide")
    load_dotenv()
    apply_custom_styles()
    init_state()

    rag = get_rag()
    top_k, show_context, use_llm = render_sidebar(rag)
    render_header()
    render_metrics(rag)

    st.markdown("---")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("Nhập câu hỏi về hành vi user, product hoặc conversion path...")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Đang truy xuất KB_Graph và sinh câu trả lời..."):
                if not use_llm:
                    original_key = rag.config.openai_api_key
                    rag.config.openai_api_key = ""
                    result = rag.answer(prompt, top_k=top_k)
                    rag.config.openai_api_key = original_key
                else:
                    result = rag.answer(prompt, top_k=top_k)

                st.markdown(result["answer"])

                if show_context:
                    with st.expander("Context gốc từ graph", expanded=False):
                        st.code(result["context_text"], language="text")

        st.session_state.messages.append({"role": "assistant", "content": result["answer"]})

    with st.expander("Gợi ý truy vấn", expanded=False):
        st.markdown(
            """
            - `user 42 đang xem gì và session nào mạnh nhất?`
            - `product 58 có các sản phẩm tiếp theo nào?`
            - `action chuyển từ click sang add_to_cart ra sao?`
            - `user nào giống user 100 nhất?`
            - `top products theo preference_score là gì?`
            """
        )

    st.caption("Chạy trên ai-service, lấy ngữ cảnh từ Neo4j KB_Graph được dựng từ data_user500.csv.")


if __name__ == "__main__":
    main()
