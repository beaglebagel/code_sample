import csv


class Loan:
    '''
    Loan class.
    '''

    def __init__(self, id, interest_rate, default_likelihood, amount, state):
        '''
        :param id: str, loan id
        :param interest_rate: float, interest rate
        :param default_likelihood: float, default likelihood
        :param amount: int, amount
        :param state: str, state code
        id: facility if only if assigned
        '''
        self.id = id
        self.interest_rate = interest_rate
        self.default_likelihood = default_likelihood
        self.amount = amount
        self.state = state
        self.facility_id = None

    def __repr__(self):
        return (
                f'Loan [id:{self.id}, '
                f'interest_rate:{self.interest_rate}, '
                f'default_likelihood:{self.default_likelihood}, '
                f'amount:{self.amount}, '
                f'state:{self.state}]'
        )

    @staticmethod
    def load(file):
        '''
         Load plain Loans objects from the input file.

        :param file: path to loans.csv
        '''
        loan_dict = csv.DictReader(open(file, mode='r'))
        loans = []

        for line in loan_dict:
            loan = Loan(id=line['id'],
                        amount=int(line['amount']),
                        interest_rate=float(line['interest_rate']),
                        default_likelihood=float(line['default_likelihood']),
                        state=line['state'])
            loans.append(loan)

        return loans
