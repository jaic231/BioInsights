
# BioInsights

## Setup

### 1. Install Requirements
First, ensure that Python 3 is installed on your machine. Then, install the required Python packages by running the following command:
```bash
pip install -r requirements.txt
```

### 2. Set Up OpenAI API Key
Before running the script, you need to export your OpenAI API key as an environment variable. Replace `YOUR_API_KEY` with your actual OpenAI API key.
```bash
export OPENAI_API_KEY=YOUR_API_KEY
```

## Usage

### Create an Assistant
To create an assistant, run the script with the `--create-assistant` flag:
```bash
python openai_manager.py --create-assistant
```

Make sure to copy the assistant and thread ids into your app.py file.

### Manage Threads
#### Create a Thread
To create a new thread, use the following command:
```bash
python openai_manager.py --create-thread
```

#### Delete a Thread
If you need to delete an old thread, you can do so by providing the thread ID to the `--delete-thread` option:
```bash
python openai_manager.py --delete-thread=THREAD_ID
```

Replace `THREAD_ID` with the actual ID of the thread you want to delete.

## Note
Ensure that the environment variable for the OpenAI API key is set each time in the terminal session where you are running the script.
