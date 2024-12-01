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
COINOS_API_URL = "https://coinos.io/api/invoice"  # Coinos API endpoint
COINOS_API_TOKEN = os.getenv("COINOS_API_TOKEN")  # API token for Coinos

# Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Headers for LNbits and Coinos APIs
lnbits_headers = {"X-Api-Key": LNBITS_API_KEY, "Content-type": "application/json"}
coinos_headers = {
    "Content-type": "application/json",
    "Authorization": f"Bearer {COINOS_API_TOKEN}",
}

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

def create_coinos_invoice(amount, webhook_url=None, invoice_type="lightning"):
    """
    Create an invoice using the Coinos API.
    
    :param amount: The amount in satoshis.
    :param invoice_type: The type of invoice ("lightning" or other supported types).
    :return: Dictionary containing the invoice details.
    """
    payload = {
        "invoice": {
            "amount": amount,
            "type": invoice_type
        }
    }

    # Include webhook URL if provided
    if webhook_url:
        payload["invoice"]["webhook"] = webhook_url

    response = requests.post(COINOS_API_URL, headers=coinos_headers, json=payload)
    
    # Check for successful response
    if response.status_code == 200:
        data = response.json()

        # Legacy fields are not directly provided by Coinos API; simulate or infer them
        payment_hash = data.get("hash")  # Example: Use the 'id' as the payment hash
        payment_request = data.get("hash")  # Example field from Coinos response

        # Add legacy fields to the response
        data["payment_hash"] = payment_hash
        data["payment_request"] = payment_request

        return data
    else:
        raise Exception(f"Error creating Coinos invoice: {response.status_code}, {response.json()}")

# Supabase Functionality
def save_invoice_to_supabase(invoice, amount, memo):
    data = {
        "bolt11": invoice["hash"],
        "payment_hash": invoice["hash"],
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

def fetch_tasks_by_user(user_id):
    """
    Fetch tasks from the Supabase 'tasks' table where created_by matches the user_id.
    
    :param user_id: The ID of the user.
    :return: A list of tasks.
    :raises Exception: If an error occurs during the query.
    """
    response = supabase.table("tasks").select("*").eq("created_by", user_id).execute()
    if hasattr(response, 'error') and response.error:
        raise Exception(f"Error fetching tasks: {response.error}")
    return response.data

def list_invoices_by_task_id(task_id):
    """
    Fetch invoices from the Supabase 'invoices' table where task_id matches.

    :param task_id: The ID of the task.
    :return: A list of invoices linked to the task.
    :raises Exception: If an error occurs during the query.
    """
    response = supabase.table("invoices").select("*").eq("task_id", task_id).execute()
    if hasattr(response, 'error') and response.error:
        raise Exception(f"Error fetching invoices by task_id: {response.error}")
    return response.data
