import os
import shutil
import json
import csv
from src.extractor import extract_text_from_pdf, parse_invoice_with_ai
from src.utils import setup_logger

logger = setup_logger("FreightParser")
CSV_FILE = "all_invoices.csv"

def invoice_exists(invoice_num: str) -> bool:
    """Checks if the invoice number is already present in the CSV file."""
    if not os.path.exists(CSV_FILE):
        return False
    
    try:
        with open(CSV_FILE, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('invoice_number') == str(invoice_num):
                    return True
    except Exception as e:
        logger.error(f"Error reading CSV: {e}")
    return False

def process_all_files():
    """Main function to process all PDF files in the data directory."""
    input_dir = "data"
    output_dir = "processed"
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(input_dir):
        if filename.endswith(".pdf"):
            logger.info(f"Processing: {filename}")
            file_path = os.path.join(input_dir, filename)
            
            raw_text = extract_text_from_pdf(file_path)
            
            if raw_text:
                parsed_json = parse_invoice_with_ai(raw_text)
                if parsed_json:
                    data = json.loads(parsed_json)
                    inv_num = data.get("invoice_number")
                    
                    # Step 1: Check for duplicates
                    if inv_num and invoice_exists(inv_num):
                        logger.warning(f"Duplicate found! Invoice {inv_num} already exists in CSV. Moving file without saving data.")
                    else:
                        # Append to CSV if it's a new invoice
                        with open(CSV_FILE, "a", newline='', encoding='utf-8') as f:
                            writer = csv.DictWriter(f, fieldnames=data.keys())
                            if os.stat(CSV_FILE).st_size == 0:
                                writer.writeheader()
                            writer.writerow(data)
                        logger.info(f"Data saved for invoice: {inv_num}")
                    
                    # Move to processed folder
                    shutil.move(file_path, os.path.join(output_dir, filename))
                    logger.info(f"Successfully moved: {filename}")
                else:
                    logger.error(f"Failed to parse: {filename}")
            else:
                logger.error(f"Could not extract text from: {filename}")

if __name__ == "__main__":
    process_all_files()