import streamlit as st
import json
import os

QUESTIONS_FILE = "questions.json"

# --- ⭐ 1. load_questions 함수 수정 ⭐ ---
def load_questions():
    """questions.json 파일에서 질문 데이터를 불러옵니다."""
    if not os.path.exists(QUESTIONS_FILE):
        return [] # 파일이 없으면 빈 리스트 반환
    with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            # 데이터가 리스트 형태인지 확인하고, 아니면 빈 리스트 반환
            if isinstance(data, list):
                return data
            else:
                return [] # 파일 내용은 있지만 리스트가 아니면 초기화
        except json.JSONDecodeError:
            return [] # 파일이 비어있거나 손상되었으면 빈 리스트 반환

def save_questions(questions):
    """질문 데이터를 questions.json 파일에 저장합니다."""
    with open(QUESTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=4)

# --- 세션 상태 초기화 ---
if "questions" not in st.session_state:
    st.session_state["questions"] = load_questions()

# --- UI 구성 ---
st.title("💬 Q&A 게시판")

if st.session_state.get("user") is None:
    st.warning("질문/답변 기능을 이용하려면 먼저 로그인 해주세요. 🙏")
else:
    if st.session_state.get("role") == "student":
        st.subheader("📌 질문하기")
        with st.form("qna_form", clear_on_submit=True):
            q_content = st.text_area("궁금한 점을 자유롭게 질문하세요.", key="new_question_content")
            submitted = st.form_submit_button("질문 등록하기")
            if submitted:
                if q_content.strip():
                    new_q = {
                        "user": st.session_state["user"],
                        "q": q_content,
                        "a": None
                    }
                    # st.session_state["questions"]가 항상 리스트임을 보장받음
                    st.session_state["questions"].insert(0, new_q)
                    save_questions(st.session_state["questions"])
                    st.success("질문이 성공적으로 등록되었습니다!")
                    st.rerun() # rerun을 form 바깥으로 옮기면 더 안정적일 수 있으나, 여기선 유지
                else:
                    st.error("질문 내용을 입력해주세요.")

    st.markdown("---")

    # --- 질문 목록 ---
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
                        with st.form(f"answer_form_{i}"):
                            a_content = st.text_input("답변을 입력하세요", key=f"ans_content_{i}")
                            if st.form_submit_button("답변 등록", key=f"ans_btn_{i}"):
                                if a_content.strip():
                                    st.session_state["questions"][i]["a"] = a_content
                                    save_questions(st.session_state["questions"])
                                    st.success("답변이 등록되었습니다!")
                                    st.rerun()
                                else:
                                    st.error("답변 내용을 입력해주세요.")
                    else:
                        st.write("멘토의 답변을 기다리고 있습니다.")
                
                can_delete = (st.session_state["user"] == q_item["user"] or st.session_state.get("role") == "mentor")
                if can_delete:
                    if st.button(f"삭제하기", key=f"del_btn_{i}", type="secondary"):
                        st.session_state["questions"].pop(i)
                        save_questions(st.session_state["questions"])
                        st.warning("질문이 삭제되었습니다.")
                        st.rerun()
