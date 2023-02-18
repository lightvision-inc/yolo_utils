import os
import sys
import argparse
import pandas as pd

from os.path import join


def main(args):

    sub_dirs = os.listdir(join(args.root_dir, 'image'))
    for sub in sub_dirs:
        print(sub)
        df = pd.read_csv(join(args.root_dir, 'annotation', sub + '.csv'))

        for _, _, f in os.walk(join(args.root_dir, 'image', sub)):
            for file in f:
                if '.jpg' not in file:
                    continue

                filename, _ = os.path.splitext(file)
                mask = df.frame_id == int(filename)
                with open(join(args.root_dir, 'image', sub, filename + '.txt'), 'w+') as fs:
                    for _, data in df[mask].iterrows():
                        cx = (data.x + data.w / 2) / 1920
                        cy = (data.y + data.h / 2) / 1080
                        w = data.w / 1920
                        h = data.h / 1080
                        fs.write(f'0 {cx} {cy} {w} {h}\n')


def parse_arguments(argv):

    parser = argparse.ArgumentParser()

    parser.add_argument('--root_dir', type=str,
                        help='root of VOC development kit', default='D:\\dataset\\helmet_dataset')

    return parser.parse_args(argv)


if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))
