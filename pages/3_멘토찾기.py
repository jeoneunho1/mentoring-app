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
st.title("👨‍🏫 멘토 찾기")
st.info("나에게 필요한 조언을 해줄 수 있는 멘토를 찾아보세요!")

# --- 로그인 상태 확인 ---
is_logged_in = "user" in st.session_state and st.session_state["user"] is not None
if is_logged_in:
    current_user_id = st.session_state["user"]
    current_user_role = st.session_state.get("role")
else:
    current_user_id = None
    current_user_role = None

# --- 데이터 로드 및 멘토 필터링 ---
all_users = load_users()
mentors = {uid: data for uid, data in all_users.items() if data.get("role") == "mentor"}

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
                with st.container(border=True, height=300): # 높이 살짝 늘림
                    st.subheader(f"{profile.get('name', mentor_id)}")
                    st.caption(f"@{mentor_id}")
                    st.markdown(f"**전문 분야**: {profile.get('specialty', '정보 없음')}")
                    st.write(profile.get('intro', '자기소개 없음'))
                    st.markdown("---") # 구분선 추가

                    # --- 멘토링 신청 버튼 로직 ---
                    if current_user_role == "student":
                        student_info = all_users.get(current_user_id, {})
                        sent_requests = student_info.get("mentoring_info", {}).get("sent_requests", [])
                        
                        # 이미 신청했는지 확인
                        already_requested = any(req['mentor_id'] == mentor_id for req in sent_requests)

                        if already_requested:
                            st.success("✅ 신청 완료")
                        else:
                            if st.button(f"멘토링 신청하기", key=f"req_{mentor_id}"):
                                # 1. 학생의 sent_requests에 추가
                                student_info.setdefault("mentoring_info", {}).setdefault("sent_requests", []).append(
                                    {"mentor_id": mentor_id, "status": "pending"}
                                )
                                # 2. 멘토의 received_requests에 추가
                                mentor_info = all_users.get(mentor_id, {})
                                mentor_info.setdefault("mentoring_info", {}).setdefault("received_requests", []).append(
                                    {"student_id": current_user_id, "status": "pending"}
                                )
                                # 3. 변경사항 저장
                                save_users(all_users)
                                st.success("멘토링 신청을 보냈습니다! '마이페이지'에서 확인하세요.")
                                st.rerun()
            i += 1
