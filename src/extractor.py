import os
import pdfplumber
from openai import OpenAI, OpenAIError, RateLimitError, APIConnectionError # Добавлены импорты ошибок
from dotenv import load_dotenv
from src.validator import InvoiceData

load_dotenv()

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extracts raw text from a PDF file."""
    full_text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"
        return full_text
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")
        return ""

def parse_invoice_with_ai(raw_text: str) -> str:
    """Sends text to OpenAI and returns structured JSON with robust error handling."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY is missing from environment variables.")
        return None

    client = OpenAI(api_key=api_key)
    
    try:
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional logistics data extractor."},
                {"role": "user", "content": f"Extract invoice data from the following text: {raw_text}"},
            ],
            response_format=InvoiceData,
        )
        return completion.choices[0].message.parsed.model_dump_json(indent=4)
        
    # Catch specific OpenAI network/server issues
    except APIConnectionError:
        print("AI Error: Failed to connect to OpenAI. Please check your internet connection.")
        return None
    except RateLimitError:
        print("AI Error: OpenAI API quota exceeded or rate limit reached. Check billing.")
        return None
    except OpenAIError as e:
        print(f"AI Error: An OpenAI-specific error occurred: {e}")
        return None
    # Catch any other unexpected python errors
    except Exception as e:
        print(f"System Error: Unexpected failure during AI parsing: {e}")
        return None