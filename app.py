import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from backend import *

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

@app.route('/invoice', methods=['POST'])
def create_invoice_endpoint():
    try:
        print("beginning of function====================")
        data = request.get_json()
        amount = data.get("amount")
        memo = data.get("memo")

        # Create LNbits invoice
        invoice = create_coinos_invoice(amount, webhook_url="https://pip-blond.vercel.app/api/webhook")
 
        # Save invoice to Supabase
        print("before create supabase")
        print(invoice)
        save_invoice_to_supabase(invoice, amount, memo)
        print("after create supabase")
        
        return jsonify({"success": True, "invoice": invoice}), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/payment_status/<string:payment_hash>', methods=['GET'])

@app.route('/invoices', methods=['GET'])
def list_all_invoices_endpoint():
    try:
        invoices = list_all_invoices()
        return jsonify({"success": True, "invoices": invoices}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/tasks/<int:id>', methods=['GET'])
def get_tasks_by_user_route(id):
    """
    Route to fetch tasks created by a specific user.
    
    :param id: The user ID.
    :return: JSON response containing the user's tasks.
    """
    try:
        tasks = fetch_tasks_by_user(id)
        return jsonify({"success": True, "tasks": tasks}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/invoices/task/<int:task_id>', methods=['GET'])
def list_invoices_by_task_id_endpoint(task_id):
    """
    Route to fetch all invoices associated with a specific task_id.

    :param task_id: The ID of the task.
    :return: JSON response containing the list of invoices.
    """
    try:
        invoices = list_invoices_by_task_id(task_id)
        return jsonify({"success": True, "invoices": invoices}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

if __name__ == "__main__":
    # Use the environment variable PORT, defaulting to 5000 if not set
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

