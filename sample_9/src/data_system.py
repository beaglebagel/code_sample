
from src.exception import EntitlementError, SubscriptionError
from collections import defaultdict
from dataclasses import dataclass


@dataclass(frozen=True)
class Subscription:
    '''
    Class to represent Subscription.
    '''
    user: str
    stock: str
    currency: str


class DataSystem:
    '''
    DataSystem class provides api interface for CLI commands.

    - only specified symbol, currencies in config are supported.
    - each symbol maintains default denomination currency as defined in config.
    - user entitlement is specified in both stock and currency.
        @NOTE: Slightly modified from the example given in README.md, where defualt(base) currency of stock is
        accessible by default into strictly requiring those currencies to be listed in config. (e.g. TSLA / USD case).
    '''

    def __init__(self, config: dict):

        self.stock_set = set()
        self.currency_set = set()

        self.symbol_currency_map: dict[str, str] = {}
        self.user_entitlement_map: dict[str, set] = defaultdict(set)

        # stock -> { subscription1, subscription2 .. }
        self.stock_subscriptions: dict[str, set[Subscription]] = defaultdict(set)
        # currency -> { subscription1, subscription2 .. }
        self.currency_subscriptions: dict[str, set[Subscription]] = defaultdict(set)
        # stock -> currency -> subscription
        self.stock_user_subscription: dict[str, dict[str, Subscription]] = defaultdict(dict)

        # maintain currency to usd price rate.
        self.currency_to_usd_price: dict = {'USD': 1.00}
        # maintain stock to native price.
        self.stock_price: dict = {}

        symbol_dict = config.get('symbols', {})
        user_dict = config.get('users', {})

        # default currency denomination of stocks.
        for symbol, currency_map in symbol_dict.items():
            self.stock_set.add(symbol)
            currency = currency_map['currency']
            self.currency_set.add(currency)
            self.symbol_currency_map[symbol] = currency

        # maintain stock only set.
        self.stock_set.difference_update(self.currency_set)

        # user entitlement: user -> set of symbols.
        for user, symbols in user_dict.items():
            self.user_entitlement_map[user] = set(symbols)

    def validate(self, stock: str = None, currency: str = None):
        '''
        validate stock, currency input against pre-loaded set.
        only pre-loaded stock, currency are strictly permitted input.
        '''
        # discern stock vs. currency
        if stock and stock not in self.stock_set:
            raise ValueError(f'Invalid {stock=}')
        elif currency and currency not in self.currency_set:
            raise ValueError(f'Invalid {currency=}')

    def validate_entitlement(self, user: str, stock: str = None, currency: str = None):
        '''
        check user entitlement per stock & currency.
        '''
        if stock and stock not in self.user_entitlement_map[user]:
            raise EntitlementError(f'{user=} is not entitled to {stock=}')
        elif currency and currency not in self.user_entitlement_map[user]:
            raise EntitlementError(f'{user=} is not entitled to {currency=}')

    def is_currency(self, symbol: str) -> bool:
        '''
        discern whether the symbol is currency or stock.
        '''
        if symbol and symbol in self.currency_set:
            return True
        return False

    def derive_price(self, stock: str, target_currency: str) -> str:
        '''
        derive stock's price from unit of base currency to unit of target_currency.
        if either of stock, stock's base_currency, or target_currency's price in unavailable, return ''.

        derived price is in 2 decimal str format.
        '''
        if (stock not in self.stock_price or
                target_currency not in self.currency_to_usd_price or
                self.symbol_currency_map[stock] not in self.currency_to_usd_price):
            return ''

        base_currency_price = self.currency_to_usd_price[self.symbol_currency_map[stock]]
        native_price = (self.stock_price[stock] *
                        (base_currency_price / self.currency_to_usd_price[target_currency]))
        native_price = f'{native_price:.2f}'
        return native_price

    def tick(self, symbol: str, price: float) -> str:
        '''
        update the stock or currency price (via stock) and publish latest subscriptions info related to price info.
        price section will be omitted if either underlying currency's price or stock price is unavailable yet.

        Parameters
        ----------
        symbol : stock or currency symbol
        price : float price

        Returns
        -------
        sorted list of subscriptions with price (if available).
        '''

        is_currency = self.is_currency(symbol=symbol)
        if is_currency:
            self.validate(currency=symbol)
            subscriptions = self.currency_subscriptions[symbol]
            self.currency_to_usd_price[symbol] = price
        else:
            self.validate(stock=symbol)
            subscriptions = self.stock_subscriptions[symbol]
            # ? get base currency's price in usd.
            self.stock_price[symbol] = price

        # find default currency to use if symbol's usd price is not found. ??
        result = []
        for sub in subscriptions:

            native_price = self.derive_price(stock=sub.stock, target_currency=sub.currency)
            result.append(f'{sub.user} {sub.stock} {sub.currency} {native_price}'.strip())

        return '\n'.join(sorted(result))

    def subscribe(self, user: str, stock: str, currency: str = None) -> str:
        '''
        creates new or replaces subscriptions of user + stock + currency

        Parameters
        ----------
        user : user name
        stock : stock ticker symbol
        currency : use stock's base currency if not provided.

        Returns
        -------
        string representation of subscriotion with price info (if available).
        '''

        self.validate(stock=stock, currency=currency)
        self.validate_entitlement(user=user, stock=stock, currency=currency)

        # resolve to default currency if not specified.
        currency = currency or self.symbol_currency_map[stock]

        new_subscription = Subscription(user=user, stock=stock, currency=currency)

        subscription = self.stock_user_subscription[stock].get(user)

        if subscription == new_subscription:
            raise SubscriptionError(f'Subscription already exists. {user=} {stock=} {currency=}')

        # add or replace as new subscription.
        # replace previous currency's subscription.
        if subscription:
            self.stock_subscriptions[stock].remove(subscription)
            self.currency_subscriptions[subscription.currency].remove(subscription)
            del self.stock_user_subscription[stock][user]

        self.stock_subscriptions[stock].add(new_subscription)
        self.currency_subscriptions[currency].add(new_subscription)
        self.stock_user_subscription[stock][user] = new_subscription

        price = self.derive_price(stock=stock, target_currency=currency)
        return f'{user} {stock} {currency} {price}'.strip()

    def unsubscribe(self, user: str, stock: str, currency: str = None) -> None:
        '''
        removes existing subscription of user + stock + currency

        Parameters
        ----------
        user : user name
        stock : stock ticker symbol
        currency : use stock's base currency if not provided.
        '''

        self.validate(stock=stock, currency=currency)
        self.validate_entitlement(user=user, stock=stock, currency=currency)

        # resolve currency
        currency = currency or self.symbol_currency_map[stock]

        un_subscription = Subscription(user=user, stock=stock, currency=currency)

        subscription = self.stock_user_subscription[stock].get(user)
        if not subscription or subscription != un_subscription:
            raise SubscriptionError(f'Subscription does not exists. {user=} {stock=} {currency=}')

        # remove subscriptions
        self.stock_subscriptions.get(stock).remove(un_subscription)
        self.currency_subscriptions.get(currency).remove(un_subscription)
        del self.stock_user_subscription[stock][user]

    def __repr__(self):
        return (
            f'DataSystem \n'
            f'{self.stock_set=}\n'
            f'{self.currency_set=}\n'
            f'{self.stock_subscriptions=}\n'
            f'{self.currency_subscriptions=}\n'
            f'{self.stock_user_subscription=}\n'
            f'{self.user_entitlement_map=}\n'
            f'{self.symbol_currency_map=}\n'
            f'{self.currency_to_usd_price=}\n'
            f'{self.stock_price=}\n')