import os
import sys
import argparse
import voc_utils as utils

sets = [('2012', 'train'), ('2012', 'val'),
        ('2007', 'train'), ('2007', 'val'), ('2007', 'test')]


def main(args):

    path = args.root_path
    classes = args.classes

    # remove existing txt files for annotation
    for year, _ in sets:
        utils.remove_annot_files(os.path.join(path, 'VOC{}'.format(year)))

    for year, img_set in sets:
        sub_dir = os.path.join(path, 'VOC{}'.format(year))
        img_ids = open(
            '{}/ImageSets/Main/{}.txt'.format(sub_dir, img_set)).read().strip().split()

        for img_id in img_ids:
            utils.convert_annotation(sub_dir, img_id, classes)


def parse_arguments(argv):

    parser = argparse.ArgumentParser()

    parser.add_argument('--root_path', type=str,
                        help='root of VOC development kit', default='E:/VOCdevkit')
    parser.add_argument('--classes', type=str,
                        help='list of classes for subset', default=['car'])

    return parser.parse_args(argv)


if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))
