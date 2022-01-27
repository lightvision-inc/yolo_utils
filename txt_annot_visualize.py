import sys
import argparse
import keyboard

import cv2
import draw_utils as utils


parser = argparse.ArgumentParser()

parser.add_argument('--list_file', type=str,
                    help='file that contains a list of annotated images')
parser.add_argument('--name_file', type=str,
                    help='file that contains a list of class names')

args = parser.parse_args(sys.argv[1:])

draw_annot = True
names = None
if args.name_file is not None:
    with open(args.name_file) as f:
        names = [l.rstrip() for l in f.readlines()]
else:
    print('Name file is not available')

with open(args.list_file) as f:
    for l in f.readlines():
        l = l.rstrip()
        img = cv2.imread(l)
        utils.draw_file_path(img, l)

        iw = img.shape[1]
        ih = img.shape[0]

        if '.jpg' or '.png' in l:
            l = l.replace('.jpg', '.txt')
            l = l.replace('.png', '.txt')
            skip = True
            with open(l) as txt_file:
                for annot in txt_file:
                    idx, cx, cy, bw, bh = annot.split()
                    cx = float(cx) * iw
                    cy = float(cy) * ih
                    bw = float(bw) * iw
                    bh = float(bh) * ih
                    tl = (int(cx - bw / 2), int(cy - bh / 2))
                    br = (int(cx + bw / 2), int(cy + bh / 2))
                    if int(idx) == 68:
                        skip = False
                    if draw_annot:
                        if names is not None:
                            utils.draw_annot(img, names[int(idx)], tl, br)
                        else:
                            utils.draw_annot(img, idx, tl, br)
        else:
            print('Txt annotation file is not available')

        cv2.imshow('visualize', img)
        key = cv2.waitKey(0)

        if key == ord('q'):
            break
