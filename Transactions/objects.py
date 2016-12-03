from decimal import *
from money import Money, xrates

xrates.install('money.exchange.SimpleBackend')

# counting tools
from collections import Counter
from itertools import chain

import json

# use google datastore to pickle an order!
class Order:
    def __init__(self,currency_code:str='GBP'):
        self.currency_code = currency_code
        self.order_dict = {}
        print(self.currency_code)
        self.total = Money(amount=0,currency=self.currency_code)

    def _new_total(self):
        for name,properties in self.order_dict.items():
            # print("Properties",properties["price"]) debbuging
            subtotal = Decimal(properties["price"]) * Decimal(int(properties["quantity"]))
            self.total = self.total + Money(subtotal,self.currency_code)


    def add_to_order_from_dict(self, paypal_transaction_item_list:dict):
        self.order_dict.update(paypal_transaction_item_list)
        self._new_total()
        return self.order_dict

    def from_json(self,order_json:str):
        self.order_dict = json.loads(order_json)
        self._new_total()
        return self.order_dict

    def total_to_gbp(self):
        return self.total.to('GBP')

    def total_to_currency(self,new_currency_code:str):
        return self.total.to(new_currency_code)

    def add_line(self,item:str,cost:str,quantity:int=1):
        for line in range(quantity):
            self.order_dict.update({str(item):str(cost)})
        self._new_total()
        return self.order_dict
    def to_paypal_transaction_items_list(self):
        # convert order_dict to {"wax":{price:"1.00",quantity:1},"candle":{price:"1.00",quantity:2}}
        self._new_total() # just for foolproofing

        paypal_items = {"items":[]}

        print(self.order_dict)

        for item, properties in self.order_dict.items():
            paypal_items["items"].append({"name":item,"sku":item,"price":properties["price"],"currency":str(self.total.currency),"quantity":properties["quantity"]})
        print(paypal_items)
        return paypal_items

    def __money__(self):
        assert isinstance(self.total,Money)
        return self.total

    def __decimal__(self):
        return Decimal(self.total.amount)