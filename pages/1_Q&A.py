import streamlit as st
import json
import os

QUESTIONS_FILE = "questions.json"

# ---------------------------
# 질문/답변 데이터 저장 및 불러오기 함수
# ---------------------------
def load_questions():
    """questions.json 파일에서 질문 데이터를 불러옵니다."""
    if not os.path.exists(QUESTIONS_FILE):
        return []
    with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_questions(questions):
    """질문 데이터를 questions.json 파일에 저장합니다."""
    with open(QUESTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=4)

# ---------------------------
# 세션 상태 초기화
# ---------------------------
if "questions" not in st.session_state:
    st.session_state["questions"] = load_questions()

# ---------------------------
# UI 구성
# ---------------------------
st.title("💬 Q&A 게시판")

# ✅ 요청 2: 로그인하지 않은 사용자는 질문/답변 기능을 사용할 수 없도록 제한합니다.
# st.session_state에 "user" 키가 없거나 그 값이 None이면, 즉 로그인 상태가 아니면 경고 메시지를 표시합니다.
if st.session_state.get("user") is None:
    st.warning("질문/답변 기능을 이용하려면 먼저 로그인 해주세요. 🙏")
# --- 로그인한 사용자만 아래 코드를 볼 수 있습니다. ---
else:
    # 학생 역할일 때만 질문 등록 폼이 보입니다.
    if st.session_state.get("role") == "student":
        st.subheader("📌 질문하기")
        q_content = st.text_area("궁금한 점을 자유롭게 질문하세요.", key="new_question_content")
        if st.button("질문 등록하기"):
            if q_content.strip():
                new_q = {
                    "user": st.session_state["user"],
                    "q": q_content,
                    "a": None
                }
                st.session_state["questions"].insert(0, new_q)
                save_questions(st.session_state["questions"])
                st.success("질문이 성공적으로 등록되었습니다!")
                st.rerun()
            else:
                st.error("질문 내용을 입력해주세요.")

    st.markdown("---")

    # --- 질문 목록 ---
    st.subheader("📖 질문 목록")
    if not st.session_state["questions"]:
        st.info("아직 등록된 질문이 없습니다. 첫 질문을 남겨보세요!")
    else:
        for i, q_item in enumerate(st.session_state["questions"]):
            with st.container():
                st.markdown(f"**Q{len(st.session_state['questions']) - i}. {q_item['q']}**")
                st.caption(f"작성자: {q_item['user']}")

                # 답변이 이미 달려있는 경우, 답변을 보여줍니다.
                if q_item["a"] is not None:
                    st.info(f"**A:** {q_item['a']}")
                # 답변이 아직 없는 경우
                else:
                    # ✅ 요청 1: 질문에 답하는 기능 (멘토 전용)
                    # 현재 로그인한 사용자의 역할이 'mentor'일 경우, 답변 입력 UI를 보여줍니다.
                    if st.session_state.get("role") == "mentor":
                        a_content = st.text_input(f"답변을 입력하세요 (Q{len(st.session_state['questions']) - i})", key=f"ans_content_{i}")
                        if st.button(f"답변 등록 (Q{len(st.session_state['questions']) - i})", key=f"ans_btn_{i}"):
                            if a_content.strip():
                                # 해당 질문에 답변 내용 저장
                                st.session_state["questions"][i]["a"] = a_content
                                save_questions(st.session_state["questions"])
                                st.success("답변이 등록되었습니다!")
                                st.rerun()
                            else:
                                st.error("답변 내용을 입력해주세요.")
                    # 멘토가 아니면 답변 대기 메시지를 보여줍니다.
                    else:
                        st.write("멘토의 답변을 기다리고 있습니다.")
                
                # ✅ 요청 3: 내가 올린 질문 삭제 기능
                # 현재 로그인한 사용자가 질문 작성자이거나, 역할이 'mentor'일 경우에만 삭제 버튼이 보입니다.
                can_delete = (st.session_state["user"] == q_item["user"] or st.session_state.get("role") == "mentor")
                if can_delete:
                    if st.button(f"삭제하기 (Q{len(st.session_state['questions']) - i})", key=f"del_btn_{i}"):
                        # 리스트에서 해당 질문 삭제
                        st.session_state["questions"].pop(i)
                        save_questions(st.session_state["questions"])
                        st.warning("질문이 삭제되었습니다.")
                        st.rerun()

                st.markdown("---")
