import streamlit as st
import json
import os

USER_FILE = "users.json"
QUESTIONS_FILE = "questions.json"

def load_data(filepath):
    if not os.path.exists(filepath): return {}
    with open(filepath, "r", encoding="utf-8") as f:
        try: return json.load(f)
        except json.JSONDecodeError: return {}

def save_data(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

st.set_page_config(layout="wide")
st.title("📊 대시보드")

if "user" not in st.session_state or st.session_state["user"] is None:
    st.warning("대시보드를 보려면 먼저 로그인해주세요.")
    st.stop()

current_user_id = st.session_state["user"]
all_users = load_data(USER_FILE)
all_questions = load_data(QUESTIONS_FILE)
user_data = all_users.get(current_user_id, {})
user_role = user_data.get("role")

if user_role == "student":
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.subheader("📬 새 메시지 알림")
            notifications = user_data.get("notifications", {})
            unread_chats = notifications.get("unread_chats", {})
            total_unread = sum(unread_chats.values())
            if total_unread > 0:
                st.metric(label="읽지 않은 총 메시지", value=f"{total_unread}개")
            else:
                st.success("모든 메시지를 확인했습니다!")
    with col2:
        with st.container(border=True):
            st.subheader("📝 최근 활동 (Q&A)")
            my_questions = [q for q in all_questions if q.get("user") == current_user_id]
            if not my_questions:
                st.write("아직 작성한 질문이 없습니다.")
            else:
                st.write("내가 최근에 남긴 질문:")
                for q in my_questions[:3]:
                    st.markdown(f"**Q.** {q['q']} ({'✅ 답변 완료' if q.get('a') else '⏳ 답변 대기중'})")

elif user_role == "mentor":
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.subheader("🔔 새 알림")
            notifications = user_data.get("notifications", {})
            unread_requests_count = notifications.get("unread_requests", 0)
            if unread_requests_count > 0:
                st.metric(label="새로운 멘토링 신청", value=f"{unread_requests_count}건")
            else:
                st.success("새로운 멘토링 신청이 없습니다.")
    with col2:
        with st.container(border=True):
            st.subheader("📬 대기중인 신청")
            if user_data.get("notifications", {}).get("unread_requests", 0) > 0:
                user_data["notifications"]["unread_requests"] = 0
                save_data(USER_FILE, all_users)
                st.rerun()
            
            pending_requests = [req for req in user_data.get("mentoring_info", {}).get("received_requests", []) if req['status'] == 'pending']
            if not pending_requests:
                st.info("처리할 멘토링 신청이 없습니다.")
            for request in pending_requests:
                student_id = request["student_id"]
                student_name = all_users.get(student_id, {}).get("profile", {}).get("name", student_id)
                with st.container(border=True):
                    st.write(f"**From.** {student_name} (@{student_id})")
                    btn_cols = st.columns(2)
                    if btn_cols[0].button("✅ 수락하기", key=f"accept_{student_id}", use_container_width=True):
                        request['status'] = 'accepted'
                        student_requests = all_users.get(student_id, {}).get("mentoring_info", {}).get("sent_requests", [])
                        for s_req in student_requests:
                            if s_req['mentor_id'] == current_user_id:
                                s_req['status'] = 'accepted'
                        save_data(USER_FILE, all_users)
                        st.rerun()
                    if btn_cols[1].button("❌ 거절하기", key=f"reject_{student_id}", use_container_width=True):
                        request['status'] = 'rejected'
                        student_requests = all_users.get(student_id, {}).get("mentoring_info", {}).get("sent_requests", [])
                        for s_req in student_requests:
                            if s_req['mentor_id'] == current_user_id:
                                s_req['status'] = 'rejected'
                        save_data(USER_FILE, all_users)
                        st.rerun()
