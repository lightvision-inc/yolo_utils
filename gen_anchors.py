'''
Created on Feb 20, 2017

@author: jumabek
'''
from os.path import join
import argparse
import numpy as np
import sys
import os
import random


def iou(x, centroids):
    w, h = x
    ious = []
    for centroid in centroids:
        cw, ch = centroid
        if cw >= w and ch >= h:
            iou = w * h / (cw * ch)
        elif cw >= w and ch <= h:
            iou = w * ch / (w * h + (cw - w) * ch)
        elif cw <= w and ch >= h:
            iou = cw * h / (w * h + cw * (ch - h))
        else:  # means both w,h are bigger than c_w and c_h respectively
            iou = (cw * ch) / (w * h)
        ious.append(iou)  # will become (k,) shape
    return np.array(ious)


def avg_iou(x, centroids):
    n, _ = x.shape
    sum = 0
    for i in range(n):
        # note IOU() will return array which contains IoU for each centroid and X[i] // slightly ineffective, but I am too lazy
        sum += max(iou(x[i], centroids))
    return sum / n


def write_anchors_to_file(x, centroids, anchor_file, input_width, input_height):
    with open(anchor_file, 'w') as f:
        anchors = centroids.copy()
        print(anchors.shape)

        for i in range(anchors.shape[0]):
            anchors[i][0] *= input_width
            anchors[i][1] *= input_height

        widths = anchors[:, 0]
        sorted_indices = np.argsort(widths)

        print(f'anchors = {anchors[sorted_indices]}')

        for i in sorted_indices[:-1]:
            f.write('%0.2f,%0.2f, ' % (anchors[i, 0], anchors[i, 1]))

        # there should not be comma after last anchor, that's why
        f.write('%0.2f,%0.2f\n' %
                (anchors[sorted_indices[-1:], 0], anchors[sorted_indices[-1:], 1]))

        f.write('%f\n' % (avg_iou(x, centroids)))
        print()


def kmeans(x, centroids, anchor_file, input_width, input_height):
    n = x.shape[0]
    k, dim = centroids.shape

    prev_assignments = np.ones(n) * (-1)
    old_dists = np.zeros((n, k))
    iter = 0

    while True:
        iter += 1

        dists = []
        for i in range(n):
            d = 1 - iou(x[i], centroids)
            dists.append(d)
        dists = np.array(dists)

        print(f'iter {iter}: dists = {np.sum(np.abs(old_dists - dists))}')

        # assign samples to centroids
        assignments = np.argmin(dists, axis=1)

        if (assignments == prev_assignments).all():
            print(f'centroids = {centroids}')
            write_anchors_to_file(x, centroids, anchor_file,
                                  input_width, input_height)
            return

        # calculate new centroids
        centroid_sums = np.zeros((k, dim), np.float64)
        for i in range(n):
            centroid_sums[assignments[i]] += x[i]

        for i in range(k):
            centroids[i] = centroid_sums[i] / (np.sum(assignments == i))

        prev_assignments = assignments.copy()
        old_dists = dists.copy()


def main(args):
    if not os.path.exists(args.output_dir):
        os.mkdir(args.output_dir)

    annot_dims = []
    with open(args.txt_file) as f1:
        lines = [line.rstrip('\n') for line in f1.readlines()]
        for line in lines:
            line = line.replace('.jpg', '.txt')
            line = line.replace('.png', '.txt')
            print(line)
            with open(line) as f2:
                for line in f2.readlines():
                    line = line.rstrip('\n')
                    w, h = line.split(' ')[3:]
                    # print(w, h)
                    annot_dims.append(tuple(map(float, (w, h))))
    annot_dims = np.array(annot_dims)

    if args.num_clusters == 0:
        for num_clusters in range(1, 11):  # we make 1 through 10 clusters
            anchor_file = join(
                args.output_dir, f'anchors{num_clusters}.txt')

            indices = [random.randrange(annot_dims.shape[0])
                       for _ in range(num_clusters)]
            centroids = annot_dims[indices]
            kmeans(annot_dims, centroids, anchor_file,
                   args.input_width, args.input_height)
            print('centroids.shape', centroids.shape)
    else:
        anchor_file = join(args.output_dir, f'anchors{args.num_clusters}.txt')
        indices = [random.randrange(annot_dims.shape[0])
                   for _ in range(args.num_clusters)]
        centroids = annot_dims[indices]
        kmeans(annot_dims, centroids, anchor_file,
               args.input_width, args.input_height)
        print('centroids.shape', centroids.shape)


def parse_arguments(argv):

    parser = argparse.ArgumentParser()

    parser.add_argument('--txt_file', help='Path to a txt file')
    parser.add_argument('--output_dir', default='anchors',
                        type=str, help='Output directory for saving anchors')
    parser.add_argument('--num_clusters', default=0, type=int,
                        help='Number of clusters')
    parser.add_argument('--input_width', default=416, type=int,
                        help='Number of clusters')
    parser.add_argument('--input_height', default=416, type=int,
                        help='Number of clusters')

    return parser.parse_args(argv)


if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))
