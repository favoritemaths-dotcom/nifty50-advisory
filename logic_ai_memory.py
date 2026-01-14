# ============================================================
# AI MEMORY MANAGER (Session-based)
# ============================================================

import streamlit as st


def get_memory_key(mode: str, identifier: str):
    return f"ai_memory::{mode}::{identifier}"


def load_memory(mode: str, identifier: str):
    key = get_memory_key(mode, identifier)
    return st.session_state.get(key, [])


def save_to_memory(mode: str, identifier: str, question: str, answer: str):
    key = get_memory_key(mode, identifier)

    if key not in st.session_state:
        st.session_state[key] = []

    st.session_state[key].append({
        "question": question,
        "answer": answer
    })


def clear_memory(mode: str, identifier: str):
    key = get_memory_key(mode, identifier)
    if key in st.session_state:
        del st.session_state[key]
