import streamlit as st
import json
import os

# --- 유틸리티 함수 (기존과 동일) ---
USER_FILE = "users.json"
REVIEWS_FILE = "reviews.json"

def load_data(filepath):
    if not os.path.exists(filepath): return {}
    with open(filepath, "r", encoding="utf-8") as f:
        try: return json.load(f)
        except json.JSONDecodeError: return {}

def save_data(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
# -----------------------

st.set_page_config(layout="wide")

# --- ⭐ 1. st.session_state를 이용해 선택된 태그 저장 ---
if 'selected_tag' not in st.session_state:
    st.session_state['selected_tag'] = None

st.title("👨‍🏫 멘토 찾기")
st.info("나에게 필요한 조언을 해줄 수 있는 멘토를 찾아보세요!")

all_users = load_data(USER_FILE)
all_reviews = load_data(REVIEWS_FILE)
mentors = {uid: data for uid, data in all_users.items() if data.get("role") == "mentor"}
is_logged_in = "user" in st.session_state and st.session_state["user"] is not None
current_user_id = st.session_state["user"] if is_logged_in else None
current_user_role = st.session_state.get("role") if is_logged_in else None

# --- ⭐ 2. 전체 태그 목록 수집 및 필터링 UI ---
all_mentor_tags = set()
for data in mentors.values():
    tags = data.get("profile", {}).get("specialty", [])
    if isinstance(tags, list):
        all_mentor_tags.update(tags)

# 태그 필터 버튼들을 가로로 나열
cols = st.columns(len(all_mentor_tags) + 1)
with cols[0]:
    if st.button("전체 보기", use_container_width=True):
        st.session_state['selected_tag'] = None
        st.rerun()

i = 1
for tag in sorted(list(all_mentor_tags)):
    with cols[i]:
        if st.button(f"#{tag}", use_container_width=True):
            st.session_state['selected_tag'] = tag
            st.rerun()
    i += 1
st.markdown("---")

# --- ⭐ 3. 선택된 태그에 따라 멘토 목록 필터링 ---
filtered_mentors = {}
selected_tag = st.session_state['selected_tag']

if selected_tag:
    st.subheader(f"#{selected_tag} 분야 멘토")
    for uid, data in mentors.items():
        tags = data.get("profile", {}).get("specialty", [])
        if selected_tag in tags:
            filtered_mentors[uid] = data
else:
    st.subheader("전체 멘토")
    filtered_mentors = mentors

if not filtered_mentors:
    st.warning("아직 해당 분야의 멘토가 없습니다.")
else:
    # --- 멘토 목록 표시 (카드 UI는 이전과 거의 동일) ---
    cols = st.columns(3)
    i = 0
    for mentor_id, data in filtered_mentors.items():
        profile = data.get("profile", {})
        with cols[i % 3]:
            with st.container(border=True, height=400):
                st.subheader(f"{profile.get('name', mentor_id)}")
                st.caption(f"@{mentor_id}")
                
                mentor_reviews = all_reviews.get(mentor_id, [])
                if mentor_reviews:
                    ratings = [r['rating'] for r in mentor_reviews]
                    avg_rating = round(sum(ratings) / len(ratings), 1)
                    stars = "⭐" * int(avg_rating) + "☆" * (5 - int(avg_rating))
                    st.write(f"**평점**: {stars} ({avg_rating})")
                else:
                    st.write("**평점**: 아직 없음")
                
                # --- ⭐ 4. 멘토 카드에 태그 표시 ---
                tags = profile.get("specialty", [])
                if tags:
                    st.write("**전문 분야**: " + " ".join(f"`{t}`" for t in tags))
                
                st.write(profile.get('intro', '자기소개 없음'))
                st.markdown("---")
                
                # (멘토링 신청 버튼 로직은 이전과 동일)
                if current_user_role == "student":
                    sent_requests = all_users.get(current_user_id, {}).get("mentoring_info", {}).get("sent_requests", [])
                    already_requested = any(req['mentor_id'] == mentor_id for req in sent_requests)
                    if already_requested:
                        st.success("✅ 신청 완료")
                    else:
                        if st.button(f"멘토링 신청하기", key=f"req_{mentor_id}"):
                            # ... (신청 로직)
                            st.rerun()
        i += 1
