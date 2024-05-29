import os
import sys
import shutil
import random
import argparse
import voc_utils as utils

from pathlib import Path


def main(args):

    print(args.path)

    images_train_path = os.path.join(args.path, 'images', 'train')
    if not os.path.exists(images_train_path):
        os.mkdir(images_train_path)

    images_val_path = os.path.join(args.path, 'images', 'val')
    if not os.path.exists(images_val_path):
        os.mkdir(images_val_path)

    labels_train_path = os.path.join(args.path, 'labels', 'train')
    if not os.path.exists(labels_train_path):
        os.mkdir(labels_train_path)

    labels_val_path = os.path.join(args.path, 'labels', 'val')
    if not os.path.exists(labels_val_path):
        os.mkdir(labels_val_path)

    images_path = os.path.join(args.path, 'images')
    files = []
    for _, _, f in os.walk(images_path):
        for file in f:
            if not '.jpg' in file and not '.jpeg' in file and not '.png' in file:
                continue

            files.append(file)

    random.shuffle(files)

    num_train = int(len(files) * args.ratio)

    train_data = files[:num_train]
    val_data = files[num_train:]

    labels_path = os.path.join(args.path, 'labels')
    for f in train_data:
        shutil.move(os.path.join(images_path, f),
                    os.path.join(images_train_path, f))

        txt = Path(f).with_suffix('.txt')
        if os.path.exists(os.path.join(labels_path, txt)):
            shutil.move(os.path.join(labels_path, txt),
                        os.path.join(labels_train_path, txt))

    for f in val_data:
        shutil.move(os.path.join(images_path, f),
                    os.path.join(images_val_path, f))

        txt = Path(f).with_suffix('.txt')
        if os.path.exists(os.path.join(labels_path, txt)):
            shutil.move(os.path.join(labels_path, txt),
                        os.path.join(labels_val_path, txt))


def parse_arguments(argv):

    parser = argparse.ArgumentParser()

    parser.add_argument('--path', type=str, required=True,
                        help='root of VOC development kit')
    parser.add_argument('--ratio', type=float, default=0.8,
                        help='ratio of training data')

    return parser.parse_args(argv)


if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))
