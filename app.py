import os
import sqlite3
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

# Set Streamlit to wide mode
st.set_page_config(layout="wide")

# Set the Google API key as an environment variable
os.environ['GOOGLE_API_KEY'] = 'AIzaSyDvlM0509T-QnYFyckAj9pQsIOTxk-kwaQ'

with open("style.css") as css:
    st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

# Initialize the model with the desired version
model = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest")  # or gemini-1.5-flash

# Initialize SQLite database connection
conn = sqlite3.connect('questions.db')
c = conn.cursor()

# Create the table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS questions
             (id INTEGER PRIMARY KEY AUTOINCREMENT, tag TEXT, question TEXT, answer TEXT, logic TEXT)''')
conn.commit()

# Function to add a question to the database
def add_question(tag, question, answer, logic):
    c.execute("INSERT INTO questions (tag, question, answer, logic) VALUES (?, ?, ?, ?)",
              (tag, question, answer, logic))
    conn.commit()

# Function to fetch all unique tags
def get_all_tags():
    c.execute("SELECT DISTINCT tag FROM questions")
    return [row[0] for row in c.fetchall()]

# Function to fetch questions by tag
def get_questions_by_tag(tag):
    c.execute("SELECT * FROM questions WHERE tag=?", (tag,))
    return c.fetchall()

# Function to update a question in the database
def update_question(id, tag, question, answer, logic):
    c.execute("UPDATE questions SET tag=?, question=?, answer=?, logic=? WHERE id=?",
              (tag, question, answer, logic, id))
    conn.commit()

# Function to generate practice questions using the model
def generate_practice_questions(prompt):
    message = HumanMessage(content=prompt)
    response = model.stream([message])
    return ''.join([r.content for r in response])

# Fetch all unique tags
tags = get_all_tags()
tags_info = ", ".join(tags) if tags else "No tags available"

st.header("SparkAPT - Developed by Sparkience AI Lab")

# Display available tags
st.info(f"Available Tags: {tags_info}")

# Sidebar for navigation
option = st.sidebar.selectbox(
    "Choose an option",
    ["Library", "Generate Practice Questions","Add Question", "View/Edit Questions"]
)

# Define the passkey
passkey = "godsparky1237"

# Add Question and View/Edit Questions sections
if option in ["Add Question", "View/Edit Questions"]:
    password = st.text_input("Enter passkey", type="password")
    if password == passkey:
        if option == "Add Question":
            st.header("Add a New Question")
            tag = st.text_input("Tag")
            question = st.text_area("Question")
            answer = st.text_input("Answer")
            logic = st.text_area("Logic")

            if st.button("Add"):
                if tag and question and answer and logic:
                    add_question(tag, question, answer, logic)
                    st.success("Question added successfully!")
                else:
                    st.error("Please fill out all fields.")

        elif option == "View/Edit Questions":
            st.header("View and Edit Questions")
            tag = st.text_input("Enter tag to filter questions")
            questions = get_questions_by_tag(tag)
            if questions:
                for q in questions:
                    id, q_tag, q_question, q_answer, q_logic = q
                    st.write(f"**ID:** {id}")


                    #new_tag = st.text_input(f"Tag (ID {id})", q_tag)
                    new_question = st.text_input(f"Question (ID {id})", q_question)
                    
                    # Using st.expander to show Answer and Logic
                    with st.expander(f"Answer and Logic (ID {id})"):
                        new_answer = st.text_input(f"Answer (ID {id})", q_answer)
                        new_logic = st.text_area(f"Logic (ID {id})", q_logic)

                    if st.button(f"Update (ID {id})"):


                        #if new_tag and new_question and new_answer and new_logic:
                        if new_question and new_answer and new_logic:
                            #update_question(id, new_tag, new_question, new_answer, new_logic)

                            update_question(id, q_tag, new_question, new_answer, new_logic)
                            st.success(f"Question ID {id} updated successfully!")
                        else:
                            st.error("Please fill out all fields.")
            else:
                st.error("No questions found for this tag.")
    else:
        if password != "":
            st.error("Incorrect passkey. You do not have access to add or edit questions.")


elif option == "Generate Practice Questions":
    st.header("Generate Practice Questions")
    tag = st.text_input("Enter tag to generate practice questions")
    questions = get_questions_by_tag(tag)
    if questions:
        practice_questions = []
        for q in questions:
            id, q_tag, q_question, q_answer, q_logic = q
            prompt = f"Generate a similar logial-thinking aptitude question to: {q_question}"
            generated_question = generate_practice_questions(prompt)
            practice_questions.append(generated_question)
        
        for pq in practice_questions:
            st.write(f"**Practice Question:** {pq}")
    else:
        st.error("No questions found for this tag.")

elif option == "Library":
    st.header("Library of Questions")
    for tag in tags:
        with st.expander(tag):
            questions = get_questions_by_tag(tag)
            if questions:
                for q in questions:
                    id, q_tag, q_question, q_answer, q_logic = q
                    st.write(f"**Question (ID {id}):** {q_question}")
                    tab1, tab2 = st.tabs(["Answer", "Logic"])
                    
                    with tab1:
                        st.write(q_answer)
                    
                    with tab2:
                        st.write(q_logic)
                    st.markdown("---")
            else:
                st.write("No questions found under this tag.")