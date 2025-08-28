import streamlit as st
import json
import os

# (load_questions, save_questions 함수는 기존과 동일)
# ...

st.title("💬 Q&A 게시판")

# --- ⭐ 2. 선택된 질문 먼저 보여주기 로직 추가 ⭐ ---
if 'selected_question' in st.session_state:
    selected_q_text = st.session_state['selected_question']
    # 전체 질문 목록에서 선택된 질문 찾기
    selected_q_item = next((q for q in st.session_state["questions"] if q['q'] == selected_q_text), None)
    
    if selected_q_item:
        st.subheader("🔎 마이페이지에서 선택한 질문")
        with st.container(border=True):
            st.markdown(f"**Q. {selected_q_item['q']}**")
            st.caption(f"작성자: {selected_q_item['user']}")
            if selected_q_item.get("a"):
                st.info(f"**A:** {selected_q_item['a']}")
            else:
                st.warning("아직 답변이 등록되지 않았습니다.")
    
    # 확인 후 세션에서 삭제하여 다음 방문 시에는 보이지 않도록 함
    del st.session_state['selected_question']
    st.markdown("---")
# --- 로직 추가 끝 ---


# (이하 질문 등록 폼, 전체 질문 목록 표시 코드는 기존과 동일)
# ...
