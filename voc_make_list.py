import os
import sys
import argparse


def main(args):

    path = args.root_dir + '/{}/JPEGImages/'
    for sub in args.sub_dir:
        img_path = []
        for _, _, f in os.walk(path.format(sub)):
            for file in f:
                if '.txt' in file:
                    file = file.replace('.txt', '.{}'.format(args.img_ext))
                    img_path.append(path.format(sub) + file)

        with open('{}.txt'.format(sub), 'w+') as f:
            for p in img_path:
                f.write(p + '\n')


def parse_arguments(argv):

    parser = argparse.ArgumentParser()

    parser.add_argument('--root_dir', type=str,
                        help='root of VOC development kit', default='E:/VOCdevkit')
    parser.add_argument('--sub_dir', action='append', type=str,
                        help='list of target VOC datasets')
    parser.add_argument('--img_ext', type=str,
                        help='extension of image files')

    return parser.parse_args(argv)


if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))
