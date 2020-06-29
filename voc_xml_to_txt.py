import os
import sys
import argparse
import voc_utils as utils


def main(args):

    path = args.root_path
    classes = args.classes

    # remove existing txt files for annotation
    utils.remove_annot_files(path)

    for _, _, f in os.walk(os.path.join(path, 'Annotations')):
        for file in f:
            if '.xml' in file:
                filename = file.replace('.xml', '')
                utils.convert_annotation(path, filename, classes)


def parse_arguments(argv):

    parser = argparse.ArgumentParser()

    parser.add_argument('--root_path', type=str,
                        help='root of VOC development kit', default='E:/VOCdevkit/VOC2020')
    parser.add_argument('--classes', type=str,
                        help='list of classes for subset', default=['car'])

    return parser.parse_args(argv)


if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))
