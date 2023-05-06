import argparse
import os
import heapq
import sys


class MergeIterator:
    '''
    MergeIterator: takes file lists, constructs file handle mapping and merge sorts the lines until exhausted.
    '''
    def __init__(self, files):
        self.files = files
        self.file_handles = {}
        self.heap = []
        self.last_line = ''
        self.last_read = {}

        for i, file in enumerate(self.files):
            print(f'Iterator opening file[{i}]: {file}')
            self.file_handles[i] = open(file, 'r')
            self.last_read[i] = ''

        # initialize heap.
        for i, fh in self.file_handles.items():
            while True:
                line = fh.readline().strip()
                if not line:
                    continue
                print(f'Adding first line of file[i]: {line}')
                self.heap.append((line, i))
                break

        # create initial heap from n input files.
        heapq.heapify(self.heap)

    def __iter__(self):
        return self

    def next(self) -> str:
        if not self.heap:
            raise StopIteration('End of Iterator reached!')

        # fetch next line & file index from heap.
        line, i = heapq.heappop(self.heap)

        # check if we received unsorted input file excluding whitespace.
        if self.last_read[i] > line:
            raise ValueError(f'Input File not sorted! index:{i} [{self.last_read[i]}] followed by [{line}]')

        # get appropriate file handle.
        fh = self.file_handles[i]
        # keep fetching next until we get non empty line or
        while True:
            # check whether end of file reached.
            before = fh.tell()
            next_line = fh.readline().strip()
            after = fh.tell()

            # reached the file end?
            if before == after:
                self.file_handles[i].close()
                break
            elif next_line:
                # save the last read line for next comparison.
                self.last_read[i] = line
                # push next line to heap.
                heapq.heappush(self.heap, (next_line, i))
                break
            # we read empty line, read again.
            elif not next_line:
                continue

        # set last line
        self.last_line = line
        return line


def write(output_file, merge_iterator) -> None:
    '''
    Generates full output path with items from merge iterator.
    @Note: Skip the duplicate outputs by itself.

    :param output_file: full output path to write merged output to.
    :param merge_iterator: merge sort iterator
    :return: generates merged output file.
    '''
    last_written = ''

    try:
        # overwrite previous file if exists.
        with open(output_file, 'w') as of:
            while True:
                line = merge_iterator.next()
                # skip duplicate lines
                if last_written == line:
                    continue
                last_written = line
                of.write(line+'\n')

    except Exception as e:
        print(e)

    print(f'Generated {output_file}')


def get_files(input_dir) -> list:
    '''
    Basic input file list gatherer.
    '''
    return [os.path.join(input_dir, file) for file in os.listdir(input_dir)]


def prompt():
    '''
    Prompt to take input files dir & output file path(both required).
    :return: input dir path, output file path
    '''

    parser = argparse.ArgumentParser(description='Merge Sort Program')
    required_arguments = parser.add_argument_group('required arguments')
    required_arguments.add_argument('-i', '--input_dir', help='Input file directory')
    required_arguments.add_argument('-o', '--output_file', help='Full path to output file')
    args = parser.parse_args(args=None if sys.argv[1:] else ['-h'])
    input_dir, output_file = args.input_dir, args.output_file

    # minor input validation.
    if not os.path.exists(input_dir):
        raise ValueError('Invalid input dir {}'.format(input_dir))
    if not os.path.exists(os.path.dirname(output_file)):
        raise ValueError('Invalid output dir {}'.format(os.path.dirname(output_file)))

    return input_dir, output_file


if __name__ == '__main__':
    input_dir, output_file = prompt()
    print(f'Read input_dir {input_dir}, output_file {output_file}')
    # Gather files.
    files = get_files(input_dir)
    print(f'Processing {files}')
    # make Merge Iterator.
    mi = MergeIterator(files)
    # write merged file.
    write(output_file, mi)
