import streamlit as st
import json
import os

# --- 기존 menaxa.py에 있던 함수들을 그대로 가져옵니다 ---
USER_FILE = "users.json"

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

# ---------------------------------------------------------------------

st.set_page_config(layout="wide")
st.title("👤 마이 프로필")

# 로그인 상태 확인: 로그인 안 했으면 아무것도 표시 안 함
if "user" not in st.session_state or st.session_state["user"] is None:
    st.warning("프로필을 보려면 먼저 로그인해주세요.")
    st.stop() # 로그인 안 했으면 여기서 코드 실행 중지

# 현재 로그인한 사용자 정보 가져오기
username = st.session_state["user"]
users = load_users()
user_data = users.get(username, {})
profile_data = user_data.get("profile", {}) # 프로필 없으면 빈 딕셔너리 반환

# 프로필 정보 화면에 표시하기
st.subheader(f"👋 {profile_data.get('name', username)}님의 프로필")

col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.write("**역할**")
        st.info(f"{user_data.get('role', '정보 없음')}")
        st.write("**전문/관심 분야**")
        st.info(f"{profile_data.get('specialty', '정보 없음')}")

with col2:
    with st.container(border=True):
        st.write("**자기소개**")
        st.info(f"{profile_data.get('intro', '정보 없음')}")

st.markdown("---")

# 프로필 수정 기능 (펼치기/접기 버튼 사용)
with st.expander("✏️ 내 프로필 수정하기"):
    with st.form("profile_form"):
        # 기존 프로필 정보를 기본값으로 설정
        new_name = st.text_input("이름", value=profile_data.get("name", ""))
        new_specialty = st.text_input("전문/관심 분야", value=profile_data.get("specialty", ""))
        new_intro = st.text_area("자기소개", value=profile_data.get("intro", ""))
        
        submitted = st.form_submit_button("저장하기")
        
        if submitted:
            # users 딕셔너리에서 현재 사용자 프로필 정보 업데이트
            # .setdefault('profile', {})는 profile 키가 없을 경우 만들어주는 안전장치
            users[username].setdefault('profile', {})['name'] = new_name
            users[username]['profile']['specialty'] = new_specialty
            users[username]['profile']['intro'] = new_intro
            
            # 변경된 내용을 users.json 파일에 저장
            save_users(users)
            
            st.success("프로필이 성공적으로 업데이트되었습니다!")
            st.rerun() # 페이지 새로고침해서 변경사항 바로 확인
