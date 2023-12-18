
import argparse
import yaml

from model import Job, Step


def read_input(input_file: str) -> list[dict]:
    print(f'reading {input_file=}')
    with open(input_file, mode='r') as infile:
        data = yaml.safe_load(infile)
    print(f'{data=}')
    return data


def write_output(output_file: str, schedule: list[str]) -> None:
    print(f'writing {output_file=}')
    with open(output_file, mode='w+') as outfile:
        for step_id in schedule:
            outfile.write(f'{step_id}\n')


def run(input_file: str) -> None:
    # takes yaml input, constructs Steps & Job, generate schedule output.
    input_data = read_input(input_file)
    job = Job(steps=[Step(**data) for data in input_data])
    print(f'constructed {job=}')
    schedule = job.generate_schedule()
    print(f'generated {schedule=}')
    write_output(output_file=output_file, schedule=schedule)


def prompt():
    '''
    Input prompt to retrieve parameters.

    e.g> python scheduler.py path_to_input_yaml path_to_output_file
    '''

    parser = argparse.ArgumentParser(description='Scheduler')
    # parser.add_argument('-i', '--input_file', type=str, required=True, help='full path to input yaml file')
    # parser.add_argument('-o', '--output_file', type=str, required=True, help='full path to output file')
    parser.add_argument('input_file', type=str, help='full path to input yaml file')
    parser.add_argument('output_file', type=str, help='full path to output file')
    args = parser.parse_args()
    print(f'received {args=}')
    return args.input_file, args.output_file


# start of the program.
# receive input, output path
# parse input, construct step, job inner constructs
# generate scheduling output.
if __name__ == '__main__':
    print(f'--- Starting Scheduler ---')
    input_file, output_file = prompt()
    run(input_file)
