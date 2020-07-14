import os
import sys
import argparse
import voc_utils as utils


def main(args):

    classes = args.classes
    for sub in args.sub_dir:
        path = os.path.join(args.root_dir, sub)

        # remove existing txt files for annotation
        utils.remove_annot_files(path)

        for _, _, f in os.walk(os.path.join(path, 'Annotations')):
            for file in f:
                if '.xml' in file:
                    filename = file.replace('.xml', '')
                    utils.convert_annotation(path, filename, classes)


def parse_arguments(argv):

    parser = argparse.ArgumentParser()

    parser.add_argument('--root_dir', type=str,
                        help='root of VOC development kit', default='E:/VOCdevkit')
    parser.add_argument('--sub_dir', action='append', type=str,
                        help='root of VOC development kit')
    parser.add_argument('--classes', action='append', type=str,
                        help='list of classes for subset')

    return parser.parse_args(argv)


if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))
