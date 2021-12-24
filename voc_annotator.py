import os
import sys
import glob
import argparse
import keyboard

import cv2
import numpy as np
import tkinter as tk
import tkinter.simpledialog
import xml.dom.minidom as minidom
import xml.etree.ElementTree as ET
import draw_utils as utils

from multiprocessing import Lock


def minmax(pt):
    global img

    x = np.min([np.max([0, pt[0]]), img.shape[1] - 1])
    y = np.min([np.max([0, pt[1]]), img.shape[0] - 1])

    return (x, y)


def annotation(event, x, y, flags, param):
    global ref_pt, prev_pt, curr_pt, tl, br, name, mutex

    curr_pt = (x, y)
    curr_pt = minmax(curr_pt)

    # ctrl + left click: remove a specific box
    if keyboard.is_pressed('ctrl'):
        if event == cv2.EVENT_LBUTTONDOWN:
            mutex.acquire()
            for i in range(len(name)):
                if tl[i][0] < x and x < br[i][0] and tl[i][1] < y and y < br[i][1]:
                    del tl[i], br[i], name[i]
                    break
            mutex.release()
        return

    if event == cv2.EVENT_LBUTTONDOWN:
        ref_pt = (x, y)

    if event == cv2.EVENT_LBUTTONUP and ref_pt is not None:
        tl.append(ref_pt)
        br.append(curr_pt)
        if args.default_name is None:
            answer = tk.simpledialog.askstring(
                title='Q', prompt='Enter object name')
        else:
            answer = args.default_name

        if answer is not None:
            name.append(answer)
        else:
            tl.pop()
            br.pop()

        ref_pt = None

    if event == cv2.EVENT_RBUTTONDOWN and 0 < len(name):
        tl.pop()
        br.pop()
        name.pop()

    # space: relocate top-left corner of the box
    if keyboard.is_pressed(' ') and ref_pt is not None:
        reloc_pt = np.add(ref_pt, np.subtract(curr_pt, prev_pt))
        ref_pt = tuple(minmax(reloc_pt))

    prev_pt = curr_pt


def construct_xml(filename, img):

    data = ET.Element('annotation')
    # ET.SubElement(data, 'filename').text = filename

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
    xml_path = xml_path[0] + os.sep + \
        os.path.join(*xml_path[1:-2], 'Annotations', filename + '.xml')

    return xml_path


def get_paired_data(img_path, xml_path):

    stream = open(img_path, 'rb')
    bytes = bytearray(stream.read())
    np_arr = np.asarray(bytes, dtype=np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_UNCHANGED)

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

parser.add_argument('--root_dir', type=str,
                    help='root directory of the dataset; directory structure must be same as VOC 2007/2012', default='E:/VOCdevkit/VOC2007')
parser.add_argument('--img_ext', type=str,
                    help='extension of image files', default='jpg')
parser.add_argument('--default_name', type=str,
                    help='default name of annotated objects')

args = parser.parse_args(sys.argv[1:])

# parsing image files
img_list = glob.glob('{}/JPEGImages/*.{}'.format(args.root_dir, args.img_ext))
if len(img_list) == 0:
    print('no {} image files'.format(args.img_ext))
    exit()

img_list.sort()

# making a directory for annotation
annot_path = '{}/Annotations'.format(args.root_dir)
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
save_tr = None
save_br = None
save_name = None
mutex = Lock()

cross_hair = True

img_path = os.path.normpath(img_list[idx])
xml_path = get_xml_path(img_path)

img, xml = get_paired_data(img_list[idx], xml_path)
xml2array(xml)

cv2.namedWindow('annotator', cv2.WINDOW_NORMAL)
cv2.setMouseCallback('annotator', annotation)

while True:
    clone = img.copy()

    utils.draw_nav_string(clone, img_list, idx)

    if cross_hair and curr_pt is not None:
        utils.draw_crosshair(clone, curr_pt)

    if ref_pt is not None:
        cv2.rectangle(clone, ref_pt, curr_pt, utils.G, 1)

    mutex.acquire()
    for i in range(len(name)):
        utils.draw_annot(clone, name[i], tl[i], br[i])
    mutex.release()

    cv2.imshow('annotator', clone)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('h'):
        cross_hair = not cross_hair

    if key == ord('c'):
        msg_box = tk.messagebox.askquestion(
            'Clear', 'Do you wish you clear annotation data?', icon='warning')
        if msg_box == 'yes':
            tl = []
            br = []
            name = []

    if key == ord('y'):
        x = curr_pt[0]
        y = curr_pt[1]
        for i in range(len(name)):
            if tl[i][0] < x and x < br[i][0] and tl[i][1] < y and y < br[i][1]:
                save_tl = tl[i]
                save_br = br[i]
                save_name = name[i]
                break

    if key == ord('v') and save_name is not None:
        tl.append(save_tl)
        br.append(save_br)
        name.append(save_name)

    if key == ord('g') or key == ord('F') or key == ord('f') or key == ord('d') or key == ord('q'):
        # save current data
        new_xml = copy_xml(xml)
        array2xml(new_xml)

        with open(xml_path, 'w+') as f:
            xml_str = ET.tostring(new_xml)
            xml_str = minidom.parseString(xml_str).toprettyxml()
            f.write(xml_str)

        # move to the next state
        if key == ord('g'):
            answer = tk.simpledialog.askinteger(
                title='Q', prompt='Enter frame index to move')
            if answer is None:
                continue
            idx = np.min([answer - 1, len(img_list) - 1])
            idx = np.max([idx, 0])
        elif key == ord('F') or key == ord('f'):
            idx = np.min([idx + 1, len(img_list) - 1])
        elif key == ord('d'):
            idx = np.max([idx - 1, 0])
        else:
            break

        img_path = os.path.normpath(img_list[idx])
        xml_path = get_xml_path(img_path)

        img, xml = get_paired_data(img_list[idx], xml_path)
        if key != ord('F'):
            xml2array(xml)

cv2.destroyAllWindows()
