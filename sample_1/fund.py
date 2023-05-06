#!/usr/bin/env python

import argparse
import os
import sys
import heapq
from collections import defaultdict

from facility import Facility
from covenant import Covenant
from loan import Loan


def write(file_dir, file_name, header, data_list):
    '''
    output file write routine.

    :param file_dir: str,
    :param file_name: str,
    :param header: str, csv
    :param data_list: expect this to be list of list.
    '''

    path = os.path.join(file_dir, file_name)
    with open(path, 'w') as fh:
        # header
        fh.write(header + '\n')
        for data in data_list:
            fh.write('{}\n'.format(','.join(data)))
    print(f'Wrote: {path}')


def find_facility(loan, facilities, covenant_map):
    '''
    find the facility this loan can be assigned to.
    facility with lowest interest rate is prioritized during matching process
    as far as loan complies under covenant.

    :param loan: Loan object to assign.
    :param facilities: available facilities list sorted by interest rate(lowest first) and id(lowest first).
    :param covenant_map: map of (bank id, facility id) -> [covenant ... ]
    :return assignable Facility object.
    '''

    backlogs = []
    assigned_facility = None

    # find candidate facility(with lowest interest rate remaining) to assign.
    while facilities:

        cheapest_facility = heapq.heappop(facilities)

        # first check whether cheapest facility can handle loan amount.
        if loan.amount > cheapest_facility.amount:
            # can't handle, add to back log and process next.
            backlogs.append(cheapest_facility)
            continue

        # get bank-level & bank+facility level covenants list.
        covenants = covenant_map.get((cheapest_facility.bank_id,), []) + \
                    covenant_map.get((cheapest_facility.bank_id, cheapest_facility.id), [])

        # check against all covenant conditions.
        passes_covenants = all([cv.check(loan.default_likelihood, loan.state) for cv in covenants])
        # assignable?
        if passes_covenants:
            # we found facility to assign loan to.
            assigned_facility = cheapest_facility
            # subtract loan amount
            cheapest_facility.amount -= loan.amount
            # push back if facility has any amount left.
            if cheapest_facility.amount > 0:
                backlogs.append(cheapest_facility)
            break
        else:
            # can't assign, keep the popped facility.
            backlogs.append(cheapest_facility)

    # add back failed to match facilities back.
    for backlog in backlogs:
        heapq.heappush(facilities, backlog)

    return assigned_facility


def process_covenants(covenants):
    '''
    process covenants & facilities to construct (bank id, facility id) -> [covenants list] mapping.
    keys are defined in either bank-level or bank+facility level.
    (covenant without facility id applies to entire bank)

    :param covenants, list of covenants
    :return dict, (bank id, facility id) -> [covenants list] mapping.
    '''

    covenant_map = defaultdict(list)

    for covenant in covenants:
        covenant_map[(covenant.bank_id, covenant.facility_id)].append(covenant)

    return covenant_map


def get_files(input_dir):
    '''
    Basic input file list gatherer.
    :return: dict, returns filename to file path info.
    '''
    return {file: os.path.join(input_dir, file) for file in os.listdir(input_dir)}


def prompt():
    '''
    Prompt to take input files dir.
    :return: input dir path, output file path (e.g. large/small).
    '''

    parser = argparse.ArgumentParser(description='Loan Assignment Program')
    required_arguments = parser.add_argument_group('required arguments')
    required_arguments.add_argument('-d', '--file_dir', help='Input/Output file directory')
    args = parser.parse_args(args=None if sys.argv[1:] else ['-h'])
    file_dir = args.file_dir

    # minor input validation.
    if not os.path.exists(file_dir) :
        raise ValueError('Invalid dir {}'.format(file_dir))

    return file_dir


if __name__ == '__main__':

    file_dir = prompt()
    print(f'Reading files from {file_dir}')

    # Collect input files.
    file_dict = get_files(input_dir=file_dir)

    # load facilities
    facilities = Facility.load(file=file_dict['facilities.csv'])

    # load covenants
    covenants = Covenant.load(file=file_dict['covenants.csv'])

    # load loans
    loans = Loan.load(file=file_dict['loans.csv'])

    # process covenants
    covenant_map = process_covenants(covenants=covenants)

    # sort the facilities first.
    heapq.heapify(facilities)

    assignments = []

    # process each loans.
    for loan in loans:
        facility = find_facility(loan=loan, facilities=facilities, covenant_map=covenant_map)
        if facility is not None:
            assignments.append([loan.id, facility.id])
            facility.loans.append(loan)
        else:
            assignments.append([loan.id, ''])

    # write result
    write(file_dir=file_dir, file_name='assignments.csv',
          header='loan_id,facility_id',
          data_list=sorted(assignments, key=lambda x: int(x[0])))

    # write yields
    yields = [(facility.id, str(facility.get_yield())) for facility in facilities]
    write(file_dir=file_dir, file_name='yields.csv',
          header='facility_id,expected_yield',
          data_list=sorted(yields, key=lambda x: int(x[0])))
