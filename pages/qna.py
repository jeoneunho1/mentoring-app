import streamlit as st

st.title("💬 Q&A 게시판")

# ✅ 세션 상태 초기화 (딕셔너리 방식으로만 접근!)
if "user" not in st.session_state:
    st.session_state["user"] = None
if "role" not in st.session_state:
    st.session_state["role"] = None
if "questions" not in st.session_state:
    st.session_state["questions"] = []

# ---------------------------
# 로그인 안 했을 때
# ---------------------------
if st.session_state["user"] is None:
    st.warning("질문/답변 기능을 이용하려면 먼저 로그인 해주세요 🙏")

# ---------------------------
# 로그인 했을 때
# ---------------------------
else:
    # --- 학생: 질문 등록 ---
    if st.session_state["role"] == "student":
        st.subheader("📌 질문하기")
        q = st.text_area("궁금한 점을 입력하세요", key="new_q")
        if st.button("질문 등록"):
            if q.strip() != "":
                st.session_state["questions"].append(
                    {"user": st.session_state["user"], "q": q, "a": None}
                )
                st.success("질문이 등록되었습니다!")
                st.rerun()  # 새로고침해서 입력창 초기화
            else:
                st.error("내용을 입력해주세요.")

    # --- 질문 목록 (학생 & 멘토 둘 다 볼 수 있음) ---
    st.subheader("📖 질문 목록")
    if len(st.session_state["questions"]) == 0:
        st.info("아직 등록된 질문이 없습니다.")
    else:
        for i, q in enumerate(st.session_state["questions"]):
            st.write(f"**Q{i+1}. {q['q']}** (작성자: {q['user']})")

            # 답변 달기 (멘토 전용)
            if st.session_state["role"] == "mentor" and q["a"] is None:
                a = st.text_input(f"답변 입력 (Q{i+1})", key=f"ans_{i}")
                if st.button(f"답변 달기 (Q{i+1})", key=f"ans_btn_{i}"):
                    st.session_state["questions"][i]["a"] = a
                    st.success("답변이 등록되었습니다!")
                    st.rerun()

            # 답변 보여주기
            if q["a"] is not None:
                st.write(f"👉 답변: {q['a']}")

            # 질문 삭제 (작성자 본인 또는 멘토만 가능)
            if (
                st.session_state["user"] == q["user"]
                or st.session_state["role"] == "mentor"
            ):
                if st.button(f"삭제하기 (Q{i+1})", key=f"del_{i}"):
                    st.session_state["questions"].pop(i)
                    st.warning("질문이 삭제되었습니다!")
                    st.rerun()
