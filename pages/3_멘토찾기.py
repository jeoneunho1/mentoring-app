import streamlit as st
import json
import os

# --- 유틸리티 함수 ---
USER_FILE = "users.json"
REVIEWS_FILE = "reviews.json" # 리뷰 파일 경로 추가

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
st.title("👨‍🏫 멘토 찾기")
st.info("나에게 필요한 조언을 해줄 수 있는 멘토를 찾아보세요!")

# --- 데이터 로드 ---
all_users = load_data(USER_FILE)
all_reviews = load_data(REVIEWS_FILE) # 리뷰 데이터 로드
mentors = {uid: data for uid, data in all_users.items() if data.get("role") == "mentor"}

# --- 현재 사용자 정보 ---
is_logged_in = "user" in st.session_state and st.session_state["user"] is not None
current_user_id = st.session_state["user"] if is_logged_in else None
current_user_role = st.session_state.get("role") if is_logged_in else None

# --- 검색창 ---
search_term = st.text_input("🔍 전문 분야로 멘토 검색하기", placeholder="예: 파이썬, AI")
st.markdown("---")

if not mentors:
    st.warning("아직 등록된 멘토가 없습니다.")
else:
    # --- 검색 로직 ---
    filtered_mentors = {}
    if search_term:
        for uid, data in mentors.items():
            specialty = data.get("profile", {}).get("specialty", "").lower()
            if search_term.lower() in specialty:
                filtered_mentors[uid] = data
    else:
        filtered_mentors = mentors

    if not filtered_mentors:
        st.info(f"'{search_term}' 분야의 멘토를 찾을 수 없습니다.")
    else:
        # --- 멘토 목록 표시 ---
        cols = st.columns(3)
        i = 0
        for mentor_id, data in filtered_mentors.items():
            profile = data.get("profile", {})
            with cols[i % 3]:
                with st.container(border=True, height=400): # 카드 높이 늘림
                    st.subheader(f"{profile.get('name', mentor_id)}")
                    st.caption(f"@{mentor_id}")

                    # --- 평점 계산 및 표시 로직 ---
                    mentor_reviews = all_reviews.get(mentor_id, [])
                    if mentor_reviews:
                        # 모든 리뷰의 rating 값을 가져와 리스트 생성
                        ratings = [r['rating'] for r in mentor_reviews]
                        # 평균 평점 계산 (소수점 첫째 자리까지)
                        avg_rating = round(sum(ratings) / len(ratings), 1)
                        # 별 모양으로 평점 시각화
                        stars = "⭐" * int(avg_rating) + "☆" * (5 - int(avg_rating))
                        st.write(f"**평점**: {stars} ({avg_rating} / 5.0)")
                    else:
                        st.write("**평점**: 아직 없음")

                    st.markdown(f"**전문 분야**: {profile.get('specialty', '정보 없음')}")
                    st.write(profile.get('intro', '자기소개 없음'))

                    # --- 최근 리뷰 1개 표시 ---
                    if mentor_reviews:
                        with st.expander("최근 리뷰 보기"):
                            latest_review = mentor_reviews[-1] # 가장 마지막 리뷰
                            reviewer_name = all_users.get(latest_review['student_id'], {}).get('profile', {}).get('name', latest_review['student_id'])
                            st.info(f'"{latest_review["comment"]}" - {reviewer_name}님')

                    st.markdown("---")

                    # --- 멘토링 신청 버튼 (이전과 동일) ---
                    if current_user_role == "student":
                        sent_requests = all_users.get(current_user_id, {}).get("mentoring_info", {}).get("sent_requests", [])
                        already_requested = any(req['mentor_id'] == mentor_id for req in sent_requests)
                        if already_requested:
                            st.success("✅ 신청 완료")
                        else:
                            if st.button(f"멘토링 신청하기", key=f"req_{mentor_id}"):
                                all_users.setdefault(current_user_id, {}).setdefault("mentoring_info", {}).setdefault("sent_requests", []).append({"mentor_id": mentor_id, "status": "pending"})
                                all_users.setdefault(mentor_id, {}).setdefault("mentoring_info", {}).setdefault("received_requests", []).append({"student_id": current_user_id, "status": "pending"})
                                save_data(USER_FILE, all_users)
                                st.success("멘토링 신청을 보냈습니다!")
                                st.rerun()
            i += 1
