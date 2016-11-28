from decimal import Decimal
from money import Money, xrates

xrates.install('money.exchange.SimpleBackend')

# counting tools
from collections import Counter
from itertools import chain


# use google datastore to pickle an order!
class Order:
    def __init__(self,currency_code:str='GBP'):
        self.order_dict = {}
        self.total = Money(amount=0,currency=currency_code)

    def _new_total(self):
        for line in self.order_dict:
            self.total.amount += Decimal(line[1])


    def from_dict(self,item_cost_pairs:dict):
        self.order_dict.update(item_cost_pairs)
        self._new_total()
        return self.order_dict

    def from_tuple_list(self,item_price_pairs:dict):
        order_dict = {}
        for line in item_price_pairs:
            order_dict.update({str(line[0]):str(line[1])})
        self.order_dict.update(order_dict)
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
        # convert order_dict to {{"item":{price:"1.00",quantity:1},{"item":{price:"1.00",quantity:1}}
        self._new_total() # just for foolproofing
        unique_items = {}
        for line in self.order_dict:
            key = dict(line).keys()
            price = dict(line).values()
            if key in unique_items:
                unique_items[str(key)]["quantity"] += 1
            elif key not in unique_items:
                unique_items.update({str(key):{"price":price,"quantity":1}})

        paypal_items = {"items":[]}

        for line in unique_items:
            """
            line.keys() # line title / item name
            line["item"]["price"]
            line["item"]["quantity"]
            """
            paypal_items["items"].append({"name":line.keys()[0],"sku":line.keys()[0],"price":line["item"]["price"],"currency":str(self.total.currency),"quantity":line["item"]["quantity"]})
        return paypal_items



