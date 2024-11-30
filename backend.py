import os
import json
import requests
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
LNBITS_API_URL = os.getenv("LNBITS_API_URL")
LNBITS_API_KEY = os.getenv("LNBITS_API_KEY")

# Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# LNbits headers
lnbits_headers = {"X-Api-Key": LNBITS_API_KEY, "Content-type": "application/json"}

def create_invoice(amount, memo):
    """
    Create an invoice using the LNbits API.
    
    :param amount: The amount in satoshis.
    :param memo: The memo or description for the invoice.
    :return: Dictionary containing 'payment_hash' and 'payment_request'.
    """
    payload = {"out": False, "amount": amount, "memo": memo, "unit": "sat"}
    response = requests.post(f"{LNBITS_API_URL}/payments", headers=lnbits_headers, json=payload)
    
    # Check for successful response
    if response.status_code == 201:
        data = response.json()
        return {
            "payment_hash": data.get("payment_hash"),
            "payment_request": data.get("payment_request"),
        }
    else:
        # Log and raise an exception if the request fails
        raise Exception(f"Error creating invoice: {response.status_code}, {response.json()}")

# Supabase Functionality
def save_invoice_to_supabase(invoice, amount, memo):
    data = {
        "bolt11": invoice["payment_request"],
        "payment_hash": invoice["payment_hash"],
        "amount": amount,
        "memo": memo,
        "status": "pending",
    }
    response = supabase.table("invoices").insert(data).execute()
    if hasattr(response, 'error') and response.error:
        raise Exception(f"Error saving invoice to Supabase: {response.error}")
    return response.data

def list_all_invoices():
    response = supabase.table("invoices").select("*").execute()
    if hasattr(response, 'error') and response.error:
        raise Exception(f"Error listing invoices from Supabase: {response.error}")
    return response.data

