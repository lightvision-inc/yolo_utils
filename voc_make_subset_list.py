import os
import sys
import argparse


def main(args):
    path = args.root_path + '/VOC{}/JPEGImages'
    img_path = []

    for year in args.years:
        for _, _, f in os.walk(path.format(year)):
            for file in f:
                if '.txt' in file:
                    file = file.replace('.txt', '.jpg')
                    img_path.append(os.path.join(path.format(year), file))

    with open('voc_subset.txt', 'w+') as f:
        for p in img_path:
            f.write(p + '\n')


def parse_arguments(argv):
    parser = argparse.ArgumentParser()

    parser.add_argument('--root_path', type=str,
                        help='root of VOC development kit', default='E:/VOCdevkit')
    parser.add_argument('--years', type=int,
                        help='target years for VOC datasets', default=[2007, 2012])

    return parser.parse_args(argv)


if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))
