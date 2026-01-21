import streamlit as st
import csv

def load_csv_from_drive():
    with open("train.csv", "r", encoding="utf-8") as f:
        return f.readlines()

def choose_number():
    st.title("MCQ Quiz (Medical)")

    subject_list = ["Any", "Medical"]
    st.session_state.category_out = st.selectbox("Select Subject", subject_list)

    st.session_state.num_questions = st.number_input(
        "Number of MCQs",
        min_value=1,
        max_value=100,
        value=10
    )

    if st.button("Start Quiz"):
        lines = load_csv_from_drive()

        # ===== FIX 1 (ONLY THIS BLOCK CHANGED) =====
        reader = csv.reader(lines)
        next(reader)
        rows = [row for row in reader if len(row) >= 10]

        if st.session_state.category_out != "Any":
            st.session_state.my_list = [
                row for row in rows
                if row[9].strip().lower() == st.session_state.category_out.lower()
            ]
        else:
            st.session_state.my_list = rows
        # ==========================================

        st.session_state.current_index = 0
        st.session_state.correct = 0
        st.session_state.wrong = 0
        st.session_state.skipped = 0
        st.session_state.quiz_started = True
        st.rerun()

def quiz_time():
    if st.session_state.current_index >= len(st.session_state.my_list):
        st.title("🎉 Quiz Finished!")
        total = st.session_state.correct + st.session_state.wrong + st.session_state.skipped
        st.write(
            f"✅ Correct: {st.session_state.correct} "
            f"❌ Wrong: {st.session_state.wrong} "
            f"⚠️ Skipped: {st.session_state.skipped} "
            f"🏁 Total Score: {st.session_state.correct}/{total}"
        )
        return

    # ===== FIX 2 (ONLY THIS LINE CHANGED) =====
    row = st.session_state.my_list[st.session_state.current_index]
    # ========================================

    question = row[0]
    options = row[1:5]
    correct_answer = row[5]

    st.subheader(f"Q{st.session_state.current_index + 1}: {question}")

    choice = st.radio("Choose one:", options, key=st.session_state.current_index)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Submit"):
            if choice == correct_answer:
                st.session_state.correct += 1
            else:
                st.session_state.wrong += 1
            st.session_state.current_index += 1
            st.rerun()

    with col2:
        if st.button("Skip"):
            st.session_state.skipped += 1
            st.session_state.current_index += 1
            st.rerun()

if "quiz_started" not in st.session_state:
    st.session_state.quiz_started = False

if not st.session_state.quiz_started:
    choose_number()
else:
    quiz_time()
