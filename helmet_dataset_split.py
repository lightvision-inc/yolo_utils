import os
import sys
import argparse
import pandas as pd

from os.path import join


def main(args):

    df = pd.read_csv(join(args.root_dir, 'data_split.csv'))
    stage = ['training', 'validation', 'test']
    for s in stage:
        with open(f'helmet_dataset_{s}.txt', 'w+') as fs:
            for _, data in df[df.Set == s].iterrows():
                for _, _, f in os.walk(join(args.root_dir, 'image', data.video_id)):
                    for file in f:
                        if '.txt' not in file:
                            continue
                        file.replace('.txt', '.jpg')
                        fs.write(
                            join(args.root_dir, 'image', data.video_id, file) + '\n')


def parse_arguments(argv):

    parser = argparse.ArgumentParser()

    parser.add_argument('--root_dir', type=str,
                        help='root of VOC development kit', default='D:\\dataset\\helmet_dataset')

    return parser.parse_args(argv)


if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))
