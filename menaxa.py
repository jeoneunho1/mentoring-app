import streamlit as st
import json
import os
import hashlib # 비밀번호 암호화를 위한 라이브러리

USER_FILE = "users.json"

# --- ⭐ 1. 비밀번호를 해싱하는 함수 추가 ---
def hash_password(password):
    """입력받은 비밀번호를 SHA-256 알고리즘으로 해싱하여 반환합니다."""
    # sha256 객체 생성
    sha256 = hashlib.sha256()
    # 비밀번호를 바이트로 인코딩하여 해시 업데이트
    sha256.update(password.encode('utf-8'))
    # 해시된 값을 16진수 문자열로 반환
    return sha256.hexdigest()

# --- 유틸리티 함수 (기존과 동일) ---
def load_users():
    if not os.path.exists(USER_FILE): return {}
    with open(USER_FILE, "r", encoding="utf-8") as f:
        try: return json.load(f)
        except json.JSONDecodeError: return {}

def save_users(users):
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

# --- 세션 상태 초기화 (기존과 동일) ---
if "user" not in st.session_state: st.session_state["user"] = None
if "role" not in st.session_state: st.session_state["role"] = None
if "users" not in st.session_state: st.session_state["users"] = load_users()
if "auth_mode" not in st.session_state: st.session_state["auth_mode"] = "login"

st.title("👋 Menaxa 멘토링 플랫폼")

# --- 로그인 상태일 때의 화면 (기존과 동일) ---
if st.session_state["user"]:
    st.sidebar.success(f"**{st.session_state['user']}**님 ({st.session_state['role']})으로 로그인 중")
    if st.sidebar.button("로그아웃"):
        st.session_state["user"] = None
        st.session_state["role"] = None
        st.session_state["auth_mode"] = "login"
        st.rerun()
    st.markdown("---")
    st.info("사이드바에서 다른 페이지로 이동할 수 있습니다.")

# --- 로그아웃 상태일 때의 화면 ---
else:
    if st.session_state["auth_mode"] == "login":
        st.subheader("🔑 로그인")
        username = st.text_input("아이디")
        password = st.text_input("비밀번호", type="password")
        col1, col2 = st.columns([1, 1])
        
        if col1.button("로그인", use_container_width=True):
            users = st.session_state["users"]
            # --- ⭐ 3. 로그인 시 비밀번호 비교 로직 변경 ---
            # 입력된 비밀번호를 해싱하여 저장된 해시값과 비교
            hashed_input_password = hash_password(password)
            if username in users and users[username]["password"] == hashed_input_password:
                st.session_state["user"] = username
                st.session_state["role"] = users[username]["role"]
                st.rerun()
            else:
                st.error("아이디 또는 비밀번호가 올바지 않습니다.")
        
        if col2.button("회원가입하기", type="secondary", use_container_width=True):
            st.session_state["auth_mode"] = "signup"
            st.rerun()

    elif st.session_state["auth_mode"] == "signup":
        st.subheader("📝 회원가입")
        new_username = st.text_input("새 아이디")
        new_password = st.text_input("새 비밀번호", type="password")
        role = st.selectbox("역할 선택", ["student", "mentor"])

        if st.button("회원가입 완료"):
            users = st.session_state["users"]
            if new_username in users:
                st.error("이미 존재하는 아이디입니다.")
            elif not new_username.strip() or not new_password.strip():
                st.error("아이디와 비밀번호는 공백일 수 없습니다.")
            else:
                # --- ⭐ 2. 회원가입 시 비밀번호 저장 로직 변경 ---
                # 비밀번호를 해싱하여 저장
                hashed_password = hash_password(new_password)
                users[new_username] = {"password": hashed_password, "role": role}
                st.session_state["users"] = users
                save_users(users)
                st.success("회원가입 성공! 로그인 페이지로 이동합니다.")
                st.session_state["auth_mode"] = "login"
                st.rerun()
        
        if st.button("로그인 화면으로 돌아가기", type="secondary"):
            st.session_state["auth_mode"] = "login"
            st.rerun()
