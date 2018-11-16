from datetime import datetime

from pony.orm import Required, Optional, PrimaryKey
from app import db

CurrencyMapping = {
    "RUB": 643,
    "EUR": 978,
    "USD": 840
}

CurrencyRevMapping = {
    643: "RUB",
    978: "EUR",
    840: "USD"
}


class InvoiceMessage(db.Entity):
    id = PrimaryKey(int, auto=True)
    amount = Required(int, unsigned=True)
    currency_code = Required(int, unsigned=True)
    created = Required(datetime)
    comment = Optional(str)

    @property
    def currency(self):
        return CurrencyRevMapping[self.currency_code]


def create_from(data: dict):
    return InvoiceMessage(created=datetime.now(), amount=data["amount"],
                          currency_code=CurrencyMapping[data.get('currency').upper()],
                          comment=data.get('comment'))
