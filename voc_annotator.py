import os
import sys
import glob
import argparse
import keyboard

import cv2
import numpy as np
import tkinter as tk
import xml.dom.minidom as minidom
import xml.etree.ElementTree as ET


def annotation(event, x, y, flags, param):
    global ref_pt, prev_pt, curr_pt, tl, br, name

    if event == cv2.EVENT_LBUTTONDOWN:
        ref_pt = (x, y)

    if event == cv2.EVENT_LBUTTONUP:
        tl.append(ref_pt)
        br.append(curr_pt)
        name.append(tk.simpledialog.askstring(
            title='Q', prompt='Enter object name'))
        ref_pt = None

    if event == cv2.EVENT_RBUTTONDOWN:
        tl.pop()
        br.pop()
        name.pop()

    curr_pt = (x, y)
    if keyboard.is_pressed(' '):
        ref_pt = tuple(np.add(ref_pt, np.subtract(curr_pt, prev_pt)))
    prev_pt = curr_pt


def construct_xml(filename, img):
    data = ET.Element('annotation')
    ET.SubElement(data, 'filename').text = filename

    sz = ET.SubElement(data, 'size')
    ET.SubElement(sz, 'width').text = str(img.shape[1])
    ET.SubElement(sz, 'height').text = str(img.shape[0])
    ET.SubElement(sz, 'depth').text = str(img.shape[2])

    ET.SubElement(data, 'segmented').text = "0"

    return data


def copy_xml(xml):
    new_xml = xml
    del_list = [e for e in new_xml.iter('object')]
    for e in del_list:
        new_xml.remove(e)

    return new_xml


def get_xml_path(img_path):
    basename = os.path.basename(img_path)
    filename = os.path.splitext(basename)[0]

    xml_path = img_path.split(os.sep)
    xml_path = '{}/Annotations/{}.xml'.format(
        os.path.join(*xml_path[:-2]), filename)

    return xml_path


def get_paired_data(img_path, xml_path):
    img = cv2.imread(img_path)

    xml = None
    if os.path.isfile(xml_path):
        xml = ET.parse(xml_path).getroot()
    else:
        xml = construct_xml(img_path, img)

    return img, xml


def xml2array(xml):
    global tl, br, name

    tl = []
    br = []
    name = []

    for e in xml.iter('object'):
        name.append(e.find('name').text)
        bb = e.find('bndbox')

        xmin = int(bb[0].text)
        ymin = int(bb[1].text)
        xmax = int(bb[2].text)
        ymax = int(bb[3].text)

        tl.append((xmin, ymin))
        br.append((xmax, ymax))


def array2xml(xml):
    global tl, br, name

    for i in range(len(tl)):
        obj = ET.SubElement(xml, 'object')
        ET.SubElement(obj, 'name').text = name[i]
        ET.SubElement(obj, 'pose').text = 'Unspecified'
        ET.SubElement(obj, 'truncated').text = '0'
        ET.SubElement(obj, 'difficult').text = '0'

        bb = ET.SubElement(obj, 'bndbox')
        ET.SubElement(bb, 'xmin').text = str(tl[i][0])
        ET.SubElement(bb, 'ymin').text = str(tl[i][1])
        ET.SubElement(bb, 'xmax').text = str(br[i][0])
        ET.SubElement(bb, 'ymax').text = str(br[i][1])


parser = argparse.ArgumentParser()

parser.add_argument('--root_path', type=str,
                    help='root path of the dataset; directory structure must be same as VOC 2007/2012', default='E:/VOCdevkit/VOC2007')
parser.add_argument('--img_ext', type=str,
                    help='extension of image files', default='jpg')

args = parser.parse_args(sys.argv[1:])

# parsing image files
img_list = glob.glob('{}/JPEGImages/*.{}'.format(args.root_path, args.img_ext))
if len(img_list) == 0:
    print('no {} image files'.format(args.img_ext))
    exit()

# making a directory for annotation
annot_path = '{}/Annotations'.format(args.root_path)
if not os.path.exists(annot_path):
    os.mkdir(annot_path)

# initialize tkinter
tk.Tk().withdraw()

idx = 0
ref_pt = None
prev_pt = None
curr_pt = None
tl = []
br = []
name = []

img_path = os.path.normpath(img_list[idx])
xml_path = get_xml_path(img_path)

img, xml = get_paired_data(img_list[idx], xml_path)
xml2array(xml)

cv2.namedWindow('annotator')
cv2.setMouseCallback('annotator', annotation)

while True:
    clone = img.copy()

    if ref_pt is not None:
        cv2.rectangle(clone, ref_pt, curr_pt, (0, 255, 0), 1)

    for i in range(len(tl)):
        cv2.rectangle(clone, tl[i], br[i], (0, 0, 255), 1)
        cv2.rectangle(clone, (tl[i][0], tl[i][1] - 20),
                      (br[i][0], tl[i][1]), (0, 0, 255), -1)
        cv2.putText(clone, name[i], (tl[i][0] + 3, tl[i][1] - 7),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    cv2.imshow('annotator', clone)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('f') or key == ord('b') or key == ord('q'):
        # save current data
        new_xml = copy_xml(xml)
        array2xml(new_xml)

        with open(xml_path, 'w+') as f:
            xml_str = ET.tostring(new_xml)
            xml_str = minidom.parseString(xml_str).toprettyxml()
            f.write(xml_str)

        # move to the next state
        if key == ord('f'):
            idx = idx + 1 % len(img_list)
        elif key == ord('b'):
            idx = np.max([idx - 1, 0])
        else:
            break

        img_path = os.path.normpath(img_list[idx])
        xml_path = get_xml_path(img_path)

        img, xml = get_paired_data(img_list[idx], xml_path)
        xml2array(xml)

cv2.destroyAllWindows()
