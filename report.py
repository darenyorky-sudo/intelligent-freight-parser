import csv
import os
from collections import defaultdict

def generate_summary_report(csv_file: str = "all_invoices.csv"):
    """Reads the CSV database and prints a financial summary report."""
    if not os.path.exists(csv_file):
        print(f"Error: Database {csv_file} not found. Run the parser first.")
        return

    total_invoices = 0
    total_amount = 0.0
    vendor_totals = defaultdict(float)

    try:
        with open(csv_file, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                total_invoices += 1
                
                # Safely parse the amount
                amount_str = row.get("total_amount", "0")
                amount = float(amount_str) if amount_str and amount_str.lower() != "none" else 0.0
                total_amount += amount
                
                # Safely parse the vendor (handle empty strings and "None")
                vendor = row.get("vendor_name", "").strip()
                sender = row.get("sender_name", "").strip()
                
                # Smart fallback if vendor is missing
                if not vendor or vendor.lower() == "none":
                    if sender and sender.lower() != "none":
                        vendor = f"Unknown Vendor (Sender: {sender})"
                    else:
                        vendor = "⚠️ Needs Manual Review"
                        
                vendor_totals[vendor] += amount

        # Print the Dashboard
        print("\n" + "="*50)
        print("📊 FREIGHT PARSER - FINAL REPORT 📊")
        print("="*50)
        print(f"Total Invoices Processed: {total_invoices}")
        print(f"Total Revenue/Amount: {total_amount:,.2f} KZT\n")
        
        print("--- Breakdown by Vendor ---")
        for vendor, amount in vendor_totals.items():
            print(f"- {vendor}: {amount:,.2f} KZT")
        print("="*50 + "\n")

    except Exception as e:
        print(f"Error generating report: {e}")

if __name__ == "__main__":
    generate_summary_report()