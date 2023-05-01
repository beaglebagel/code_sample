import csv


class Covenant:
    '''
    Covenant class.
    '''

    def __init__(self, bank_id, facility_id=None, maximum_default_likelihood=0.0, banned_state=None):
        '''
        bank_id: str, bank id
        facility_id: str, facility id
        maximum_default_likelihood: float, max_default_likelihood
        banned_states: set{}, set of banned state codes
        '''
        self.bank_id = bank_id
        self.facility_id = facility_id
        self.maximum_default_likelihood = maximum_default_likelihood
        self.banned_state = banned_state

    def check(self, default_likelihood, state):
        '''
        loan criteria check under covenant.
        :param default_likelihood: float,
        :param state: str, state code

        :return: bool, pass / fail
        '''
        if self.maximum_default_likelihood and default_likelihood > self.maximum_default_likelihood:
            return False
        if state == self.banned_state:
            return False
        return True

    def __repr__(self):
        return 'Covenant [bank_id:{}, facility_id:{}, maximum_default_likelihood:{}, banned_states:{}]'.format(
            self.bank_id,
            self.facility_id,
            self.maximum_default_likelihood,
            self.banned_state
        )

    @staticmethod
    def load(file):
        '''
        load covenants, normalize back per available criteria & allocate to facility.

        :param file: path to covenants.csv
        '''
        covenant_dict = csv.DictReader(open(file, mode='r'))

        covenants = []
        for line in covenant_dict:
            covenants.append(Covenant(bank_id=line['bank_id'],
                                      facility_id=line['facility_id'],
                                      maximum_default_likelihood=float(line['max_default_likelihood'] or 0),
                                      banned_state=line['banned_state']))

        return covenants
