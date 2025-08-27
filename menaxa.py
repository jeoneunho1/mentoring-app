import streamlit as st
import json
import os

# 사용자 데이터 파일
USER_FILE = "users.json"

# 파일이 없으면 새로 생성
if not os.path.exists(USER_FILE):
    with open(USER_FILE, "w") as f:
        json.dump({}, f)

# 사용자 불러오기 (에러 대비)
def load_users():
    try:
        with open(USER_FILE, "r") as f:
            data = f.read().strip()
            if not data:   # 파일이 비어있으면
                return {}
            return json.loads(data)
    except json.JSONDecodeError:
        return {}

# 사용자 저장하기
def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f)

# 세션 초기화
if "user" not in st.session_state:
    st.session_state.user = None

st.title("🎓 멘토링 플랫폼")

users = load_users()

# 로그인 안 된 상태
if st.session_state.user is None:
    menu = st.sidebar.radio("메뉴", ["로그인", "회원가입"])

    if menu == "로그인":
        st.subheader("로그인")
        username = st.text_input("아이디")
        password = st.text_input("비밀번호", type="password")
        if st.button("로그인"):
            if username in users and users[username]["password"] == password:
                st.session_state.user = username
                st.success(f"{username}님 환영합니다!")
                st.rerun()   # ✅ 최신 방식
            else:
                st.error("로그인 실패")

    elif menu == "회원가입":
        st.subheader("회원가입")
        new_user = st.text_input("새 아이디")
        new_pass = st.text_input("새 비밀번호", type="password")
        role = st.selectbox("역할 선택", ["student", "mentor"])
        if st.button("가입하기"):
            if new_user in users:
                st.error("이미 존재하는 아이디입니다.")
            else:
                users[new_user] = {"password": new_pass, "role": role}
                save_users(users)
                st.success("회원가입 성공! 로그인 해보세요.")

# 로그인 된 상태
else:
    username = st.session_state.user
    role = users[username]["role"]

    st.sidebar.success(f"👋 {username}님 ({role}) 로그인 중")
    if st.sidebar.button("로그아웃"):
        st.session_state.user = None
        st.rerun()   # ✅ 최신 방식

    # 페이지 안내
    st.write("왼쪽 메뉴 `Pages`에서 원하는 기능(질문하기 등)으로 이동하세요.")
