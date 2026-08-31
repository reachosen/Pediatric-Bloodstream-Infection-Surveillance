from __future__ import annotations

# Pair layout: surveillance class | bedside action, teal / pink / gold. v3

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import streamlit as st

from cases import CASES, REVIEW_WINDOW, get_case
from engine import evaluate_case
from ui import CSS, case_html, header_html, queue_html, spec_html

ICON = ROOT.parent / "public" / "favicon.svg"

st.set_page_config(
    page_title="Aegis",
    page_icon=str(ICON) if ICON.exists() else None,
    layout="wide",
    initial_sidebar_state="collapsed",
)

if "accepted" not in st.session_state:
    st.session_state.accepted = {}
if "notes" not in st.session_state:
    st.session_state.notes = {}

page = st.query_params.get("page", "queue") or "queue"
case_id = st.query_params.get("id", "") or ""

st.markdown(CSS, unsafe_allow_html=True)


def paint(html: str) -> None:
    # st.html skips markdown, so indented tags never become a code fence.
    st.html(html)


if page == "spec":
    paint(header_html("spec", REVIEW_WINDOW["label"]) + spec_html(CASES))
elif page == "case":
    c = get_case(case_id)
    head = header_html("case", REVIEW_WINDOW["label"])
    if not c:
        paint(
            head
            + """
            <div style="text-align:center;padding:4rem 1rem">
              <h1 class="display">Case not in this window</h1>
              <p class="muted">That identifier is not one of the five synthetic review-window fixtures.</p>
              <p><a href="?page=queue">Back to queue</a></p>
            </div>
            """
        )
    else:
        result = evaluate_case(c)
        accepted = bool(st.session_state.accepted.get(c["id"]))
        paint(head + case_html(c, result, accepted))
        note_key = f"note-{c['id']}"
        st.text_area(
            "Infection preventionist note",
            value=st.session_state.notes.get(c["id"], ""),
            key=note_key,
            height=90,
            placeholder="Optional local note — stored in this session only.",
        )
        st.session_state.notes[c["id"]] = st.session_state[note_key]
        label = "Accepted" if accepted else "Accept classification"
        if st.button(label, type="primary"):
            st.session_state.accepted[c["id"]] = not accepted
            st.rerun()
else:
    paint(header_html("queue", REVIEW_WINDOW["label"]) + queue_html(CASES, st.session_state.accepted))
