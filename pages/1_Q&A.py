import streamlit as st
from streamlit_autorefresh import st_autorefresh
import json, os

# 질문 저장 파일 이름
FILE_NAME = "questions.json"

# 질문 불러오기
def get_questions():
    if not os.path.exists(FILE_NAME):
        return []
    try:
        with open(FILE_NAME, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except:
        return []

# 질문 저장하기
def set_questions(q_list):
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        json.dump(q_list, f, ensure_ascii=False, indent=4)

# 세션에 질문 리스트 올리기
if "questions" not in st.session_state:
    st.session_state["questions"] = get_questions()

# 자동 새로고침 (3초마다)
st_autorefresh(interval=3000, key="refresh")

st.title("💬 Q&A 게시판")
st.caption("3초마다 새로고침돼요.")

# 마이페이지에서 선택된 질문
if "selected_question" in st.session_state:
    picked_q = st.session_state.pop("selected_question")
    item = next((q for q in st.session_state["questions"] if q["q"] == picked_q), None)
    if item:
        st.subheader("🔎 선택한 질문")
        with st.container(border=True):
            st.markdown(f"**Q. {item['q']}**")
            st.caption(f"작성자: {item['user']}")
            if item.get("a"):
                st.info(f"**A:** {item['a']}")
            else:
                st.warning("아직 답변이 안 달렸습니다.")
        st.divider()

# 로그인 안 했을 경우
if not st.session_state.get("user"):
    st.warning("👉 로그인 먼저 해주세요.")
else:
    # 학생일 때 질문하기
    if st.session_state.get("role") == "student":
        st.subheader("✍️ 질문 등록")
        with st.form("q_form", clear_on_submit=True):
            new_q = st.text_area("궁금한 점을 적어주세요.")
            if st.form_submit_button("등록"):
                if new_q.strip():
                    st.session_state["questions"].insert(
                        0, {"user": st.session_state["user"], "q": new_q, "a": None}
                    )
                    set_questions(st.session_state["questions"])
                    st.success("질문이 올라갔습니다!")
                    st.rerun()
                else:
                    st.error("내용을 입력하세요.")
    st.divider()

    # 질문 목록
    st.subheader("📖 질문 모음")
    if not st.session_state["questions"]:
        st.info("아직 질문이 없어요. 첫 질문을 남겨보세요!")
    else:
        for i, q in enumerate(st.session_state["questions"]):
            with st.container(border=True):
                st.markdown(f"**Q. {q['q']}**")
                st.caption(f"작성자: {q['user']}")
                
                if q.get("a"):
                    st.info(f"**A:** {q['a']}")
                else:
                    if st.session_state.get("role") == "mentor":
                        ans = st.text_area("답변 입력", key=f"ans_{i}")
                        if st.button("등록", key=f"ans_btn_{i}"):
                            if ans.strip():
                                st.session_state["questions"][i]["a"] = ans
                                set_questions(st.session_state["questions"])
                                st.success("답변 완료!")
                                st.rerun()
                    else:
                        st.write("멘토 답변 대기 중...")

                # 본인 질문이거나 멘토라면 삭제 가능
                if st.session_state.get("user") == q["user"] or st.session_state.get("role") == "mentor":
                    if st.button("삭제", key=f"del_{i}", type="secondary"):
                        st.session_state["questions"].pop(i)
                        set_questions(st.session_state["questions"])
                        st.warning("삭제되었습니다.")
                        st.rerun()
