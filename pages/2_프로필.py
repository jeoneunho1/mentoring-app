import streamlit as st
import json
import os

# --- 유틸리티 함수 (기존과 동일) ---
USER_FILE = "users.json"

def load_users():
    if not os.path.exists(USER_FILE): return {}
    with open(USER_FILE, "r", encoding="utf-8") as f:
        try: return json.load(f)
        except json.JSONDecodeError: return {}

def save_users(users):
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

# ---------------------------------------------------------------------

st.set_page_config(layout="wide")
st.title("👤 마이 프로필")

if "user" not in st.session_state or st.session_state["user"] is None:
    st.warning("프로필을 보려면 먼저 로그인해주세요.")
    st.stop()

username = st.session_state["user"]
users = load_users()
user_data = users.get(username, {})
profile_data = user_data.get("profile", {})

# --- ⭐ 1. 태그를 리스트 형태로 가져오도록 변경 ---
# 기존에 문자열로 저장된 specialty가 있다면, 쉼표로 구분된 리스트로 변환
specialty = profile_data.get("specialty", [])
if isinstance(specialty, str):
    specialty = [s.strip() for s in specialty.split(',')]

# --- 프로필 정보 화면에 표시 ---
st.subheader(f"👋 {profile_data.get('name', username)}님의 프로필")
col1, col2 = st.columns(2)
with col1:
    with st.container(border=True):
        st.write("**역할**")
        st.info(f"{user_data.get('role', '정보 없음')}")
        st.write("**전문/관심 분야**")
        # 태그를 예쁘게 표시
        if specialty:
            st.write(" ".join(f"`{s}`" for s in specialty))
        else:
            st.info("정보 없음")

with col2:
    with st.container(border=True):
        st.write("**자기소개**")
        st.info(f"{profile_data.get('intro', '정보 없음')}")

st.markdown("---")

# --- 프로필 수정 기능 ---
with st.expander("✏️ 내 프로필 수정하기"):
    with st.form("profile_form"):
        new_name = st.text_input("이름", value=profile_data.get("name", ""))
        
        # --- ⭐ 2. st.text_input을 st.multiselect로 변경 ---
        # 선택 가능한 전체 태그 목록
        all_tags = [
            "파이썬", "데이터 분석", "AI", "머신러닝", "웹 개발", 
            "Streamlit", "진로상담", "취업/이직", "포트폴리오"
        ]
        # st.multiselect를 사용해 여러 태그를 선택 가능하게 함
        new_specialty = st.multiselect(
            "전문/관심 분야 (여러 개 선택 가능)",
            options=all_tags,
            default=specialty # 기존에 선택했던 태그들을 기본값으로 표시
        )
        
        new_intro = st.text_area("자기소개", value=profile_data.get("intro", ""))
        
        submitted = st.form_submit_button("저장하기")
        if submitted:
            users[username].setdefault('profile', {})['name'] = new_name
            users[username]['profile']['specialty'] = new_specialty # 리스트 형태로 저장
            users[username]['profile']['intro'] = new_intro
            
            save_users(users)
            st.success("프로필이 성공적으로 업데이트되었습니다!")
            st.rerun()
