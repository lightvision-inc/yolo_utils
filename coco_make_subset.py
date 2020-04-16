import os
import sys
import glob
import json
import shutil
import argparse
import matplotlib.pyplot as plt


def remove_annot_files(path):
    img_list = glob.glob('{}/*.txt'.format(path))
    for img in img_list:
        try:
            os.remove(img)
        except:
            print('unable to delete: ' + img)


def main(args):
    annot_path = os.path.join(args.root_path, 'annotations')
    img_path = os.path.join(args.root_path, args.stage + '2017')

    remove_annot_files(img_path)

    with open(os.path.join(annot_path, 'instances_' + args.stage + '2017.json')) as f:
        data = json.load(f)

    annot = data['annotations']

    img_info = {}
    iw = 0
    ih = 0

    for a in annot:
        cid = a['category_id']
        label = 0
        if cid in args.category_ids:
            if not args.assign_one_label:
                label = args.category_ids.index(cid)
        else:
            continue

        bw = a['bbox'][2]
        bh = a['bbox'][3]
        cx = a['bbox'][0] + bw / 2
        cy = a['bbox'][1] + bh / 2

        iid = a['image_id']

        if iid in img_info:
            iw = img_info[iid][0]
            ih = img_info[iid][1]
        else:
            img = plt.imread('{}/{:012d}.jpg'.format(img_path, iid))
            iw = img.shape[1]
            ih = img.shape[0]
            img_info[iid] = (iw, ih)

        with open('{}/{:012d}.txt'.format(img_path, iid), 'a+') as f:
            f.write('{} {:f} {:f} {:f} {:f}\n'.format(
                label, cx / iw, cy / ih, bw / iw, bh / ih))


def parse_arguments(argv):
    parser = argparse.ArgumentParser()

    parser.add_argument('--stage', type=str,
                        help='either train or val', default='val')
    parser.add_argument('--root_path', type=str,
                        help='root of COCO dataset', default='E:/coco')
    parser.add_argument('--category_ids', type=int,
                        help='list of category ids for subset', default=[3, 6, 8])
    parser.add_argument('--assign_one_label', type=bool,
                        help='assign identical labels (0, zero) for subset', default=True)

    return parser.parse_args(argv)


if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))
