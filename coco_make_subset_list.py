import os
import sys
import argparse


def main(args):
    img_path = os.path.join(args.root_dir, args.stage + '2017')
    txt_path = []
    for _, _, f in os.walk(img_path):
        for file in f:
            if '.txt' in file:
                file = file.replace('.txt', '.jpg')
                txt_path.append(os.path.join(img_path, file))

    with open('coco_' + args.stage + '_subset.txt', 'w+') as f:
        for p in txt_path:
            f.write(p + '\n')


def parse_arguments(argv):
    parser = argparse.ArgumentParser()

    parser.add_argument('--stage', type=str,
                        help='either train or val', default='val')
    parser.add_argument('--root_dir', type=str,
                        help='root of COCO dataset', default='E:/coco')

    return parser.parse_args(argv)


if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))
