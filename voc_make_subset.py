import os
import sys
import glob
import pickle
import argparse
import xml.etree.ElementTree as ET

sets = [('2012', 'train'), ('2012', 'val'),
        ('2007', 'train'), ('2007', 'val'), ('2007', 'test')]


def remove_annot_files(path, year):
    img_list = glob.glob('{}/VOC{}/JPEGImages/*.txt'.format(path, year))
    for img in img_list:
        try:
            os.remove(img)
        except:
            print('unable to delete: ' + img)


def convert(size, box):
    dw = 1.0 / (size[0])
    dh = 1.0 / (size[1])
    x = (box[0] + box[1]) / 2.0 - 1
    y = (box[2] + box[3]) / 2.0 - 1
    w = box[1] - box[0]
    h = box[3] - box[2]
    x = x * dw
    w = w * dw
    y = y * dh
    h = h * dh
    return (x, y, w, h)


def convert_annotation(path, year, img_id, classes):
    in_file = open(
        '{}/VOC{}/Annotations/{}.xml'.format(path, year, img_id))
    tree = ET.parse(in_file)
    root = tree.getroot()
    size = root.find('size')
    w = int(size.find('width').text)
    h = int(size.find('height').text)

    for obj in root.iter('object'):
        difficult = obj.find('difficult').text
        c = obj.find('name').text
        if c not in classes or int(difficult) == 1:
            continue

        cid = classes.index(c)
        xmlbox = obj.find('bndbox')
        b = (float(xmlbox.find('xmin').text), float(xmlbox.find('xmax').text), float(
            xmlbox.find('ymin').text), float(xmlbox.find('ymax').text))
        bb = convert((w, h), b)

        out_file = open(
            '{}/VOC{}/JPEGImages/{}.txt'.format(path, year, img_id), 'a+')
        out_file.write('{} {:f} {:f} {:f} {:f}\n'.format(
            cid, bb[0], bb[1], bb[2], bb[3]))


def main(args):
    path = args.root_path
    classes = args.classes

    # remove existing txt files for annotation
    remove_annot_files(path, 2007)
    remove_annot_files(path, 2012)

    for year, img_set in sets:
        img_ids = open(
            '{}/VOC{}/ImageSets/Main/{}.txt'.format(path, year, img_set)).read().strip().split()

        for img_id in img_ids:
            convert_annotation(path, year, img_id, classes)


def parse_arguments(argv):
    parser = argparse.ArgumentParser()

    parser.add_argument('--root_path', type=str,
                        help='root of VOC development kit', default='E:/VOCdevkit')
    parser.add_argument('--classes', type=str,
                        help='list of classes for subset', default=['car'])

    return parser.parse_args(argv)


if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))
