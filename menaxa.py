import streamlit as st

users = {"student": "1234", "mentor": "abcd"}
questions = []

if "user" not in st.session_state:
    st.session_state.user = None

st.title("🎓 멘토링 플랫폼 (Streamlit)")

if st.session_state.user is None:
    st.subheader("로그인")
    username = st.text_input("아이디")
    password = st.text_input("비밀번호", type="password")
    if st.button("로그인"):
        if username in users and users[username] == password:
            st.session_state.user = username
            st.success(f"{username}님 환영합니다!")
        else:
            st.error("로그인 실패")
else:
    st.sidebar.write(f"👋 {st.session_state.user}님 로그인 중")
    if st.sidebar.button("로그아웃"):
        st.session_state.user = None
        st.experimental_rerun()

    if st.session_state.user == "student":
        st.subheader("질문하기")
        q = st.text_area("궁금한 점을 입력하세요")
        if st.button("등록"):
            questions.append({"q": q, "a": None})
            st.success("질문 등록 완료!")

    elif st.session_state.user == "mentor":
        st.subheader("학생 질문 목록")
        for i, q in enumerate(questions):
            st.write(f"Q{i+1}: {q['q']}")
            if q["a"] is None:
                a = st.text_input(f"답변 입력 (Q{i+1})", key=f"a{i}")
                if st.button(f"답변 달기 (Q{i+1})"):
                    questions[i]["a"] = a
                    st.success("답변 등록 완료!")
            else:
                st.write(f"👉 답변: {q['a']}")
