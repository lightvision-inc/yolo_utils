import os
import glob
import xml.etree.ElementTree as ET


def remove_annot_files(path):

    annot_list = glob.glob(os.path.join(path, 'JPEGImages/*.txt'))
    for annot in annot_list:
        try:
            os.remove(annot)
        except:
            print('unable to delete: ' + annot)


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


def convert_annotation(path, filename, classes):

    in_file = open(
        '{}/Annotations/{}.xml'.format(path, filename))
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
            '{}/JPEGImages/{}.txt'.format(path, filename), 'a+')
        out_file.write('{} {:f} {:f} {:f} {:f}\n'.format(
            cid, bb[0], bb[1], bb[2], bb[3]))
