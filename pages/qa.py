import streamlit as st

# session_state에 질문/답변 저장할 공간 만들기
if "qa_list" not in st.session_state:
    st.session_state.qa_list = []  # [(질문, 답변)] 형태로 저장

st.title("Q&A 게시판 ✨")

# 입력 폼
with st.form("qa_form", clear_on_submit=True):
    question = st.text_input("질문을 입력하세요")
    answer = st.text_area("답변을 입력하세요")
    submitted = st.form_submit_button("추가하기")

    if submitted:
        if question and answer:
            st.session_state.qa_list.append((question, answer))
            st.success("질문/답변이 추가되었습니다 ✅")
        else:
            st.warning("질문과 답변을 모두 입력해주세요.")

st.divider()

# 저장된 질문/답변 목록 보여주기
st.subheader("📌 질문 목록")
if st.session_state.qa_list:
    for idx, (q, a) in enumerate(st.session_state.qa_list):
        with st.expander(f"Q{idx+1}: {q}"):
            st.write(f"**답변:** {a}")
            # 삭제 버튼
            if st.button("삭제", key=f"delete_{idx}"):
                st.session_state.qa_list.pop(idx)
                st.experimental_rerun()
else:
    st.info("아직 등록된 질문이 없습니다.")
