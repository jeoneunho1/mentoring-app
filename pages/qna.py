import streamlit as st

st.title("💬 질문 / 답변 페이지")

# 로그인 안 했으면 접근 제한
if "user" not in st.session_state or st.session_state.user is None:
    st.error("⚠️ 먼저 로그인 해주세요!")
    st.stop()

username = st.session_state.user

# 질문 저장용 세션
if "questions" not in st.session_state:
    st.session_state.questions = []

# 역할 확인
users = {"dummy": "test"}  # 필요 시 불러올 수 있지만 여기선 간단히
role = "student"  # 기본값
if "user" in st.session_state and st.session_state.user is not None:
    # 임시로 student/mentor 구분
    # 실제로는 users.json에서 role을 불러와야 함
    import json
    with open("users.json", "r") as f:
        users_data = json.load(f)
    role = users_data[username]["role"]

# 학생 기능
if role == "student":
    st.subheader("🙋 질문하기")
    q = st.text_area("궁금한 점을 입력하세요")
    if st.button("질문 등록"):
        st.session_state.questions.append({"user": username, "q": q, "a": None})
        st.success("질문 등록 완료!")

# 멘토 기능
elif role == "mentor":
    st.subheader("📋 학생 질문 목록")
    if len(st.session_state.questions) == 0:
        st.info("아직 등록된 질문이 없습니다.")
    for i, q in enumerate(st.session_state.questions):
        st.write(f"**Q{i+1} ({q['user']})**: {q['q']}")
        if q["a"] is None:
            a = st.text_input(f"답변 입력 (Q{i+1})", key=f"a{i}")
            if st.button(f"답변 달기 (Q{i+1})"):
                st.session_state.questions[i]["a"] = a
                st.success("답변 등록 완료!")
        else:
            st.write(f"👉 답변: {q['a']}")
