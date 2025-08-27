import streamlit as st
import json
import os

USER_FILE = "users.json"

# ---------------------------
# 유저 저장 & 불러오기
# ---------------------------
def load_users():
    if not os.path.exists(USER_FILE):
        return {}
    with open(USER_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_users(users):
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

# ---------------------------
# 세션 상태 기본값
# ---------------------------
if "user" not in st.session_state:
    st.session_state["user"] = None
if "role" not in st.session_state:   # ✅ 역할도 세션에 저장
    st.session_state["role"] = None
if "users" not in st.session_state:
    st.session_state["users"] = load_users()

# ---------------------------
# UI
# ---------------------------
st.title("👋 Menaxa 멘토링 플랫폼")

menu = st.sidebar.radio("메뉴", ["로그인", "회원가입", "로그아웃"])

# ---------------------------
# 로그인
# ---------------------------
if menu == "로그인":
    st.subheader("🔑 로그인")

    username = st.text_input("아이디")
    password = st.text_input("비밀번호", type="password")

    if st.button("로그인"):
        users = st.session_state["users"]
        if username in users and users[username]["password"] == password:
            st.session_state["user"] = username
            st.session_state["role"] = users[username]["role"]   # ✅ 역할 저장
            st.success(f"{username}님, 환영합니다! (역할: {st.session_state['role']})")
            st.rerun()
        else:
            st.error("아이디 또는 비밀번호가 올바르지 않습니다.")

# ---------------------------
# 회원가입
# ---------------------------
elif menu == "회원가입":
    st.subheader("📝 회원가입")

    new_username = st.text_input("새 아이디")
    new_password = st.text_input("새 비밀번호", type="password")
    role = st.selectbox("역할 선택", ["student", "mentor"])

    if st.button("회원가입"):
        users = st.session_state["users"]
        if new_username in users:
            st.error("이미 존재하는 아이디입니다.")
        elif new_username.strip() == "" or new_password.strip() == "":
            st.error("아이디와 비밀번호를 입력하세요.")
        else:
            users[new_username] = {"password": new_password, "role": role}
            st.session_state["users"] = users
            save_users(users)
            st.success("회원가입 성공! 로그인 해주세요.")

# ---------------------------
# 로그아웃
# ---------------------------
elif menu == "로그아웃":
    if st.session_state["user"] is not None:
        st.success(f"{st.session_state['user']}님이 로그아웃 되었습니다.")
        st.session_state["user"] = None
        st.session_state["role"] = None   # ✅ 로그아웃 시 역할도 초기화
        st.rerun()
    else:
        st.info("현재 로그인된 유저가 없습니다.")
