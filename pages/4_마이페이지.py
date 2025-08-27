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
st.title(" dashboards 마이페이지")

if "user" not in st.session_state or st.session_state["user"] is None:
    st.warning("마이페이지를 보려면 먼저 로그인해주세요.")
    st.stop()

current_user_id = st.session_state["user"]
all_users = load_data(USER_FILE)
all_reviews = load_data(REVIEWS_FILE) # 리뷰 데이터 로드
user_data = all_users.get(current_user_id, {})
user_role = user_data.get("role")
mentoring_info = user_data.get("mentoring_info", {})

# =======================================
# 학생 (Student) 화면
# =======================================
if user_role == "student":
    st.header("✉️ 내가 보낸 멘토링 신청")
    sent_requests = mentoring_info.get("sent_requests", [])
    if not sent_requests:
        st.info("아직 보낸 멘토링 신청이 없습니다.")
    else:
        for request in sent_requests:
            mentor_id = request["mentor_id"]
            status = request["status"]
            mentor_name = all_users.get(mentor_id, {}).get("profile", {}).get("name", mentor_id)
            status_emoji = {"pending": "⏳ 대기중", "accepted": "✅ 수락됨", "rejected": "❌ 거절됨"}

            with st.container(border=True):
                st.subheader(f"To. {mentor_name} 멘토")
                st.write(f"신청 상태: **{status_emoji.get(status, status)}**")

                if status == 'accepted':
                    st.success("멘토링이 수락되었습니다!")
                    # 1. 채팅방 입장 버튼
                    if st.button(f"💬 {mentor_name} 멘토와 대화하기", key=f"chat_{mentor_id}"):
                        st.session_state['chat_partner'] = mentor_id
                        st.switch_page("pages/5_채팅.py")

                    # --- 2. 리뷰 작성 폼 추가 ---
                    with st.expander("⭐ 멘토링 리뷰 남기기"):
                        # 이미 이 멘토에게 리뷰를 남겼는지 확인
                        mentor_reviews = all_reviews.get(mentor_id, [])
                        already_reviewed = any(r['student_id'] == current_user_id for r in mentor_reviews)

                        if already_reviewed:
                            st.info("이미 리뷰를 작성했습니다. 감사합니다!")
                        else:
                            with st.form(f"review_form_{mentor_id}"):
                                rating = st.slider("별점", 1, 5, 5)
                                comment = st.text_area("한 줄 평")
                                submitted = st.form_submit_button("리뷰 제출하기")

                                if submitted:
                                    if not comment.strip():
                                        st.error("리뷰 내용을 입력해주세요.")
                                    else:
                                        new_review = {
                                            "student_id": current_user_id,
                                            "rating": rating,
                                            "comment": comment
                                        }
                                        # 멘토 ID를 키로 하여 리뷰 저장
                                        all_reviews.setdefault(mentor_id, []).append(new_review)
                                        save_data(REVIEWS_FILE, all_reviews)
                                        st.success("소중한 리뷰가 등록되었습니다!")
                                        st.rerun()

# =======================================
# 멘토 (Mentor) 화면
# =======================================
elif user_role == "mentor":
    # 멘토 화면은 이전과 동일 (변경 없음)
    st.header("📬 내가 받은 멘토링 신청")
    received_requests = mentoring_info.get("received_requests", [])
    pending_requests = [req for req in received_requests if req['status'] == 'pending']
    accepted_requests = [req for req in received_requests if req['status'] == 'accepted']
    
    if not received_requests:
        st.info("아직 받은 멘토링 신청이 없습니다.")

    if pending_requests:
        st.subheader("대기중인 신청")
        for request in pending_requests:
            student_id = request["student_id"]
            student_name = all_users.get(student_id, {}).get("profile", {}).get("name", student_id)
            with st.container(border=True):
                st.write(f"**From. {student_name} 학생** (@{student_id})")
                col1, col2 = st.columns(2)
                if col1.button("✅ 수락하기", key=f"accept_{student_id}", use_container_width=True):
                    request['status'] = 'accepted'
                    for s_req in all_users.get(student_id, {}).get("mentoring_info", {}).get("sent_requests", []):
                        if s_req['mentor_id'] == current_user_id: s_req['status'] = 'accepted'
                    save_data(USER_FILE, all_users)
                    st.success(f"{student_name} 학생의 멘토링을 수락했습니다.")
                    st.rerun()
                if col2.button("❌ 거절하기", key=f"reject_{student_id}", use_container_width=True):
                    request['status'] = 'rejected'
                    for s_req in all_users.get(student_id, {}).get("mentoring_info", {}).get("sent_requests", []):
                        if s_req['mentor_id'] == current_user_id: s_req['status'] = 'rejected'
                    save_data(USER_FILE, all_users)
                    st.warning(f"{student_name} 학생의 멘토링을 거절했습니다.")
                    st.rerun()

    if accepted_requests:
        st.markdown("---")
        st.subheader("나의 멘티 목록")
        for request in accepted_requests:
            student_id = request["student_id"]
            student_name = all_users.get(student_id, {}).get("profile", {}).get("name", student_id)
            with st.container(border=True):
                st.write(f"**멘티: {student_name}** (@{student_id})")
                if st.button(f"💬 {student_name} 멘티와 대화하기", key=f"chat_{student_id}"):
                    st.session_state['chat_partner'] = student_id
                    st.switch_page("pages/5_채팅.py")
