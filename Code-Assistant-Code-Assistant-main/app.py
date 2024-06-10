import requests
import json
import gradio as gr
import pandas as pd
import docx2txt
import PyPDF2

# API endpoint and headers
url = "http://localhost:11434/api/generate"
headers = {
    'Content-Type': 'application/json'
}

# To store conversation history
history = []

def extract_text_from_file(file):
    # Determine the file type and extract text accordingly
    if file.name.endswith('.pdf'):
        text = ""
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    elif file.name.endswith('.docx'):
        text = docx2txt.process(file)
        return text
    elif file.name.endswith('.csv'):
        df = pd.read_csv(file)
        text = df.to_string()
        return text
    else:
        return "Unsupported file format."

def generate_response(file):
    # Extract text from the file
    text = extract_text_from_file(file)
    
    # Append the extracted text to the history
    history.append(text)
    # Create the final prompt by joining the history
    final_prompt = "\n".join(history)
    
    # Prepare the data to send in the request
    data = {
        "model": "codeguru",
        "prompt": final_prompt,
        "stream": False
    }
    
    # Send the request to the API
    response = requests.post(url, headers=headers, data=json.dumps(data))
    
    if response.status_code == 200:
        try:
            # Parse the response JSON
            data = response.json()
            # Extract the actual response
            actual_response = data['response']
            # Add the response to the history
            history.append(actual_response)
            return actual_response
        except (json.JSONDecodeError, KeyError) as e:
            return f"Error parsing response: {e}"
    else:
        # Return an error message if the request failed
        return f"Error: {response.status_code}, {response.text}"

# Create the Gradio interface
interface = gr.Interface(
    fn=generate_response,
    inputs=gr.File(file_count="single", type="binary", label="Upload your file (PDF, DOCX, or CSV)"),
    outputs="text",
    title="File-based Prompt Generator"
)

# Launch the interface
interface.launch()

