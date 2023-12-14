
import sys
import json
import traceback

from src.exception import EntitlementError, SubscriptionError
from dataclasses import dataclass
from data_system import DataSystem

'''
cli interface for market data system.
'''

COMMANDS = {'tick', 'subscribe', 'unsubscribe', 'print', 'quit'}


@dataclass(frozen=True)
class Subscription:
    '''
    Class to represent Subscription.
    '''
    user: str
    stock: str
    currency: str


class CLI:

    def __init__(self, data_system: DataSystem):
        self.data_system = data_system

    def run(self):

        while True:
            try:
                val = input('> ')
                command, *args = val.strip().split(' ')
                print(f'{command=}, {args=}')

                if command not in COMMANDS:
                    print(f'invalid {command=}')
                elif command == 'quit':
                    break
                elif command == 'print':
                    print(self.data_system)
                elif command == 'tick':
                    symbol, price = args[0], float(args[1])
                    print(self.data_system.tick(symbol=symbol, price=price))
                else:
                    user, symbol = args[0], args[1]
                    currency = args[2] if len(args) > 2 else None

                    if command == 'subscribe':
                        print(self.data_system.subscribe(user=user, stock=symbol, currency=currency))
                    elif command == 'unsubscribe':
                        self.data_system.unsubscribe(user=user, stock=symbol, currency=currency)
                    else:
                        # should not occur.
                        print(f'impossible case - should not occur!')
            # selectively handle custom exceptions.
            except (ValueError, EntitlementError, SubscriptionError) as e:
                print(e)
            except Exception as e:
                print(f'An error occurred: {e}')
                traceback.print_exc()


def main():
    # load config
    config_path = sys.argv[1]
    with open(config_path, 'r') as file:
        config_data = json.load(file)
        print(config_data)

    # build data system instance.
    data_system = DataSystem(config=config_data)
    # attach to cli.
    cli = CLI(data_system=data_system)
    cli.run()


if __name__ == '__main__':
    main()
