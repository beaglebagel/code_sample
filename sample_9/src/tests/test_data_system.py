"""
Test module for DataSystem.
"""

import pytest

from src.data_system import DataSystem

# test constants.
from src.exception import EntitlementError, SubscriptionError

TEST_STOCK_A= 'TEST_STOCK_A'
TEST_STOCK_B = 'TEST_STOCK_B'
TEST_STOCK_C = 'TEST_STOCK_C'
TEST_USER_A = 'TEST_USER_A'
TEST_USER_B = 'TEST_USER_B'
TEST_USER_C = 'TEST_USER_C'
TEST_CURRENCY_A = 'TEST_CURRENCY_A'
TEST_CURRENCY_B = 'TEST_CURRENCY_B'
TEST_CURRENCY_C = 'TEST_CURRENCY_C'
TEST_CURRENCY_USD = 'USD'
INVALID_USER = 'INVALID_USER'
INVALID_STOCK = 'INVALID_STOCK'
INVALID_CURRENCY = 'INVALID_CURRENCY'
TEST_PRICE_1_00 = 1.00
TEST_PRICE_1_25 = 1.25
TEST_PRICE_80 = 80.0
TEST_PRICE_100 = 100.0
TEST_PRICE_200 = 200.0

TEST_CONFIG = {
    'symbols': {
        TEST_STOCK_A: {
            'currency': TEST_CURRENCY_A
        },
        TEST_STOCK_B: {
            'currency': TEST_CURRENCY_B
        },
        TEST_STOCK_C: {
            'currency': TEST_CURRENCY_C
        }
    },
    'users': {
        TEST_USER_A: [TEST_STOCK_A, TEST_STOCK_B, TEST_CURRENCY_A, TEST_CURRENCY_B],
        TEST_USER_B: [TEST_STOCK_B, TEST_STOCK_C, TEST_CURRENCY_B],
        TEST_USER_C: [TEST_STOCK_A, TEST_STOCK_B, TEST_STOCK_C, TEST_CURRENCY_A, TEST_CURRENCY_B, TEST_CURRENCY_C]
    }
}


def test_validate():

    test_system = DataSystem(config=TEST_CONFIG)

    with pytest.raises(ValueError):
        test_system.validate(stock=INVALID_STOCK)

    with pytest.raises(ValueError):
        test_system.validate(currency=INVALID_CURRENCY)

    with pytest.raises(ValueError):
        test_system.validate(stock=TEST_STOCK_A, currency=INVALID_CURRENCY)

    with pytest.raises(ValueError):
        test_system.validate(stock=INVALID_STOCK, currency=TEST_CURRENCY_A)


def test_validate_entitlement():
    test_system = DataSystem(config=TEST_CONFIG)

    assert not test_system.validate_entitlement(user=TEST_USER_A, stock=TEST_STOCK_A)
    assert not test_system.validate_entitlement(user=TEST_USER_A, currency=TEST_CURRENCY_A)
    assert not test_system.validate_entitlement(user=TEST_USER_A, stock=TEST_STOCK_A, currency=TEST_CURRENCY_A)

    with pytest.raises(EntitlementError):
        test_system.validate_entitlement(user=TEST_USER_A, stock=INVALID_STOCK)

    with pytest.raises(EntitlementError):
        test_system.validate_entitlement(user=INVALID_USER, stock=TEST_STOCK_A)

    with pytest.raises(EntitlementError):
        test_system.validate_entitlement(user=TEST_USER_A, stock=TEST_STOCK_A, currency=INVALID_CURRENCY)


def test_is_currency():
    test_system = DataSystem(config=TEST_CONFIG)
    assert not test_system.is_currency(symbol=TEST_STOCK_A)
    assert test_system.is_currency(symbol=TEST_CURRENCY_A)


def test_derive_price():
    test_system = DataSystem(config=TEST_CONFIG)

    # neither stock A nor currency A price available.
    assert not test_system.derive_price(stock=TEST_STOCK_A, target_currency=TEST_CURRENCY_A)

    test_system.tick(symbol=TEST_STOCK_A, price=100)

    # currency A price not available.
    assert not test_system.derive_price(stock=TEST_STOCK_A, target_currency=TEST_CURRENCY_A)

    # currency A price available.
    test_system.tick(symbol=TEST_CURRENCY_A, price=TEST_PRICE_1_00)
    assert f'{TEST_PRICE_100:.2f}' == test_system.derive_price(stock=TEST_STOCK_A, target_currency=TEST_CURRENCY_A)


def test_tick():
    test_system = DataSystem(config=TEST_CONFIG)
    # invalid input 1
    with pytest.raises(ValueError):
        test_system.tick(symbol=INVALID_STOCK, price=0)
    # invalid input 2
    with pytest.raises(ValueError):
        test_system.tick(symbol=INVALID_CURRENCY, price=0)

    # plain tick insert
    assert not test_system.tick(symbol=TEST_STOCK_A, price=TEST_PRICE_100)
    assert {TEST_STOCK_A: TEST_PRICE_100} == test_system.stock_price

    # insert test subscription.
    test_system.subscribe(user=TEST_USER_A, stock=TEST_STOCK_A)

    # no currency price yet, blank price
    assert f'{TEST_USER_A} {TEST_STOCK_A} {TEST_CURRENCY_A}' == \
           test_system.tick(symbol=TEST_STOCK_A, price=TEST_PRICE_100).strip()

    # update currency A price
    assert f'{TEST_USER_A} {TEST_STOCK_A} {TEST_CURRENCY_A} {TEST_PRICE_100:.2f}' == \
           test_system.tick(symbol=TEST_CURRENCY_A, price=TEST_PRICE_1_00)

    # update stock A price
    assert f'{TEST_USER_A} {TEST_STOCK_A} {TEST_CURRENCY_A} {TEST_PRICE_200:.2f}' == \
           test_system.tick(symbol=TEST_STOCK_A, price=TEST_PRICE_200)

    # test C subscribes to stock A
    test_system.subscribe(user=TEST_USER_C, stock=TEST_STOCK_A, currency=TEST_CURRENCY_A)

    assert '\n'.join(sorted(
        [
            f'{TEST_USER_C} {TEST_STOCK_A} {TEST_CURRENCY_A} {TEST_PRICE_100:.2f}',
            f'{TEST_USER_A} {TEST_STOCK_A} {TEST_CURRENCY_A} {TEST_PRICE_100:.2f}',
        ])) == test_system.tick(symbol=TEST_STOCK_A, price=TEST_PRICE_100)

    # test C subscribes to stock A
    # update currency C price
    test_system.tick(symbol=TEST_CURRENCY_C, price=TEST_PRICE_1_25)
    # update user C's subscription to currency C.
    test_system.subscribe(user=TEST_USER_C, stock=TEST_STOCK_A, currency=TEST_CURRENCY_C)
    print(test_system)

    assert '\n'.join(sorted(
        [
            f'{TEST_USER_C} {TEST_STOCK_A} {TEST_CURRENCY_C} {TEST_PRICE_80:.2f}',
            f'{TEST_USER_A} {TEST_STOCK_A} {TEST_CURRENCY_A} {TEST_PRICE_100:.2f}',
        ])) == test_system.tick(symbol=TEST_STOCK_A, price=TEST_PRICE_100)
    # print(test_system)


def test_subscribe():
    test_system = DataSystem(config=TEST_CONFIG)
    # subscription add, omit currency
    assert (f'{TEST_USER_A} {TEST_STOCK_A} {TEST_CURRENCY_A}' ==
           test_system.subscribe(user=TEST_USER_A, stock=TEST_STOCK_A).strip())

    # subscription overlap
    with pytest.raises(SubscriptionError):
        test_system.subscribe(user=TEST_USER_A, stock=TEST_STOCK_A, currency=TEST_CURRENCY_A)

    # subscription add
    assert (f'{TEST_USER_B} {TEST_STOCK_B} {TEST_CURRENCY_B}' ==
            test_system.subscribe(user=TEST_USER_B, stock=TEST_STOCK_B, currency=TEST_CURRENCY_B).strip())

    # subscription add
    test_system.subscribe(user=TEST_USER_C, stock=TEST_STOCK_C, currency=TEST_CURRENCY_C)

    # change subscription's currency
    assert (f'{TEST_USER_C} {TEST_STOCK_C} {TEST_CURRENCY_B}' ==
        test_system.subscribe(user=TEST_USER_C, stock=TEST_STOCK_C, currency=TEST_CURRENCY_B).strip())


def test_unsubscribe():
    test_system = DataSystem(config=TEST_CONFIG)

    # non-existant subscription
    with pytest.raises(SubscriptionError):
        test_system.unsubscribe(user=TEST_USER_A, stock=TEST_STOCK_A)

    # subscribe, wrongly addressed subscription.
    test_system.subscribe(user=TEST_USER_A, stock=TEST_STOCK_A, currency=TEST_CURRENCY_A)
    with pytest.raises(SubscriptionError):
        test_system.unsubscribe(user=TEST_USER_A, stock=TEST_STOCK_A, currency=TEST_CURRENCY_B)

    # unsubscribe success
    test_system.unsubscribe(user=TEST_USER_A, stock=TEST_STOCK_A)
    assert not test_system.stock_subscriptions[TEST_USER_A]
    assert not test_system.currency_subscriptions[TEST_CURRENCY_A]
    assert not test_system.stock_user_subscription[TEST_STOCK_A]
