import os
import cv2
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
        if classes is None:
            cid = int(c)
        else:
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


def privacy_protection(path, img_filename, classes):

    if not os.path.exists(f'{path}/PrivacyProtected'):
        os.makedirs(f'{path}/PrivacyProtected')

    filename = img_filename[:img_filename.rfind('.')]

    img = cv2.imread(f'{path}/JPEGImages/{img_filename}')
    annot_file = open(f'{path}/Annotations/{filename}.xml')
    tree = ET.parse(annot_file)
    root = tree.getroot()
    size = root.find('size')
    w = int(size.find('width').text)
    h = int(size.find('height').text)

    for obj in root.iter('object'):
        c = obj.find('name').text
        if c not in classes:
            continue

        xmlbox = obj.find('bndbox')
        pt1 = (int(xmlbox.find('xmin').text), int(xmlbox.find('ymin').text))
        pt2 = (int(xmlbox.find('xmax').text), int(xmlbox.find('ymax').text))

        img = cv2.rectangle(img, pt1, pt2, (0, 0, 0), -1)

    cv2.imwrite(f'{path}/PrivacyProtected/{img_filename}', img)
