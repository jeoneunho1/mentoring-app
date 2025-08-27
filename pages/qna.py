import streamlit as st

# 세션 상태 기본값 초기화
if "user" not in st.session_state:
    st.session_state["user"] = None
if "users" not in st.session_state:
    st.session_state["users"] = {}
if "questions" not in st.session_state:
    st.session_state["questions"] = []

st.title("💬 Q&A 게시판")

# 로그인 여부 확인
if st.session_state["user"] is None:
    st.warning("로그인 후 이용 가능합니다.")
    st.stop()

username = st.session_state["user"]

# ---------------------------
# 질문 등록
# ---------------------------
st.subheader("✏️ 질문하기")
q = st.text_area("궁금한 점을 입력하세요")
if st.button("질문 등록"):
    if q.strip():
        st.session_state["questions"].append({"user": username, "q": q, "a": None})
        st.success("질문이 등록되었습니다!")
    else:
        st.error("질문 내용을 입력하세요.")

st.write("---")

# ---------------------------
# 질문 목록 & 답변
# ---------------------------
st.subheader("📋 질문 목록")

if len(st.session_state["questions"]) == 0:
    st.info("아직 등록된 질문이 없습니다.")
else:
    for i, q in enumerate(st.session_state["questions"]):
        st.markdown(f"**Q{i+1}. {q['user']}의 질문:** {q['q']}")

        # 답변 (멘토만 가능)
        if q["a"] is None:
            if username in st.session_state["users"] and \
               st.session_state["users"][username]["role"] == "mentor":
                a = st.text_input(f"답변 입력 (Q{i+1})", key=f"a{i}")
                if st.button(f"답변 달기 (Q{i+1})"):
                    st.session_state["questions"][i]["a"] = a
                    st.success("답변이 등록되었습니다!")
        else:
            st.markdown(f"👉 **답변:** {q['a']}")

        # 본인 질문 삭제
        if q["user"] == username:
            if st.button(f"❌ 질문 삭제 (Q{i+1})"):
                st.session_state["questions"].pop(i)
                st.success("질문이 삭제되었습니다!")
                st.rerun()

        st.write("---")
