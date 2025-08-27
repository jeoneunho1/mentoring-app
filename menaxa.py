import streamlit as st
import json
import os

USER_FILE = "users.json"

# ---------------------------
# 사용자 정보 저장 및 불러오기 함수
# ---------------------------
def load_users():
    """users.json 파일에서 사용자 정보를 불러옵니다."""
    if not os.path.exists(USER_FILE):
        return {}
    with open(USER_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_users(users):
    """사용자 정보를 users.json 파일에 저장합니다."""
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

# ---------------------------
# 세션 상태 초기화
# ---------------------------
# 앱이 실행되는 동안 사용자 정보를 유지하기 위해 세션 상태를 사용합니다.
if "user" not in st.session_state:
    st.session_state["user"] = None
if "role" not in st.session_state:
    st.session_state["role"] = None
if "users" not in st.session_state:
    st.session_state["users"] = load_users()

# ---------------------------
# UI 구성
# ---------------------------
st.title("👋 Menaxa 멘토링 플랫폼")

# 사이드바 메뉴
menu = st.sidebar.radio("메뉴", ["로그인", "회원가입", "로그아웃"])

# ---------------------------
# 로그인 기능
# ---------------------------
if menu == "로그인":
    st.subheader("🔑 로그인")

    username = st.text_input("아이디")
    password = st.text_input("비밀번호", type="password")

    if st.button("로그인"):
        users = st.session_state["users"]
        # 사용자 정보가 일치하는지 확인
        if username in users and users[username]["password"] == password:
            st.session_state["user"] = username
            st.session_state["role"] = users[username]["role"]
            st.success(f"{username}님, 환영합니다! (역할: {st.session_state['role']})")
            st.rerun() # 페이지를 새로고침하여 로그인 상태를 즉시 반영
        else:
            st.error("아이디 또는 비밀번호가 올바르지 않습니다.")

# ---------------------------
# 회원가입 기능
# ---------------------------
elif menu == "회원가입":
    st.subheader("📝 회원가입")

    new_username = st.text_input("새 아이디")
    new_password = st.text_input("새 비밀번호", type="password")
    role = st.selectbox("역할 선택", ["student", "mentor"]) # 역할 선택 기능

    if st.button("회원가입"):
        users = st.session_state["users"]
        if new_username in users:
            st.error("이미 존재하는 아이디입니다.")
        elif not new_username.strip() or not new_password.strip():
            st.error("아이디와 비밀번호는 공백일 수 없습니다.")
        else:
            # 새 사용자 정보 추가
            users[new_username] = {"password": new_password, "role": role}
            st.session_state["users"] = users
            save_users(users) # 파일에 저장
            st.success("회원가입 성공! 로그인 페이지로 이동하여 로그인 해주세요.")

# ---------------------------
# 로그아웃 기능
# ---------------------------
elif menu == "로그아웃":
    if st.session_state["user"] is not None:
        st.success(f"{st.session_state['user']}님이 안전하게 로그아웃 되었습니다.")
        # 세션 상태 초기화
        st.session_state["user"] = None
        st.session_state["role"] = None
        st.rerun() # 페이지 새로고침
    else:
        st.info("현재 로그인된 사용자가 없습니다.")

# ---------------------------
# 로그인 상태 표시
# ---------------------------
if st.session_state["user"]:
    st.sidebar.success(f"**{st.session_state['user']}**님 ({st.session_state['role']})으로 로그인 중")
    st.markdown("---")
    st.info("사이드바에서 다른 페이지로 이동할 수 있습니다.")
else:
    st.warning("로그인 후 Q&A 게시판 등 모든 기능을 이용할 수 있습니다.")
