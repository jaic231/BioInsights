import argparse
from openai import OpenAI
import glob

# Initialize OpenAI client
client = OpenAI()

def upload_files():
    file_ids = []
    files_to_upload = glob.glob("data/*")
    for file_path in files_to_upload:
        uploaded_file = client.files.create(
            file=open(file_path, "rb"),
            purpose='assistants'
        )
        file_ids.append(uploaded_file.id)
    return file_ids

def create_assistant(file_ids):
    prompt = """
    You are an expert data analyst. You analyze csv files and answer questions pertaining to them. 
    If you are asked to plot something, DO NOT actually plot anything. ONLY do the following steps if you are asked to plot something.
    1. Find the data from the csv file that pertains to what you were asked to plot
    2. Convert that data into a two-column pandas dataframe that can be used as the input to an Altair chart
    3. Convert that new pandas dataframe to a csv file
    4. Generate a download link for the modified csv file. This csv file will be downloaded, converted back into a pandas dataframe, and then passed into Altair to make a chart.
    Otherwise, just respond to the question with analysis on the data, with specific calculations to back up the analysis.
    """
    assistant = client.beta.assistants.create(
      name="Data Analyst",
      instructions=prompt,
      model="gpt-4-turbo",
      tools=[{"type": "code_interpreter"}],
      tool_resources={
        "code_interpreter": {
          "file_ids": file_ids
        }
      }
    )
    return assistant

def create_thread():
    return client.beta.threads.create()

def delete_thread(thread_id):
    return client.beta.threads.delete(thread_id=thread_id)

def save_id(id, filename):
    with open(filename, "w") as file:
        file.write(id)
        
def main():
    parser = argparse.ArgumentParser(description="Manage Assistants and Threads on OpenAI.")
    parser.add_argument("--create-assistant", action="store_true", help="Create a new assistant")
    parser.add_argument("--create-thread", action="store_true", help="Create a new thread (default action)")
    parser.add_argument("--delete-thread", type=str, help="Delete a thread by providing the thread ID")

    args = parser.parse_args()

    if args.delete_thread:
        delete_thread(args.delete_thread)

    if args.create_assistant:
        file_ids = upload_files()
        assistant = create_assistant(file_ids)
        save_id(assistant.id, "assistant_id.txt")
        print(f"Assistant created with ID: {assistant.id}")

    if args.create_thread or (not args.create_assistant and not args.delete_thread):
        thread = create_thread()
        save_id(thread.id, "thread_id.txt")
        print(f"Thread created with ID: {thread.id}")

if __name__ == "__main__":
    main()
