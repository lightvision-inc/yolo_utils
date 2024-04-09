import os
import sys
import argparse
import voc_utils as utils

from os.path import join


def main(args):

    classes = args.classes
    for sub in args.sub_dir:
        path = join(args.root_dir, sub)
        print(path)

        for _, _, f in os.walk(join(path, 'JPEGImages')):
            for file in f:
                if '.jpg' in file or '.jpeg' in file or '.png' in file:
                    print(f' {file}')
                    utils.privacy_protection(path, file, classes)
                    utils.privacy_protection_darkmark(path, file, classes)


def parse_arguments(argv):

    parser = argparse.ArgumentParser()

    parser.add_argument('--root_dir', type=str, required=True
                        help='root of VOC development kit')
    parser.add_argument('--sub_dir', action='append', type=str, required=True
                        help='root of VOC development kit')
    parser.add_argument('--classes', action='append', type=str,
                        help='list of classes for subset', default=['person', 'license_plate'])

    return parser.parse_args(argv)


if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))
