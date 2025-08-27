import streamlit as st
import json, os

# 질문 저장 파일
QUESTION_FILE = "questions.json"
if not os.path.exists(QUESTION_FILE):
    with open(QUESTION_FILE, "w") as f:
        json.dump([], f)

# 질문 불러오기
def load_questions():
    with open(QUESTION_FILE, "r") as f:
        return json.load(f)

# 질문 저장하기
def save_questions(questions):
    with open(QUESTION_FILE, "w") as f:
        json.dump(questions, f)

st.title("📝 질문하기")

# 로그인 체크
if "user" not in st.session_state or st.session_state.user is None:
    st.error("로그인 후 이용 가능합니다. 메인 페이지에서 로그인 해주세요.")
    st.stop()

username = st.session_state.user

questions = load_questions()

q = st.text_area("궁금한 점을 입력하세요")
if st.button("질문 등록"):
    if q.strip():
        questions.append({"user": username, "q": q, "a": None})
        save_questions(questions)
        st.success("질문이 등록되었습니다!")
    else:
        st.warning("질문 내용을 입력해주세요.")

# 내 질문 목록 표시
st.subheader("내 질문 목록")
my_questions = [x for x in questions if x["user"] == username]

if my_questions:
    for i, q in enumerate(my_questions, 1):
        st.write(f"Q{i}: {q['q']}")
        if q["a"]:
            st.write(f"👉 답변: {q['a']}")
        else:
            st.write("⏳ 아직 답변 없음")
else:
    st.info("아직 등록한 질문이 없습니다.")
