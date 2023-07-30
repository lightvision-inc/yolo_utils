import os
import sys
import argparse
import voc_utils as utils


def main(args):

    classes = args.classes
    for sub in args.sub_dir:
        path = os.path.join(args.root_dir, sub)
        print(path)

        for _, _, f in os.walk(os.path.join(path, 'JPEGImages')):
            for file in f:
                if '.jpg' in file or '.jpeg' in file or '.png' in file:
                    utils.privacy_protection(path, file, classes)


def parse_arguments(argv):

    parser = argparse.ArgumentParser()

    parser.add_argument('--root_dir', type=str,
                        help='root of VOC development kit', default='D:/230720_annotation_VN_data')
    parser.add_argument('--sub_dir', action='append', type=str,
                        help='root of VOC development kit', default=['camera_1', 'camera_2', 'camera_3', 'camera_4', 'camera_5', 'camera_6', 'camera_7', 'camera_8', 'camera_9', 'camera_10', 'camera_11', 'camera_13', 'camera_14', 'camera_15'])
    parser.add_argument('--classes', action='append', type=str,
                        help='list of classes for subset', default=['person'])

    return parser.parse_args(argv)


if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))
