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


def is_point_in_path(x: int, y: int, poly) -> bool:
    """Determine if the point is in the path.

    Args:
      x -- The x coordinates of point.
      y -- The y coordinates of point.
      poly -- a list of tuples [(x, y), (x, y), ...]

    Returns:
      True if the point is in the path.
    """
    num = len(poly)
    i = 0
    j = num - 1
    c = False
    for i in range(num):
        if ((poly[i][1] > y) != (poly[j][1] > y)) and \
                (x < poly[i][0] + (poly[j][0] - poly[i][0]) * (y - poly[i][1]) /
                                  (poly[j][1] - poly[i][1])):
            c = not c
        j = i
    return c


def annotation(event, x, y, flags, param):
    global curr_polygon, polygons, names, ref_pt, curr_pt, mutex

    curr_pt = (x, y)
    curr_pt = minmax(curr_pt)

    # ctrl + left click: remove a specific polygon
    if keyboard.is_pressed('ctrl'):
        if event == cv2.EVENT_LBUTTONDOWN:
            mutex.acquire()
            for i in range(len(polygons)):
                if is_point_in_path(x, y, polygons[i]):
                    del names[i], polygons[i]
                    break
            mutex.release()
        return

    if event == cv2.EVENT_LBUTTONDOWN:
        if len(curr_polygon) == 0:
            ref_pt = (x, y)
            curr_polygon.append(ref_pt)
        else:
            norm = np.linalg.norm(
                [curr_pt[0] - ref_pt[0], curr_pt[1] - ref_pt[1]])
            if norm < 10:
                answer = tk.simpledialog.askstring(
                    title='Q', prompt='Enter object name')
                if answer is not None:
                    names.append(answer.upper())
                    polygons.append(curr_polygon)
                    curr_polygon = []
            else:
                curr_polygon.append(curr_pt)

    if event == cv2.EVENT_RBUTTONDOWN:
        curr_polygon.pop()


def construct_xml(cam_name):

    data = ET.Element('polygons')
    ET.SubElement(data, 'cam_name').text = cam_name

    return data


def copy_xml(xml):

    new_xml = xml
    del_list = [e for e in new_xml.iter('polygon')]
    for e in del_list:
        new_xml.remove(e)

    return new_xml


def get_xml_path(img_path):

    basename = os.path.basename(img_path)
    filename = os.path.splitext(basename)[0]

    xml_path = img_path.split(os.sep)
    xml_path = '{}/polygons/{}.xml'.format(
        os.path.join(*xml_path[:-2]), filename)

    return xml_path


def get_paired_data(img_path, xml_path):

    img = cv2.imread(img_path)

    xml = None
    if os.path.isfile(xml_path):
        xml = ET.parse(xml_path).getroot()
    else:
        xml = construct_xml(img_path)

    return img, xml


def xml2array(xml):
    global polygons

    polygons = []

    for e in xml.iter('polygon'):
        name = e.find('name').text
        names.append(name)

        polygon = []
        num = int(e.find('num').text)
        for i in range(num):
            x = int(e.find('x{}'.format(i)).text)
            y = int(e.find('y{}'.format(i)).text)
            polygon.append((x, y))
        polygons.append(polygon)


def array2xml(xml):
    global polygons

    for i in range(len(polygons)):
        obj = ET.SubElement(xml, 'polygon')
        ET.SubElement(obj, 'name').text = names[i]
        ET.SubElement(obj, 'num').text = str(len(polygons[i]))
        for j in range(len(polygons[i])):
            ET.SubElement(obj, 'x{}'.format(j)).text = str(polygons[i][j][0])
            ET.SubElement(obj, 'y{}'.format(j)).text = str(polygons[i][j][1])


parser = argparse.ArgumentParser()

parser.add_argument('--root_dir', type=str,
                    help='root directory containing images', default='E:/cam_data')
parser.add_argument('--img_ext', type=str,
                    help='extension of image files', default='png')

args = parser.parse_args(sys.argv[1:])

# parsing image files
img_list = glob.glob('{}/images/*.{}'.format(args.root_dir, args.img_ext))
if len(img_list) == 0:
    print('no {} image files'.format(args.img_ext))
    exit()

# making a directory for annotation
annot_path = '{}/polygons'.format(args.root_dir)
if not os.path.exists(annot_path):
    os.mkdir(annot_path)

# initialize tkinter
tk.Tk().withdraw()

idx = 0
names = []
polygons = []
curr_polygon = []
ref_pt = None
curr_pt = None
mutex = Lock()

cross_hair = True

img_path = os.path.normpath(img_list[idx])
xml_path = os.path.normpath(get_xml_path(img_path))

img, xml = get_paired_data(img_list[idx], xml_path)
xml2array(xml)

cv2.namedWindow('set_polygons')
cv2.setMouseCallback('set_polygons', annotation)

while True:
    clone = img.copy()

    utils.draw_nav_string(clone, img_list, idx)

    if cross_hair and curr_pt is not None:
        utils.draw_crosshair(clone, curr_pt)

    if len(curr_polygon) != 0:
        cv2.circle(clone, curr_polygon[0], 10, utils.G, 1)
        for i in range(len(curr_polygon) - 1):
            cv2.line(clone, curr_polygon[i], curr_polygon[i + 1], utils.G, 1)

    mutex.acquire()
    for i in range(len(polygons)):
        utils.draw_polygon(clone, polygons[i], names[i])
    mutex.release()

    cv2.imshow('set_polygons', clone)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('h'):
        cross_hair = not cross_hair

    if key == ord('c'):
        msg_box = tk.messagebox.askquestion(
            'Clear', 'Do you wish you clear annotation data?', icon='warning')
        if msg_box == 'yes':
            names = []
            polygons = []
            curr_polygon = []
            ref_pt = None
            curr_pt = None

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
