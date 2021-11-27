from flask import Flask, jsonify, request

from model.transfer import Transfer, TransferSchema
from model.transaction_type import TransactionType

app = Flask(__name__)

transactions = [
  Transfer('Salary', 5000),
  Transfer('Dividends', 200)
]


@app.route('/transfer')
def get_transfer():
    schema = TransferSchema(many=True)
    transfer = schema.dump(
        filter(lambda t: t.type == TransactionType.TRANSFER, transactions)
    )
    return jsonify(transfer)


@app.route('/transfer', methods=['POST'])
def add_transfer():
    transfer = TransferSchema().load(request.get_json())
    transactions.append(transfer.data)
    return "", 204


if __name__ == "__main__":
    app.run(debug=True)
