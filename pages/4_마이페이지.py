import streamlit as st
import json
import os

# --- 유틸리티 함수 ---
USER_FILE = "users.json"
REVIEWS_FILE = "reviews.json"
QUESTIONS_FILE = "questions.json"

def load_data(filepath):
    if not os.path.exists(filepath): return {}
    with open(filepath, "r", encoding="utf-8") as f:
        try: return json.load(f)
        except json.JSONDecodeError: return {}
# -----------------------

st.set_page_config(layout="wide")
st.title("📊 대시보드")

if "user" not in st.session_state or st.session_state["user"] is None:
    st.warning("대시보드를 보려면 먼저 로그인해주세요.")
    st.stop()

# --- 데이터 로드 ---
current_user_id = st.session_state["user"]
all_users = load_data(USER_FILE)
all_questions = load_data(QUESTIONS_FILE)
user_data = all_users.get(current_user_id, {})
user_role = user_data.get("role")

# --- 대시보드 레이아웃 ---
col1, col2 = st.columns([1, 1])

# --- 왼쪽 컬럼: 알림 및 멘토/멘티 목록 ---
with col1:
    # --- 1. 새 메시지 알림 위젯 ---
    with st.container(border=True):
        st.subheader("📬 새 메시지 알림")
        notifications = user_data.get("notifications", {})
        unread_chats = notifications.get("unread_chats", {})
        
        total_unread = sum(unread_chats.values())
        
        if total_unread > 0:
            st.metric(label="읽지 않은 총 메시지", value=f"{total_unread}개")
            for key, count in unread_chats.items():
                if count > 0:
                    partner_id = key.replace("from_", "")
                    partner_name = all_users.get(partner_id, {}).get("profile", {}).get("name", partner_id)
                    st.info(f"**{partner_name}**님으로부터 **{count}**개의 새 메시지가 있습니다.")
        else:
            st.success("모든 메시지를 확인했습니다! 👍")
    
    st.markdown("---")
    
    # --- 2. 나의 멘토/멘티 목록 위젯 ---
    with st.container(border=True):
        mentoring_info = user_data.get("mentoring_info", {})
        
        if user_role == "student":
            st.subheader("👨‍🏫 나의 멘토")
            my_mentors = [req for req in mentoring_info.get("sent_requests", []) if req['status'] == 'accepted']
            if not my_mentors:
                st.write("아직 매칭된 멘토가 없습니다.")
            for req in my_mentors:
                mentor_id = req["mentor_id"]
                mentor_name = all_users.get(mentor_id, {}).get("profile", {}).get("name", mentor_id)
                if st.button(f"💬 {mentor_name} 멘토와 대화하기", key=f"dash_chat_{mentor_id}", use_container_width=True):
                    st.session_state['chat_partner'] = mentor_id
                    st.switch_page("pages/5_채팅.py")

        elif user_role == "mentor":
            st.subheader("🧑‍🎓 나의 멘티")
            my_mentees = [req for req in mentoring_info.get("received_requests", []) if req['status'] == 'accepted']
            if not my_mentees:
                st.write("아직 매칭된 멘티가 없습니다.")
            for req in my_mentees:
                student_id = req["student_id"]
                student_name = all_users.get(student_id, {}).get("profile", {}).get("name", student_id)
                if st.button(f"💬 {student_name} 멘티와 대화하기", key=f"dash_chat_{student_id}", use_container_width=True):
                    st.session_state['chat_partner'] = student_id
                    st.switch_page("pages/5_채팅.py")

# --- 오른쪽 컬럼: 최근 활동 ---
with col2:
    # --- 3. 최근 활동 위젯 ---
    with st.container(border=True):
        st.subheader("📝 최근 활동 (Q&A)")
        my_questions = [q for q in all_questions if q.get("user") == current_user_id]
        
        if not my_questions:
            st.write("아직 작성한 질문이 없습니다.")
        else:
            st.write("내가 최근에 남긴 질문:")
            # 최근 3개의 질문만 표시
            for q in my_questions[:3]:
                with st.container(border=True):
                    st.markdown(f"**Q. {q['q']}**")
                    if q.get('a'):
                        st.success("✅ 답변 완료")
                    else:
                        st.warning("⏳ 답변 대기중")
