import streamlit as st
import csv
import random
import requests
import io

@st.cache_data
def load_csv_from_drive():
    url = "https://drive.google.com/uc?id=1AsnDikQZdkbn1O03pk6BBRRMGHP0U73S"
    response = requests.get(url)
    response.raise_for_status()
    return response.text.splitlines()


# variable to store or hold date 
# Data will come thorugh different loops here to store it and use it for later maybe in results

if not all(k in st.session_state for k in ["stage","category_out","my_list","number_of_mcqs","current_index","correct","wrong","wrong_input","locked"]):
    st.session_state.stage = st.session_state.get("stage","choose_subject")
    st.session_state.category_out = st.session_state.get("category_out","")
    st.session_state.my_list = st.session_state.get("my_list",[])
    st.session_state.number_of_mcqs = st.session_state.get("number_of_mcqs",0)
    st.session_state.current_index = st.session_state.get("current_index",0)
    st.session_state.correct = st.session_state.get("correct",0)
    st.session_state.wrong = st.session_state.get("wrong",0)
    st.session_state.wrong_input = st.session_state.get("wrong_input",0)
    st.session_state.locked = st.session_state.get("locked",False)

# All available subjects are listed here. These are those that we have currently
#---------------------------

list_of_subjects = [
    "anaesthesia", "anatomy", "biochemistry", "dental", "ent",
    "forensic medicine", "gynaecology & obstetrics", "medicine",
    "microbiology", "ophthalmology", "orthopaedics", "pathology",
    "pediatrics", "pharmacology", "physiology", "psychiatry",
    "radiology", "skin", "social & preventive medicine", "surgery",
    "unknown"
]

st.title("MCQ Quiz (Medical)")

# This is the filter option. It doesnt have mcqs number as its a permanat thing so even if user
# selects no for filter it will still be needed to be filled

if st.session_state.stage == "choose_subject":
    filter_option = st.radio("Would you like to choose a subject first?", ["Yes", "No"])
    if filter_option == "Yes":
        subject = st.text_input("Enter subject name: (Even short form like anaes or thesia -----> Anaesthesia)")
        if st.button("Apply"):
            matched = None
            for s in list_of_subjects:
                if subject and subject.lower() in s.lower():
                    matched = s
                    break
            if matched:
                st.session_state.category_out = matched
                st.session_state.stage = "choose_number"
                st.rerun()
            else:
                st.warning("We don't have this subject. Available ones are: " + ", ".join(list_of_subjects))
    else:
        if st.button("Continue without choosing subject"):
            st.session_state.stage = "choose_number"
            st.rerun()
# this is permanat to chose number of mcqs to start forward
# ---------------- -------------------- -------------------

elif st.session_state.stage == "choose_number":
    num = st.number_input("How many questions would you like to attempt?", 1, 50, 5)
    if st.button("Start Quiz"):
        st.session_state.number_of_mcqs = num

        lines = load_csv_from_drive()
        reader = csv.reader(lines)
        next(reader)
        rows = [row for row in reader if len(row) >= 10]

        if st.session_state.category_out:
            st.session_state.my_list = [
                row for row in rows
                if row[9].strip().lower() == st.session_state.category_out.lower()
            ]
        else:
            st.session_state.my_list = rows

        random.shuffle(st.session_state.my_list)
        st.session_state.stage = "quiz_time"
        st.rerun()

elif st.session_state.stage == "quiz_time":
    if (
        st.session_state.current_index >= st.session_state.number_of_mcqs
        or st.session_state.current_index >= len(st.session_state.my_list)
    ):
        st.session_state.stage = "show_result"
        st.rerun()

    row = st.session_state.my_list[st.session_state.current_index]

    while len(row) < 10:
        row.append('Sorry! Right now we have not added explanation.')

    id, question, op1, op2, op3, op4, answer, type_, exp, category = row

    st.subheader(f"Q{st.session_state.current_index+1}: {question}")

    options = {"A": op1, "B": op2, "C": op3, "D": op4}

    correct_letter = answer.strip().upper() if answer else ""
    if correct_letter in ["0", "1", "2", "3"]:
        correct_letter = chr(int(correct_letter) + 65)

    choice = st.radio(
        "Pick your answer:",
        list(options.keys()),
        format_func=lambda x: f"{x}. {options[x]}",
        index=None,
        disabled=st.session_state.locked,
    )

    if not st.session_state.locked and st.button("Submit Answer"):
        if choice:
            if choice.upper() == correct_letter:
                st.success("✅ Correct!\n\n" + exp)
                st.session_state.correct += 1
            else:
                st.error(f"❌ Wrong! The correct answer was {correct_letter}. \n\n{exp}")
                st.session_state.wrong += 1
        else:
            st.warning("⚠️ You didn’t select anything!")
            st.session_state.wrong_input += 1

        st.session_state.locked = True

    if st.session_state.locked and st.button("Next Question ➡️"):
        st.session_state.current_index += 1
        st.session_state.locked = False
        st.rerun()

elif st.session_state.stage == "show_result":
    total = st.session_state.correct + st.session_state.wrong + st.session_state.wrong_input
    st.success(
        f"🎉 Quiz Finished!\n\n"
        f"✅ Correct: {st.session_state.correct}\n"
        f"❌ Wrong: {st.session_state.wrong}\n"
        f"⚠️ Skipped: {st.session_state.wrong_input}\n"
        f"🏁 Total Score: {st.session_state.correct}/{total}"
    )
# this is the restart part to return back

    if st.button("🔄 Restart Quiz"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.session_state.stage = "choose_subject"
        st.rerun()

# this is where it end but other features + some fixes and bugs are being resolved and will be done soon
