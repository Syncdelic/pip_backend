from flask import Flask, request, jsonify
from backend import create_invoice, save_invoice_to_supabase, list_all_invoices

app = Flask(__name__)

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

if __name__ == "__main__":
    app.run(debug=True)

