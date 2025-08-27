import streamlit as st
import json
import os

# --- 다른 파일들에도 있는, 사용자 데이터를 불러오는 함수입니다 ---
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

# ---------------------------------------------------------------------

st.set_page_config(layout="wide")
st.title("👨‍🏫 멘토 찾기")
st.info("나에게 필요한 조언을 해줄 수 있는 멘토를 찾아보세요!")

# 1. 전체 사용자 정보 불러오기
all_users = load_users()

# 2. 멘토 역할을 가진 사용자만 필터링하기
mentors = {username: data for username, data in all_users.items() if data.get("role") == "mentor"}

# 3. 검색창 만들기
search_term = st.text_input(
    "🔍 전문 분야로 멘토 검색하기", 
    placeholder="예: 파이썬, AI, 데이터 분석"
)

st.markdown("---")

# 4. 필터링된 멘토 목록 보여주기
if not mentors:
    st.warning("아직 등록된 멘토가 없습니다.")
else:
    # 검색어에 따라 보여줄 멘토 목록을 다시 필터링
    filtered_mentors = {}
    if search_term:
        for username, data in mentors.items():
            profile = data.get("profile", {})
            specialty = profile.get("specialty", "").lower() # 소문자로 변환하여 검색 정확도 높임
            if search_term.lower() in specialty:
                filtered_mentors[username] = data
    else:
        # 검색어가 없으면 모든 멘토를 보여줌
        filtered_mentors = mentors

    if not filtered_mentors:
        st.info(f"'{search_term}' 분야의 멘토를 찾을 수 없습니다.")
    else:
        # st.columns를 사용해 한 줄에 여러 멘토 카드 표시
        cols = st.columns(3) # 한 줄에 3명씩 보여주기
        i = 0
        for username, data in filtered_mentors.items():
            profile = data.get("profile", {})
            with cols[i % 3]: # 0, 1, 2, 0, 1, 2... 순서로 컬럼에 접근
                with st.container(border=True, height=250):
                    st.subheader(f"{profile.get('name', username)}")
                    st.caption(f"@{username}")
                    st.markdown(f"**전문 분야**: {profile.get('specialty', '정보 없음')}")
                    st.write(profile.get('intro', '자기소개 없음'))
            i += 1
