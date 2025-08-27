import streamlit as st
from streamlit_chat import message
import json
import os

# --- 유틸리티 함수 ---
CHATS_FILE = "chats.json"
USERS_FILE = "users.json"

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
st.title("💬 1:1 채팅")

# --- 로그인 및 채팅 상대방 확인 ---
if "user" not in st.session_state or st.session_state["user"] is None:
    st.warning("채팅 기능을 이용하려면 먼저 로그인해주세요.")
    st.stop()
if "chat_partner" not in st.session_state or st.session_state["chat_partner"] is None:
    st.error("채팅 상대를 찾을 수 없습니다. '마이페이지'에서 다시 시도해주세요.")
    st.stop()

# --- 채팅 참여자 정보 설정 ---
current_user_id = st.session_state["user"]
partner_id = st.session_state["chat_partner"]
all_users = load_data(USERS_FILE)
partner_name = all_users.get(partner_id, {}).get("profile", {}).get("name", partner_id)

st.header(f"'{partner_name}'님과의 대화")

# --- 채팅방 ID 생성 ---
# (ID 순서를 보장하여 항상 동일한 채팅방 ID가 생성되도록 함)
chat_room_id = "_".join(sorted([current_user_id, partner_id]))

# --- 채팅 기록 로드 및 초기화 ---
all_chats = load_data(CHATS_FILE)
if chat_room_id not in all_chats:
    all_chats[chat_room_id] = []

# --- 채팅 화면 UI 구성 ---
chat_history = all_chats[chat_room_id]
for i, chat in enumerate(chat_history):
    is_user = chat["sender"] == current_user_id
    message(chat["message"], is_user=is_user, key=f"chat_{i}")

# --- 메시지 입력 폼 ---
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("메시지:", key="user_input", placeholder="메시지를 입력하세요...")
    submitted = st.form_submit_button("전송")

if submitted and user_input:
    # 1. 새 메시지 객체 생성
    new_message = {"sender": current_user_id, "message": user_input}
    # 2. 채팅 기록에 추가
    all_chats[chat_room_id].append(new_message)
    # 3. 파일에 저장
    save_data(CHATS_FILE, all_chats)
    # 4. 페이지 새로고침하여 즉시 반영
    st.rerun()
