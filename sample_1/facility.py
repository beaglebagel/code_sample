import csv


class Facility:
    '''
    Facility class.
    '''

    def __init__(self, id, bank_id, interest_rate, amount):
        '''
        :param id: str, facility id
        :param bank_id: str, bank id
        :param interest_rate: float, interest rate
        :param amount: float, amount
        '''
        self.id = id
        self.bank_id = bank_id
        self.interest_rate = interest_rate
        self.amount = amount
        self.covenant = None
        self.loans = []

    def get_yield(self):
        ''' calculate yield across all assigned loans. '''
        combined_yield = 0
        for loan in self.loans:
            combined_yield += ((1 - loan.default_likelihood) * loan.interest_rate * loan.amount -
                               (loan.default_likelihood * loan.amount) -
                               self.interest_rate * loan.amount)
        return round(combined_yield)

    def __repr__(self):
        return (
            f'Facility '
            f'[id:{self.id}, '
            f'bank_id:{self.bank_id}, '
            f'interest_rate:{self.interest_rate}, '
            f'amount: {self.amount}, '
            f'covenant: {self.covenant}, '
            f'loan: {self.loans}]'
        )

    def __lt__(self, other):
        '''
        Determines the order of Facilities using interest_rate & id.

        Facility of interest_rate 1.0 < Facility of interest rate 2.0.
        Facility of id 1 < Facility of id 2.
        Orders are determined by interest_rate and then by id.
        '''
        if self.interest_rate < other.interest_rate:
            return True
        elif self.interest_rate > other.interest_rate:
            return False
        else:
            return self.id < other.id

    @staticmethod
    def load(file):
        '''
        Load plain Facility objects from the input file.

        :param file: path to facilities.csv
        '''

        facility_dict = csv.DictReader(open(file, mode='r'))

        facilities = []
        for line in facility_dict:
            facilities.append(Facility(id=line['id'],
                                       bank_id=line['bank_id'],
                                       interest_rate=float(line['interest_rate']),
                                       amount=float(line['amount'])))
        return facilities
