import streamlit as st
import json
import os

# --- 유틸리티 함수 ---
USER_FILE = "users.json"

def load_users():
    if not os.path.exists(USER_FILE): return {}
    with open(USER_FILE, "r", encoding="utf-8") as f:
        try: return json.load(f)
        except json.JSONDecodeError: return {}

def save_users(users):
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

# -----------------------

st.set_page_config(layout="wide")
st.title(" dashboards 마이페이지")

# --- 로그인 확인 ---
if "user" not in st.session_state or st.session_state["user"] is None:
    st.warning("마이페이지를 보려면 먼저 로그인해주세요.")
    st.stop()

# --- 현재 사용자 정보 로드 ---
current_user_id = st.session_state["user"]
all_users = load_users()
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
        st.info("아직 보낸 멘토링 신청이 없습니다. '멘토찾기'에서 신청해보세요!")
    else:
        for request in sent_requests:
            mentor_id = request["mentor_id"]
            status = request["status"]
            mentor_profile = all_users.get(mentor_id, {}).get("profile", {})
            mentor_name = mentor_profile.get("name", mentor_id)
            
            status_emoji = {"pending": "⏳ 대기중", "accepted": "✅ 수락됨", "rejected": "❌ 거절됨"}

            with st.container(border=True):
                st.subheader(f"To. {mentor_name} 멘토")
                st.write(f"신청 상태: **{status_emoji.get(status, status)}**")
                if status == 'accepted':
                    st.success("멘토링이 수락되었습니다! 멘토와 자유롭게 소통해보세요.")


# =======================================
# 멘토 (Mentor) 화면
# =======================================
elif user_role == "mentor":
    st.header("📬 내가 받은 멘토링 신청")
    received_requests = mentoring_info.get("received_requests", [])
    
    # 상태가 'pending'인 요청만 먼저 보여주기
    pending_requests = [req for req in received_requests if req['status'] == 'pending']
    other_requests = [req for req in received_requests if req['status'] != 'pending']

    if not pending_requests:
        st.info("아직 처리할 멘토링 신청이 없습니다.")
    else:
        st.subheader("대기중인 신청")
        for request in pending_requests:
            student_id = request["student_id"]
            student_profile = all_users.get(student_id, {}).get("profile", {})
            student_name = student_profile.get("name", student_id)
            
            with st.container(border=True):
                st.write(f"**From. {student_name} 학생** (@{student_id})")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ 수락하기", key=f"accept_{student_id}", use_container_width=True):
                        # 1. 멘토의 요청 상태 변경
                        request['status'] = 'accepted'
                        # 2. 학생의 요청 상태도 변경
                        student_data = all_users.get(student_id, {})
                        for s_req in student_data.get("mentoring_info", {}).get("sent_requests", []):
                            if s_req['mentor_id'] == current_user_id:
                                s_req['status'] = 'accepted'
                        # 3. 저장 및 새로고침
                        save_users(all_users)
                        st.success(f"{student_name} 학생의 멘토링을 수락했습니다.")
                        st.rerun()

                with col2:
                    if st.button("❌ 거절하기", key=f"reject_{student_id}", use_container_width=True):
                        request['status'] = 'rejected'
                        student_data = all_users.get(student_id, {})
                        for s_req in student_data.get("mentoring_info", {}).get("sent_requests", []):
                            if s_req['mentor_id'] == current_user_id:
                                s_req['status'] = 'rejected'
                        save_users(all_users)
                        st.warning(f"{student_name} 학생의 멘토링을 거절했습니다.")
                        st.rerun()

    # 처리 완료된 요청들 (수락/거절)
    if other_requests:
        st.markdown("---")
        st.subheader("처리 완료된 신청")
        for request in other_requests:
            student_id = request["student_id"]
            student_name = all_users.get(student_id, {}).get("profile", {}).get("name", student_id)
            status_text = "수락함" if request['status'] == 'accepted' else "거절함"
            st.write(f"- **{student_name}** 학생: {status_text}")
