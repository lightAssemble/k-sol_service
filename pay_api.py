import requests
from urllib.request import quote
import hashlib
from json import dumps
from invoicing_message import InvoiceMessage


def create_sign(data: dict, secret_key, keys_require: list):
    keys_require = keys_require.copy()
    keys_require.sort()
    hash_data = ":".join(str(data[k]) for k in keys_require) + secret_key

    m = hashlib.sha256()
    m.update(hash_data.encode('utf8'))
    return m.hexdigest()


def with_parameters(url, pay_data):
    return url + "?" + '&'.join(f"{k}={quote(str(v))}" for k, v in pay_data.items() if v)


class PayApi:
    PAY_KEYS_REQUIRE = ["shop_id", "amount", "currency", "shop_order_id"]
    PAY_URL = "https://pay.piastrix.com/ru/pay"

    BILL_KEYS_REQUIRE = ["shop_id", "shop_amount", "shop_currency", "shop_order_id", "payer_currency"]
    BILL_URL = "https://core.piastrix.com/bill/create"

    INVOICE_KEYS_REQUIRE = ["shop_id", "amount", "currency", "shop_order_id", "payway"]
    INVOICE_URL = "https://core.piastrix.com/invoice/create"

    def __init__(self, logger, key, shop_id, shop_currency, payway):
        self.payway = payway
        self.logger = logger
        self.key = key
        self.shop_id = shop_id
        self.shop_currency_code = shop_currency

    def pay(self, message: InvoiceMessage, order_id: int):
        pay_data = dict(
            shop_id=self.shop_id,
            amount=message.amount,
            currency=message.currency_code,
            description=message.comment,
            shop_order_id=order_id,
        )
        pay_data["sign"] = create_sign(pay_data, self.key, self.PAY_KEYS_REQUIRE)

        self.logger.info("Formed link for `pay` method: " + dumps(pay_data))
        return dict(
            url=with_parameters(self.PAY_URL, pay_data)
        )

    def bill(self, message: InvoiceMessage, order_id: int):
        pay_data = dict(
            shop_id=self.shop_id,
            shop_amount=message.amount,
            shop_currency=self.shop_currency_code,
            shop_order_id=order_id,
            description=message.comment,
            payer_currency=message.currency_code,
        )
        pay_data["sign"] = create_sign(pay_data, self.key, self.BILL_KEYS_REQUIRE)

        self.logger.info("Formed link for `bill create` method: " + dumps(pay_data))

        res = requests.post(self.BILL_URL, json=pay_data).json()

        if res['error_code'] != 0:
            self.logger.error("Error during `bill link` request: " + dumps(res))
            return

        self.logger.info("Successfully `bill link` request: " + dumps(pay_data))
        return dict(
            url=res['data']['url']
        )

    def invoice(self, message: InvoiceMessage, order_id: int):
        pay_data = dict(
            shop_id=self.shop_id,
            amount=message.amount,
            currency=message.currency_code,
            shop_order_id=order_id,
            description=message.comment,
            payway=self.payway,
        )
        pay_data["sign"] = create_sign(pay_data, self.key, self.INVOICE_KEYS_REQUIRE)

        self.logger.info("Formed link for `invoice create` method: " + dumps(pay_data))

        res = requests.post(self.INVOICE_URL, json=pay_data).json()

        if res['error_code'] != 0:
            return
        res = res['data']
        return dict(
            url=with_parameters(res["url"], res["data"])
        )
