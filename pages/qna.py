import streamlit as st

# 세션 상태 초기화
if "user" not in st.session_state:
    st.session_state.user = None
if "users" not in st.session_state:
    st.session_state.users = {}
if "questions" not in st.session_state:
    st.session_state.questions = []

st.title("💬 질문 & 답변")

if "questions" not in st.session_state:
    st.session_state.questions = []

q = st.text_area("질문을 입력하세요")
if st.button("질문 등록"):
    st.session_state.questions.append({"user": st.session_state.user, "q": q, "a": None})
    st.success("질문이 등록되었습니다!")

st.subheader("📌 질문 목록")
for i, q in enumerate(st.session_state.questions):
    st.write(f"Q{i+1} ({q['user']}): {q['q']}")
    if q["a"]:
        st.write(f"👉 답변: {q['a']}")
    else:
        st.write("⏳ 답변 대기중...")
