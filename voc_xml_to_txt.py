import os
import sys
import shutil
import argparse
import voc_utils as utils

from pathlib import Path


def main(args):

    print(args.path)

    images_path = os.path.join(args.path, 'images')
    if not os.path.exists(images_path):
        os.mkdir(images_path)

    labels_path = os.path.join(args.path, 'labels')
    if not os.path.exists(labels_path):
        os.mkdir(labels_path)

    jpeg_path = os.path.join(args.path, 'JPEGImages')
    for _, _, f in os.walk(jpeg_path):
        for file in f:
            if not '.jpg' in file and not '.jpeg' in file and not '.png' in file:
                continue

            filename = Path(file).stem
            print(filename)
            utils.convert_annotation(args.path, filename, args.classes)

            shutil.copy(os.path.join(jpeg_path, file),
                        os.path.join(images_path, file))


def parse_arguments(argv):

    parser = argparse.ArgumentParser()

    parser.add_argument('--path', type=str, required=True,
                        help='root of VOC development kit')
    parser.add_argument('--classes', action='append', type=str,
                        help='list of classes for subset')

    return parser.parse_args(argv)


if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))
