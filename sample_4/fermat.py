import sys
import argparse

from itertools import combinations_with_replacement, product


def write(output_file, result_iterator):
    '''
    Simple output writer from result iterator.

    :param output_file: output file name to write out.
    :param result_iterator: iterator containing result strings.
    '''

    try:
        # overwrite previous file if exists.
        with open(output_file, 'w') as of:
            for result in result_iterator:
                of.write(result + '\n')

    except Exception as e:
        print(e)

    print('Generated {}'.format(output_file))


def evaluate(exponent_limit, base_limit, precalculation):
    '''
    generates evaluation results in stream.

    :param exponent_limit: allowed exponent range: between 3 and exponent_limit-1.
    :param base_limit: allowed a,b,c range: between 1 and base_limit-1.
    :param precalculation: storage containing pre-calculated base^exponent.
    :return: single iteration of evaluation.
    '''

    for e in range(3, exponent_limit):
        # generate unique a,b,c triplets each < base_limit.
        for combo in product(
                combinations_with_replacement(range(1, base_limit), 2),
                range(1, base_limit)):
            # unpack ((a,b), c) pairs.
            a, b, c = *combo[0], combo[1]
            result = ((precalculation[(a, e)] + precalculation[(b, e)]) == precalculation[(c, e)])
            yield '{}^{} + {}^{} == {}^{} = {}'.format(a, e, b, e, c, e, result)


def power(base, exponent, precalculation):
    '''
    Calculate base ^ exponent in O(log 2 of exponent) time.

    :param base: base assumed to be > 2.
    :param exponent: assumed to be >= 0.
    :param precalculation: map to store base^exponent results.
    :return: base^exponent.
    '''

    # base cases of exponent 0 & 1.
    if exponent == 0:
        return 1
    elif exponent == 1:
        return base
    # check existence of (base, exponent).
    elif (base, exponent) in precalculation:
        return precalculation[(base, exponent)]

    # if exponent is odd, take one base aside, and continue with base^2 & exponent/2.
    if exponent & 1 == 1:
        result = base * power(base * base, exponent // 2, precalculation)
    # exponent is even, continue with base^2 & exponent/2.
    else:
        result = power(base * base, exponent // 2, precalculation)
    precalculation[(base, exponent)] = result
    return result


def precalculate(exponent_limit, base_limit):
    '''
    Pre-calculate all possible (a,b,c) ^ n in dictionary for simple lookup later on.

    :param exponent_limit: allowed exponent range: between 3 and exponent_limit-1.
    :param base_limit: allowed a,b,c range: between 1 and base_limit-1.
    :return: dict: pre-calculated map of (base, exponent) -> value.
    '''
    precalculation = {}

    for base in range(1, base_limit):
        for exponent in range(3, exponent_limit):
            # power routine start.
            power(base, exponent, precalculation)

    return precalculation


def prompt():
    '''
    Prompt to take n, abc.
    :return: n, abc.
    '''

    parser = argparse.ArgumentParser(description='Fermat Solver')
    required_arguments = parser.add_argument_group('required arguments')
    required_arguments.add_argument('-n', '--n', help='max exponent value exclusive..')
    required_arguments.add_argument('-abc', '--abc', help='limit of a,b,c values exclusive..')
    args = parser.parse_args(args=None if sys.argv[1:] else ['-h'])
    n, abc = int(args.n), int(args.abc)

    # quick input validation.
    if n <= 2:
        raise ValueError('broken input condition, n > 2, n:{}'.format(n))
    if abc <= 1:
        raise ValueError('broken input condition, abc > 1, abc:{}'.format(abc))

    return n, abc


if __name__ == '__main__':
    '''
    Program to evaluate a^n + b^n = c^n fermat law.
    
    Written and tested with Python 3.6.8.
    
    Run ex> python fermat.py -n 12345 -abc 10
    
    output.txt will be generated in the same folder as the script.
    '''
    n, abc = prompt()
    print('Input n:{}, abc:{}'.format(n, abc))

    # 1. pre-calculate a,b,c ^ n values.
    precalculation = precalculate(n, abc)

    # 2. generate 3-value tuple (a, b, c) combos and evaluation results of a^n + b^n == c^n.
    result_iterator = evaluate(exponent_limit=n, base_limit=abc, precalculation=precalculation)

    # 3. write result out.
    write(output_file='output.txt', result_iterator=result_iterator)
