import streamlit as st
import pandas as pd
import altair as alt
import os

from openai import OpenAI
import time 
import shutil

client = OpenAI()

# Load assistant ID and thread ID from separate files
with open("assistant_id.txt", "r") as file:
    assistant_id = file.read().strip()

with open("thread_id.txt", "r") as file:
    thread_id = file.read().strip()

plot_container = None

def download_file(cited_file):
    if 'init_done' not in st.session_state: return
    if not st.session_state.init_done: return
    data = client.files.content(cited_file.id)
    data_bytes = data.read()
    file_path = f"tmp/{cited_file.id}.csv"

    with open(file_path, "wb") as file:
        file.write(data_bytes)
    # display_chart(f"{cited_file.id}.csv", "tmp")

    if 'new_files' not in st.session_state:
        st.session_state.new_files = []
    st.session_state.new_files.append(f"{cited_file.id}.csv")

def get_messages():
    if "cursor" not in st.session_state:
        st.session_state.cursor = None
    thread_messages = client.beta.threads.messages.list(thread_id, limit=100, order='desc', before=st.session_state.cursor)
    messages = []
    for message in thread_messages.data[::-1]:
        for block in message.content:
            if block.type == "text":
                text = block.text
                annotations = text.annotations
                citations = []
                for index, annotation in enumerate(annotations):
                    text.value = text.value.replace(annotation.text, f' [{index}]')
                    if file_citation := getattr(annotation, 'file_path', None):
                        cited_file = client.files.retrieve(file_citation.file_id)
                        download_file(cited_file)
                messages.append({"id": message.id, "role": message.role, "content": text.value})
    if 'init_done' not in st.session_state:
        st.session_state.init_done = True  # Mark initialization complete
    if messages:
        st.session_state.cursor = messages[-1]["id"]
    return messages

def load_and_plot_data():
    if not os.path.exists('charts'):
        os.makedirs('charts')
    if not os.path.exists('tmp'):
        os.makedirs('tmp')
    global plot_container
    plot_container = st.container(height=450)

    with plot_container:
        # Load and display charts from the 'charts' directory (pinned)
        for file in os.listdir("charts"):
            display_chart(file, "charts")

        # Load and display new charts created in this session
        for file in st.session_state.get('new_files', []):
            if file not in os.listdir("charts"):  # Avoid duplication with pinned charts
                display_chart(file, "tmp")

def save_plot(path, file):
    destination = os.path.join("charts", file)
    shutil.copy(path, destination)

def delete_plot(file):
    destination = os.path.join("charts", file)
    os.remove(destination)

def display_chart(file, folder):
    path = os.path.join(folder, file)
    data = pd.read_csv(path)
    chart = (
        alt.Chart(data)
        .mark_circle()
        .encode(x=data.columns[0], y=data.columns[1])
    )
    col1, col2 = st.columns([1, 9])
    if folder == "charts":
        col1.button('🗑️', on_click=delete_plot, args=[file], key=f"button_{file}")
    else:
        col1.button('📌', on_click=save_plot, args=[path, file], key=f"button_{file}")
    col2.altair_chart(chart, use_container_width=True)

def sendMessage(content):
    thread_message = client.beta.threads.messages.create(
        thread_id,
        role="user",
        content=content,
    )
    st.session_state.cursor = thread_message.id
    return thread_message

# Function to add a message to the thread and run it
def run_assistant():
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id
    )
    return run.id

# Function to check if the thread is finished
def check_run_status(run_id):
    run = client.beta.threads.runs.retrieve(
        thread_id=thread_id,
        run_id=run_id
    )
    return run.status

def main():
    # Set up the Streamlit app layout
    st.set_page_config(layout="wide")
    st.title("BioInsights 🧬🔬")

    col1, col2 = st.columns(2)

    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.messages = get_messages()

    # Chatbox in the left column
    with col1:
        st.header("Chat")

        chat_container = st.container(height=450)

        # Display chat messages in the scrollable container
        with chat_container:
            for message in st.session_state.messages:
                st.chat_message(message["role"]).markdown(message["content"])

        if prompt := st.chat_input("What's up?"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with chat_container:
                st.chat_message("user").markdown(prompt)
            sendMessage(prompt)
            run_id = run_assistant()
            status = check_run_status(run_id)
            while status != "completed":
                time.sleep(5)
                status = check_run_status(run_id)
            newMessages = get_messages()
            st.session_state.messages += newMessages
            with chat_container:
                for message in newMessages:
                    st.chat_message(message["role"]).markdown(message["content"])

    # Plots in the right column
    with col2:
        st.header("Plots")
        load_and_plot_data()

main()