from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from quiz_templates import create_multiple_choice_template, create_true_false_template, create_open_ended_template
from typing import List
import streamlit as st


class QuizTrueFalse(BaseModel):
    quiz_text: str = Field(description="The quiz text")
    questions: List[str] = Field(description="The quiz questions")
    answers: List[str] = Field(description="The quiz answers for each question as True or False only.")


class QuizMultipleChoice(BaseModel):
    quiz_text: str = Field(description="The quiz text")
    questions: List[str] = Field(description="The quiz questions")
    alternatives: List[List[str]] = Field(description="The quiz alternatives for each question as a list of lists")
    answers: List[str] = Field(description="The quiz answers")
    
class QuizOpenEnded(BaseModel):
    questions: List[str] = Field(description="The quiz questions")
    answers: List[str] = Field(description="The quiz answers")


def create_quiz_chain(prompt_template, llm, pydantic_object_schema):
    """Creates the chain for the quiz app."""
    return prompt_template | llm.with_structured_output(pydantic_object_schema)


def main():
    st.title("Quiz App")
    st.write("This app generates a quiz based on a given context.")

    # Initialize session state variables if they don't already exist
    for key in ["questions", "answers", "user_answers", "alternatives", "context", "num_questions", "quiz_type_index"]:
        if key not in st.session_state:
            st.session_state[key] = [] if key in ["questions", "answers", "user_answers", "alternatives"] else None

    # Get OpenAI API Key securely
    openai_api_key = st.sidebar.text_input("Enter your OpenAI API key", type="password")
    if not openai_api_key:
        st.error("Please enter your OpenAI API key")
        return

    # Initialize LLM
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0, openai_api_key=openai_api_key)

    # Quiz Settings
    context = st.text_area("Enter the concept/context for the quiz", value=st.session_state.get('context', ''))
    num_questions = st.number_input("Enter the number of questions", min_value=1, max_value=10, value=st.session_state.get('num_questions', 3))
    quiz_type = st.selectbox("Select the quiz type", ["multiple-choice", "true-false", "open-ended"], index=st.session_state.get('quiz_type_index', 0))

    # Select Prompt and Schema
    if quiz_type == "multiple-choice":
        prompt_template = create_multiple_choice_template()
        pydantic_object_schema = QuizMultipleChoice
    elif quiz_type == "true-false":
        prompt_template = create_true_false_template()
        pydantic_object_schema = QuizTrueFalse
    elif quiz_type == "open-ended":
        prompt_template = create_open_ended_template()
        pydantic_object_schema = QuizOpenEnded

    # Generate Quiz
    if st.button("Generate Quiz"):
        chain = create_quiz_chain(prompt_template, llm, pydantic_object_schema)
        quiz_response = chain.invoke({"num_questions": num_questions, "quiz_context": context})

        # Store questions and answers in session state
        st.session_state.questions = quiz_response.questions
        st.session_state.answers = quiz_response.answers
        if quiz_type == "multiple-choice":
            st.session_state.alternatives = quiz_response.alternatives
        st.session_state.user_answers = [None] * len(quiz_response.questions)
        st.session_state.context = context
        st.session_state.num_questions = num_questions
        st.session_state.quiz_type_index = ["multiple-choice", "true-false", "open-ended"].index(quiz_type)

    # Display Quiz Questions
    if st.session_state.questions:
        with st.form(key='quiz_form'):
            display_questions(quiz_type)
            submitted = st.form_submit_button("Submit Answers")
            if submitted:
                process_submission(quiz_type)


def display_questions(quiz_type):
    """Displays questions based on quiz type and stores user responses."""
    if quiz_type == "multiple-choice":
        for i, question in enumerate(st.session_state.questions):
            st.markdown(question)
            options = st.session_state.alternatives[i]
            selected_option = st.radio("Select your answer", options, key=f"question_{i}")

            # Convert selected option to identifier (a, b, c, d, etc.)
            option_index = options.index(selected_option)
            st.session_state.user_answers[i] = chr(97 + option_index)  # 'a', 'b', 'c', etc.

    elif quiz_type == "true-false":
        for i, question in enumerate(st.session_state.questions):
            st.markdown(question)
            selected_option = st.radio("Select your answer", ["True", "False"], key=f"question_{i}")
            st.session_state.user_answers[i] = selected_option

    elif quiz_type == "open-ended":
        for i, question in enumerate(st.session_state.questions):
            st.markdown(question)
            user_input = st.text_area("Enter your answer", key=f"question_{i}")
            st.session_state.user_answers[i] = user_input


def process_submission(quiz_type):
    """Processes submitted answers and displays the score."""
    if None in st.session_state.user_answers:
        st.warning("Please answer all the questions before submitting.")
        return

    if quiz_type in ["multiple-choice", "true-false"]:
        score = sum(
            user_answer == correct_answer
            for user_answer, correct_answer in zip(st.session_state.user_answers, st.session_state.answers)
        )
        st.success(f'Your score is {score}/{len(st.session_state.questions)}')

    elif quiz_type == "open-ended":
        st.write("Your answers have been recorded! Open-ended responses are subjective.")


if __name__ == "__main__":
    main()
