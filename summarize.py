from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))

def docuSum(text, mode):
    response = client.responses.create(
        model = "gpt-5-nano",
        instructions = "You are given the text for a document and your job is to summarize it based on the type of summary the user wants.",
        input = f"Type of summary: {mode} || Text: {text}"
    )
    return response.output_text, response.usage.total_tokens