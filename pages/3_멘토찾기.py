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

if 'selected_tag' not in st.session_state:
    st.session_state['selected_tag'] = None

st.title("👨‍🏫 멘토 찾기")

# --- ⭐ 1. 현재 로그인 상태 진단 메시지 ---
st.info(f"진단 정보: 현재 로그인 역할 = {st.session_state.get('role')}")

all_users = load_data(USER_FILE)
all_reviews = load_data(REVIEWS_FILE)
mentors = {uid: data for uid, data in all_users.items() if data.get("role") == "mentor"}
is_logged_in = "user" in st.session_state and st.session_state["user"] is not None
current_user_id = st.session_state["user"] if is_logged_in else None
current_user_role = st.session_state.get("role") if is_logged_in else None

# --- 태그 필터링 UI (기존과 동일) ---
all_mentor_tags = set()
for data in mentors.values():
    tags = data.get("profile", {}).get("specialty", [])
    if isinstance(tags, list):
        all_mentor_tags.update(tags)

if all_mentor_tags: # 태그가 있을 때만 버튼들을 보여줌
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

# --- 멘토 목록 필터링 (기존과 동일) ---
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
    cols = st.columns(3)
    i = 0
    for mentor_id, data in filtered_mentors.items():
        profile = data.get("profile", {})
        with cols[i % 3]:
            with st.container(border=True, height=420): # 카드 높이 살짝 조정
                st.subheader(f"{profile.get('name', mentor_id)}")
                st.caption(f"@{mentor_id}")

                # (평점 및 태그 표시 로직은 기존과 동일)
                mentor_reviews = all_reviews.get(mentor_id, [])
                if mentor_reviews:
                    ratings = [r['rating'] for r in mentor_reviews]
                    avg_rating = round(sum(ratings) / len(ratings), 1)
                    stars = "⭐" * int(avg_rating) + "☆" * (5 - int(avg_rating))
                    st.write(f"**평점**: {stars} ({avg_rating})")
                else:
                    st.write("**평점**: 아직 없음")
                tags = profile.get("specialty", [])
                if tags:
                    st.write("**전문 분야**: " + " ".join(f"`{t}`" for t in tags))
                st.write(profile.get('intro', '자기소개 없음'))
                st.markdown("---")

                # --- ⭐ 2. 멘토링 신청 버튼 로직 수정 ---
                if current_user_role == "student":
                    student_info = all_users.get(current_user_id, {})
                    sent_requests = student_info.get("mentoring_info", {}).get("sent_requests", [])
                    already_requested = any(req['mentor_id'] == mentor_id for req in sent_requests)
                    
                    if already_requested:
                        st.success("✅ 신청 완료")
                    else:
                        if st.button(f"멘토링 신청하기", key=f"req_{mentor_id}"):
                            # 버튼 클릭 시 즉시 사용자에게 피드백을 줍니다.
                            st.warning("...신청 처리 중...")

                            # 최신 사용자 정보를 다시 불러와서 안전하게 처리합니다.
                            users_db = load_data(USER_FILE)
                            
                            # 학생 정보에 신청 기록 추가
                            student_data = users_db.get(current_user_id, {})
                            student_data.setdefault("mentoring_info", {}).setdefault("sent_requests", []).append(
                                {"mentor_id": mentor_id, "status": "pending"}
                            )
                            
                            # 멘토 정보에 받은 신청 기록 추가
                            mentor_data = users_db.get(mentor_id, {})
                            mentor_data.setdefault("mentoring_info", {}).setdefault("received_requests", []).append(
                                {"student_id": current_user_id, "status": "pending"}
                            )
                            
                            # 파일에 최종적으로 저장
                            save_data(USER_FILE, users_db)
                            
                            # 성공 메시지를 보여주고 페이지를 새로고침
                            st.success("멘토링 신청을 보냈습니다! '마이페이지'에서 확인하세요.")
                            st.rerun()
        i += 1
