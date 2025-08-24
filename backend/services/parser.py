import requests
from bs4 import BeautifulSoup
import PyPDF2
from youtube_transcript_api import YouTubeTranscriptApi

def extract_text_from_pdf(file_stream):
    """Extract text from an uploaded PDF file."""
    reader = PyPDF2.PdfReader(file_stream)
    text = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text.append(page_text)
    return "\n".join(text)

def extract_text_from_url(url):
    """Extract text from a webpage."""
    res = requests.get(url, timeout=10)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")
    return soup.get_text(separator="\n")
    
def extract_text(input_data, input_type):
    """
    Generic text extractor. 
    input_type: 'pdf', 'url', or 'text'
    """
    if input_type == "pdf":
        return extract_text_from_pdf(input_data)
    elif input_type == "url":
        return extract_text_from_url(input_data)
    elif input_type == "text":
        return input_data
    else:
        raise ValueError("Unsupported input type")


def extract_text_from_youtube(url, languages=("en", "hi")):
    video_id = url.split("v=")[-1]
    api = YouTubeTranscriptApi()
    transcript = api.fetch(video_id, languages=languages)
    full_text = " ".join([entry.text for entry in transcript])
    return full_text