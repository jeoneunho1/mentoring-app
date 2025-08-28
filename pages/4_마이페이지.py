import streamlit as st
import json
import os

# --- 유틸리티 함수 (기존과 동일) ---
USER_FILE = "users.json"
REVIEWS_FILE = "reviews.json"
QUESTIONS_FILE = "questions.json"

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
st.title("📊 대시보드")

if "user" not in st.session_state or st.session_state["user"] is None:
    st.warning("대시보드를 보려면 먼저 로그인해주세요.")
    st.stop()

current_user_id = st.session_state["user"]
all_users = load_data(USER_FILE)
all_questions = load_data(QUESTIONS_FILE)
user_data = all_users.get(current_user_id, {})
user_role = user_data.get("role")
mentoring_info = user_data.get("mentoring_info", {})

# =======================================
# 학생 (Student) 화면
# =======================================
if user_role == "student":
    col1, col2 = st.columns(2)
    with col1:
        # (기존 알림 및 멘토 목록 코드)
        with st.container(border=True):
            st.subheader("👨‍🏫 나의 멘토")
            # ... (이하 동일)

    with col2:
        with st.container(border=True):
            st.subheader("📝 최근 활동 (Q&A)")
            my_questions = [q for q in all_questions if q.get("user") == current_user_id]
            if not my_questions:
                st.write("아직 작성한 질문이 없습니다.")
            else:
                st.write("내가 최근에 남긴 질문:")
                for q in my_questions[:3]:
                    status_text = "✅ 답변 완료" if q.get('a') else "⏳ 답변 대기중"
                    
                    # --- ⭐ 1. st.markdown을 st.button으로 변경 ⭐ ---
                    button_label = f"Q. {q['q'][:30]}... ({status_text})" # 질문이 길 경우 잘라냄
                    if st.button(button_label, key=f"q_btn_{q['q']}", use_container_width=True):
                        # 선택한 질문 내용을 세션에 저장하고 Q&A 페이지로 이동
                        st.session_state['selected_question'] = q['q']
                        st.switch_page("pages/1_Q&A.py")

# =======================================
# 멘토 (Mentor) 화면 (기존과 동일)
# =======================================
elif user_role == "mentor":
    # (멘토 대시보드 코드는 변경 없음)
