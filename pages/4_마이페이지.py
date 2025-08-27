# --- 들여쓰기 오류 수정 완료 ---
import streamlit as st
import json
import os

# --- 유틸리티 함수 (이전과 동일) ---
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
st.title(" dashboards 마이페이지")

if "user" not in st.session_state or st.session_state["user"] is None:
    st.warning("마이페이지를 보려면 먼저 로그인해주세요.")
    st.stop()

current_user_id = st.session_state["user"]
all_users = load_data(USER_FILE)
all_reviews = load_data(REVIEWS_FILE)
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
                    if st.button(f"💬 {mentor_name} 멘토와 대화하기", key=f"chat_{mentor_id}"):
                        st.session_state['chat_partner'] = mentor_id
                        st.switch_page("pages/5_채팅.py")

                    with st.expander("⭐ 멘토링 리뷰 남기기"):
                        mentor_reviews = all_reviews.get(mentor_id, [])
                        already_reviewed = any(r['student_id'] == current_user_id for r in mentor_reviews)

                        if already_reviewed:
                            st.info("이미 리뷰를 작성했습니다. 감사합니다!")
                        else:
                            # 1. 별점 선택 UI를 form 바깥으로 이동
                            st.write("**별점을 선택해주세요**")
                            star_rating_key = f"rating_{mentor_id}"
                            if star_rating_key not in st.session_state:
                                st.session_state[star_rating_key] = 5

                            cols = st.columns(5)
                            for i in range(5):
                                with cols[i]:
                                    if st.button("⭐", key=f"star_{mentor_id}_{i+1}", use_container_width=True):
                                        st.session_state[star_rating_key] = i + 1
                            
                            selected_rating = st.session_state[star_rating_key]
                            stars_display = "⭐" * selected_rating + "☆" * (5 - selected_rating)
                            st.write(f"선택: {stars_display} ({selected_rating}점)")

                            # 2. form 안에는 '한 줄 평'과 '제출 버튼'만 남김
                            with st.form(f"review_form_{mentor_id}"):
                                comment = st.text_area("한 줄 평")
                                submitted = st.form_submit_button("리뷰 제출하기")

                                if submitted:
                                    if not comment.strip():
                                        st.error("리뷰 내용을 입력해주세요.")
                                    else:
                                        new_review = {
                                            "student_id": current_user_id,
                                            "rating": selected_rating,
                                            "comment": comment
                                        }
                                        all_reviews.setdefault(mentor_id, []).append(new_review)
                                        save_data(REVIEWS_FILE, all_reviews)
                                        del st.session_state[star_rating_key]
                                        st.success("소중한 리뷰가 등록되었습니다!")
                                        st.rerun()

# =======================================
# 멘토 (Mentor) 화면 (멘토 코드는 생략, 이전 코드와 동일하게 유지하시면 됩니다)
# =======================================
elif user_role == "mentor":
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
