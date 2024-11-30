from flask import Flask, request, jsonify
from flask_cors import CORS
from backend import create_invoice, save_invoice_to_supabase, list_all_invoices

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

@app.route('/invoice', methods=['POST'])
def create_invoice_endpoint():
    try:
        data = request.get_json()
        amount = data.get("amount")
        memo = data.get("memo")

        # Create LNbits invoice
        invoice = create_invoice(amount, memo)
        
        # Save invoice to Supabase
        save_invoice_to_supabase(invoice, amount, memo)
        
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

