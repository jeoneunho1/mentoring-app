# --- 자동 새로고침 기능이 추가된 최종 코드 ---
import streamlit as st
from streamlit_chat import message
from streamlit_autorefresh import st_autorefresh # --- ⭐ 1. 이 줄 추가 ⭐ ---
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

# --- ⭐ 2. 이 줄 추가 ⭐ ---
st_autorefresh(interval=2000, limit=None, key="chat_autorefresh")

st.title("💬 1:1 채팅")
st.caption("이 페이지는 2초마다 자동으로 업데이트됩니다.")

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

chat_room_id = "_".join(sorted([current_user_id, partner_id]))
all_chats = load_data(CHATS_FILE)
if chat_room_id not in all_chats:
    all_chats[chat_room_id] = []

# --- 채팅방 입장 시 '안 읽은 메시지' 초기화 ---
current_user_notifications = all_users.setdefault(current_user_id, {}).setdefault("notifications", {})
unread_chats = current_user_notifications.setdefault("unread_chats", {})
unread_chats[f"from_{partner_id}"] = 0
save_data(USERS_FILE, all_users)

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
    new_message = {"sender": current_user_id, "message": user_input}
    all_chats[chat_room_id].append(new_message)
    save_data(CHATS_FILE, all_chats)
    
    # --- 메시지 전송 시 상대방의 '안 읽은 메시지' 카운트 증가 ---
    partner_notifications = all_users.setdefault(partner_id, {}).setdefault("notifications", {})
    partner_unread_chats = partner_notifications.setdefault("unread_chats", {})
    
    count_key = f"from_{current_user_id}"
    partner_unread_chats[count_key] = partner_unread_chats.get(count_key, 0) + 1
    save_data(USERS_FILE, all_users)

    st.rerun()
