from decimal import Decimal
from money import Money, xrates

xrates.install('money.exchange.SimpleBackend')

# counting tools
from collections import Counter
from itertools import chain


# use google datastore to pickle an order!
class Order:
    def __init__(self,currency_code:str='GBP'):
        self.currency_code = currency_code
        self.order_dict = {}
        print(self.currency_code)
        self.total = Money(amount=0,currency=self.currency_code)

    def _new_total(self):
        for name,value in self.order_dict.items():
            print(name,value)
            self.total = self.total + Money(Decimal(value),self.currency_code)


    def add_to_folder_from_dict(self, paypal_transaction_item_list:dict):
        self.order_dict.update(paypal_transaction_item_list)
        self._new_total()
        return self.order_dict

    def from_json(self,paypal_):
        pass
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
        unique_items = {}

        for key,price in self.order_dict.items():
            # key = dict(line).keys()
            # price = dict(line).values()
            if key in unique_items:
                unique_items[str(key)]["quantity"] += 1
            elif key not in unique_items:
                unique_items.update({str(key):{"price":price,"quantity":1}})

        paypal_items = {"items":[]}

        print(unique_items)

        for item, properties in unique_items.items():
            paypal_items["items"].append({"name":item,"sku":item,"price":properties["price"],"currency":str(self.total.currency),"quantity":properties["quantity"]})
        print(paypal_items)
        return paypal_items

    def __money__(self):
        assert isinstance(self.total,Money)
        return self.total

    def __decimal__(self):
        return Decimal(self.total.amount)