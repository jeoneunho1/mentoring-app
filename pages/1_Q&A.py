import streamlit as st
from streamlit_autorefresh import st_autorefresh # --- ⭐ 1. 이 줄 추가 ⭐ ---
import json
import os

QUESTIONS_FILE = "questions.json"

def load_questions():
    if not os.path.exists(QUESTIONS_FILE):
        return []
    with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            return data if isinstance(data, list) else []
        except (json.JSONDecodeError, UnicodeDecodeError):
            return []

def save_questions(questions):
    with open(QUESTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=4)

if "questions" not in st.session_state:
    st.session_state["questions"] = load_questions()

# --- ⭐ 2. 이 줄 추가 (5초마다 새로고침) ⭐ ---
st_autorefresh(interval=3000, limit=None, key="qna_autorefresh")

st.title("💬 Q&A 게시판")
st.caption("이 페이지는 3초마다 자동으로 업데이트됩니다.")

if 'selected_question' in st.session_state:
    selected_q_text = st.session_state.pop('selected_question')
    selected_q_item = next((q for q in st.session_state["questions"] if q['q'] == selected_q_text), None)
    
    if selected_q_item:
        st.subheader("🔎 마이페이지에서 선택한 질문")
        with st.container(border=True):
            st.markdown(f"**Q. {selected_q_item['q']}**")
            st.caption(f"작성자: {selected_q_item['user']}")
            if selected_q_item.get("a"):
                st.info(f"**A:** {selected_q_item['a']}")
            else:
                st.warning("아직 답변이 등록되지 않았습니다.")
        st.markdown("---")

if st.session_state.get("user") is None:
    st.warning("질문/답변 기능을 이용하려면 먼저 로그인 해주세요. 🙏")
else:
    if st.session_state.get("role") == "student":
        st.subheader("📌 질문하기")
        with st.form("qna_form", clear_on_submit=True):
            q_content = st.text_area("궁금한 점을 자유롭게 질문하세요.")
            if st.form_submit_button("질문 등록하기"):
                if q_content.strip():
                    new_q = {"user": st.session_state["user"], "q": q_content, "a": None}
                    st.session_state["questions"].insert(0, new_q)
                    save_questions(st.session_state["questions"])
                    st.success("질문이 성공적으로 등록되었습니다!")
                    st.rerun()
                else:
                    st.error("질문 내용을 입력해주세요.")
    st.markdown("---")
    st.subheader("📖 질문 목록")
    if not st.session_state["questions"]:
        st.info("아직 등록된 질문이 없습니다. 첫 질문을 남겨보세요!")
    else:
        for i, q_item in enumerate(st.session_state["questions"]):
            with st.container(border=True):
                st.markdown(f"**Q. {q_item['q']}**")
                st.caption(f"작성자: {q_item['user']}")
                if q_item.get("a"):
                    st.info(f"**A:** {q_item['a']}")
                else:
                    if st.session_state.get("role") == "mentor":
                        a_content = st.text_area("답변을 입력하세요", key=f"ans_{i}")
                        if st.button("답변 등록", key=f"ans_btn_{i}"):
                            if a_content.strip():
                                st.session_state["questions"][i]["a"] = a_content
                                save_questions(st.session_state["questions"])
                                st.success("답변이 등록되었습니다!")
                                st.rerun()
                    else:
                        st.write("멘토의 답변을 기다리고 있습니다.")
                if st.session_state.get("user", "") == q_item.get("user") or st.session_state.get("role") == "mentor":
                    if st.button("삭제하기", key=f"del_{i}", type="secondary"):
                        st.session_state["questions"].pop(i)
                        save_questions(st.session_state["questions"])
                        st.warning("질문이 삭제되었습니다.")
                        st.rerun()
