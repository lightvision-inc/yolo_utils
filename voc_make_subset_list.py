import os
import sys
import argparse


def main(args):
    path = args.root_path + '/{}/JPEGImages/'
    img_path = []

    for sub in args.sub_dir:
        for _, _, f in os.walk(path.format(sub)):
            for file in f:
                if '.txt' in file:
                    file = file.replace('.txt', '.{}'.format(args.img_ext))
                    img_path.append(path.format(sub) + file)

    with open('voc_subset.txt', 'w+') as f:
        for p in img_path:
            f.write(p + '\n')


def parse_arguments(argv):
    parser = argparse.ArgumentParser()

    parser.add_argument('--root_path', type=str,
                        help='root of VOC development kit', default='E:/VOCdevkit')
    parser.add_argument('--sub_dir', type=str,
                        help='list of target VOC datasets', default=['VOC2007', 'VOC2012'])
    parser.add_argument('--img_ext', type=str,
                        help='extension of image files', default='jpg')

    return parser.parse_args(argv)


if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))
