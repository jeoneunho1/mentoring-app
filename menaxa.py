import streamlit as st
import json, os

# 사용자 데이터 파일
USER_FILE = "users.json"
if not os.path.exists(USER_FILE):
    with open(USER_FILE, "w") as f:
        json.dump({}, f)

# 사용자 불러오기
def load_users():
    with open(USER_FILE, "r") as f:
        return json.load(f)

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
                st.experimental_rerun()
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
        st.experimental_rerun()

    # 페이지 안내
    st.write("왼쪽 메뉴 `Pages`에서 원하는 기능(질문하기 등)으로 이동하세요.")
