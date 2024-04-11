import numpy as np
import torch
from PIL import Image
import sys
import os
import argparse
from typing import List
import xml.etree.ElementTree as ET
    
def xyxytoxywh(x):
    # Convert nx4 boxes from [x1, y1, x2, y2] to [x, y, w, h] where xy1=top-left, xy2=bottom-right
    y = x.clone() if isinstance(x, torch.Tensor) else np.copy(x)
    y[0] = (x[0] + x[2]) / 2  # x center
    y[1] = (x[1] + x[3]) / 2  # y center
    y[2] = x[2] - x[0]  # width
    y[3] = x[3] - x[1]  # height
    return y
    
def annotation_to_xyxy(path, filename):
    in_file = open(
    '{}/Annotations/{}.xml'.format(path, filename))
    tree = ET.parse(in_file)
    root = tree.getroot()
    b = []

    for obj in root.iter('object'):
        c = obj.find('name').text
        if c in ('car', 'motorbike', 'license_plate'):
            xmlbox = obj.find('bndbox')
            b.append([float(xmlbox.find('xmin').text), float(xmlbox.find('ymin').text), float(
                xmlbox.find('xmax').text), float(xmlbox.find('ymax').text)])
        
    return b

def save_data(lpd_box_list, vd_xyxy, image, filename, opt, i):
    cropped_image = image.crop((vd_xyxy[0], vd_xyxy[1], vd_xyxy[2], vd_xyxy[3]))
    crop_path = '{}/{}_{}.jpg'.format(opt.outdir, filename, i)
    cropped_image.save(crop_path)
    
    f = open('{}/{}_{}.txt'.format(opt.outdir, filename, i), "w+")
    for lpd_xyxy in lpd_box_list:
        new_lpd = []
        if (lpd_xyxy[2] - lpd_xyxy[0]) * (lpd_xyxy[3] - lpd_xyxy[1]) > opt.plate_size:
            if not(lpd_xyxy[0] > vd_xyxy[2] or lpd_xyxy[2] < vd_xyxy[0] or lpd_xyxy[1] > vd_xyxy[3] or lpd_xyxy[3] < vd_xyxy[1]):
                new_lpd.append(lpd_xyxy[0] - vd_xyxy[0])
                new_lpd.append(lpd_xyxy[1] - vd_xyxy[1])
                new_lpd.append(lpd_xyxy[2] - vd_xyxy[0])
                new_lpd.append(lpd_xyxy[3] - vd_xyxy[1])

                lpd_xywh = xyxytoxywh(new_lpd)

                f.write("{} {:f} {:f} {:f} {:f}\n".format("0", lpd_xywh[0], lpd_xywh[1], lpd_xywh[2], lpd_xywh[3]))
    f.close()

def crop_lpd(lpd_box_list, vd_box_list, image, filename, opt):
    i = 0
    for vd_xyxy in vd_box_list:
        #print('-------')
        #print(vd_xyxy)
        check = 0
        for lpd_xyxy in lpd_box_list:
            if (lpd_xyxy[2] - lpd_xyxy[0]) * (lpd_xyxy[3] - lpd_xyxy[1]) > opt.plate_size:
                    #print(lpd_xyxy)
                if not(lpd_xyxy[0] > vd_xyxy[2] or lpd_xyxy[2] < vd_xyxy[0] or lpd_xyxy[1] > vd_xyxy[3] or lpd_xyxy[3] < vd_xyxy[1]):
                    vd_xyxy[0] = min(vd_xyxy[0], lpd_xyxy[0])
                    vd_xyxy[1] = min(vd_xyxy[1], lpd_xyxy[1])
                    vd_xyxy[2] = max(vd_xyxy[2], lpd_xyxy[2])
                    vd_xyxy[3] = max(vd_xyxy[3], lpd_xyxy[3])
                    check = 1

        if(check):
            save_data(lpd_box_list, vd_xyxy, image, filename, opt, i)
            i += 1

def main(opt):
    if not os.path.exists(opt.outdir):
        os.makedirs(opt.outdir)

    path=opt.input
    img_path = os.path.join(path,"lpd/JPEGImages")
    img_names=os.listdir(img_path)
    
    for img_name in img_names:
        if img_name.endswith(".jpg") or img_name.endswith(".png"):
            image = Image.open(os.path.join(img_path,img_name))

            filename = img_name[:-4]
            vd_filename = filename
            if "LP" in filename:
                vd_filename = vd_filename.replace("LP", "CMP")
            lpd_anno_path = os.path.join(path,"lpd")
            vd_anno_path = os.path.join(path, "car")

            lpd_box_list = annotation_to_xyxy(lpd_anno_path, filename)
            vd_box_list = annotation_to_xyxy(vd_anno_path, vd_filename)

            crop_lpd(lpd_box_list, vd_box_list, image, filename, opt)


def parse_opt(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, default='01_annotated', help='Specify the folder where the \'car\' and \'lpd\' folders are located')
    parser.add_argument('--outdir', type=str, default='output', help='file/output/dir')
    parser.add_argument('--plate_size', type=int, default='0')
    return parser.parse_args(argv)


if __name__ == '__main__':
    main(parse_opt(sys.argv[1:]))