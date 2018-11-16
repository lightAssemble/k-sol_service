import logging
import os

from flask import Flask, send_file, request, jsonify
from pony.orm import db_session

import app_db

env = os.environ

if "TEST_LOG_FILE" in env:
    logging.basicConfig(filename=env["TEST_LOG_FILE"], level=logging.INFO)


app = Flask(__name__)
db = app_db.get(env.get("DATABASE_URL"))

from invoicing_message import InvoiceMessage, CurrencyMapping, create_from
from pay_api import PayApi

payApi = PayApi(logging.getLogger("PayApi"),
                env["SECRET_KEY"],  # SecretKey01
                env["SHOP_ID"],  # 5
                CurrencyMapping[env["SHOP_CURRENCY"]],  # CurrencyMapping["USD"],
                env["PAYWAY"])

CriticalError = (dict(error=True, message="Unprocessable critical error"))

db.generate_mapping(create_tables=True)


@app.route('/')
def index():
    return send_file("./assets/index.html")


@app.route("/process", methods=["POST"])
def process():
    message = get_message()
    if not message:
        return jsonify(CriticalError)

    result = pay_use(message)

    if not result:
        return jsonify(CriticalError)

    return jsonify(dict(error=False, **result))


def pay_use(message: InvoiceMessage):
    try:
        return try_pay_use(message)
    except Exception as e:
        logging.error("Error during message processing, " + str(e.args))
        pass


def try_pay_use(message: InvoiceMessage):
    if message.currency == "EUR":
        return payApi.pay(message, message.id)
    elif message.currency == "USD":
        return payApi.bill(message, message.id)
    elif message.currency == "RUB":
        return payApi.invoice(message, message.id)


def get_message():
    try:
        with db_session:
            return create_from(request.json)
    except Exception as e:
        logging.error("Error during parsing message, " + str(e.args))

if __name__ == '__main__':

    port = int(env.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
