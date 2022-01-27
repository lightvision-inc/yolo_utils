import sys
import argparse

import matplotlib.pyplot as plt


parser = argparse.ArgumentParser()

parser.add_argument('--list_file', type=str,
                    help='file that contains a list of annotated images')

args = parser.parse_args(sys.argv[1:])

x = []
with open(args.list_file) as f:
    for l in f.readlines():
        l = l.rstrip()

        if '.jpg' or '.png' in l:
            l = l.replace('.jpg', '.txt')
            l = l.replace('.png', '.txt')
            skip = True
            with open(l) as txt_file:
                for annot in txt_file:
                    idx, _, _, _, _ = annot.split()
                    x.append(int(idx))
        else:
            print('Txt annotation file is not available')

plt.hist(x=x, bins=max(x) - min(x) + 1)
plt.show()
