import streamlit as st

st.title("💬 Q&A 게시판")

# ---------------------------
# 세션 상태 기본값
# ---------------------------
if "questions" not in st.session_state:
    st.session_state["questions"] = []  # 질문 목록
if "user" not in st.session_state:
    st.session_state["user"] = None     # 로그인된 사용자

# ---------------------------
# 로그인 확인
# ---------------------------
if st.session_state["user"] is None:
    st.warning("👉 질문을 등록하려면 먼저 로그인해주세요.")
else:
    # ---------------------------
    # 질문 등록
    # ---------------------------
    st.subheader("✍️ 질문하기")
    q = st.text_area("질문 내용")
    if st.button("질문 등록"):
        if q.strip():
            st.session_state.questions.append({
                "user": st.session_state["user"],
                "q": q,
                "a": None
            })
            st.success("질문이 등록되었습니다!")
        else:
            st.error("질문 내용을 입력해주세요.")

# ---------------------------
# 질문 목록 & 답변/삭제
# ---------------------------
st.subheader("📋 등록된 질문들")

if not st.session_state.questions:
    st.info("아직 등록된 질문이 없습니다.")
else:
    for idx, item in enumerate(st.session_state.questions):
        with st.container():
            st.markdown(f"**Q{idx+1}. {item['q']}**  (작성자: `{item['user']}`)")

            # 답변이 달렸으면 보여주기
            if item["a"]:
                st.success(f"👉 답변: {item['a']}")

            # ---------------------------
            # 로그인한 경우에만 답변/삭제 버튼
            # ---------------------------
            if st.session_state["user"]:
                col1, col2 = st.columns(2)

                # 답변 버튼 (멘토/누구든 가능하게)
                with col1:
                    answer = st.text_input(f"답변 입력 (Q{idx+1})", key=f"answer_{idx}")
                    if st.button(f"답변 등록 (Q{idx+1})"):
                        if answer.strip():
                            st.session_state.questions[idx]["a"] = answer
                            st.success("답변이 등록되었습니다!")
                            st.rerun()

                # 삭제 버튼 (작성자만 삭제 가능)
                with col2:
                    if st.session_state["user"] == item["user"]:
                        if st.button(f"질문 삭제 (Q{idx+1})"):
                            st.session_state.questions.pop(idx)
                            st.warning("질문이 삭제되었습니다.")
                            st.rerun()
            st.markdown("---")
