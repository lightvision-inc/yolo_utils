# Crops specified objects from VOC annotated image
# By default, this will act as license plate cropper.

import os
import sys
import argparse
import xml.etree.ElementTree as ET
from PIL import Image

def extract_annotation(obj_name, xml_path):    

    tree = ET.parse(xml_path)
    root = tree.getroot()

    annotations = []

    for obj in root.findall('object'):
        name = obj.find('name').text
        if name == obj_name:
            xmin = int(obj.find('bndbox/xmin').text)
            ymin = int(obj.find('bndbox/ymin').text)
            xmax = int(obj.find('bndbox/xmax').text)
            ymax = int(obj.find('bndbox/ymax').text)

            annotations.append({
                'xmin': xmin,
                'ymin': ymin,
                'xmax': xmax,
                'ymax': ymax
            })

    return annotations

def crop_image(image_path, xmin, ymin, xmax, ymax):

    image = Image.open(image_path)
    cropped_image = image.crop((xmin, ymin, xmax, ymax))
    return cropped_image

def save_crops(current_path, img_name, img_ext_str, annotations):
    os.makedirs(current_path + 'cropped/', exist_ok=True)
    image_path = current_path+img_name+img_ext_str
    image = Image.open(image_path)
    for i in range(len(annotations)):
        if (annotation['ymax']-annotation['ymin']<25):
            continue
        annotation = annotations[i]
        crop_path = current_path + 'cropped/' + img_name + '_{}'.format(i) + img_ext_str
        cropped_image = image.crop((annotation['xmin'], annotation['ymin'], 
                                    annotation['xmax'], annotation['ymax']))
        cropped_image.save(crop_path)

def main(args):
    path = args.root_dir + '/JPEGImages/'
    for _, _, f in os.walk(path):
        for file in f:
            img_ext_str = '.{}'.format(args.img_ext)
            if img_ext_str in file:
                img_name = file[:-4]
                xml_file = file.replace(img_ext_str, '.xml')
                xml_path = args.root_dir + '/Annotations/' + xml_file
                annotation = extract_annotation(args.obj_name, xml_path)
                save_crops(path, img_name, img_ext_str, annotation)

def parse_arguments(argv):

    parser = argparse.ArgumentParser()

    parser.add_argument('--root_dir', type=str,
                        help='root of VOC development kit', default='E:/VOCdevkit')
    parser.add_argument('--obj_name', type=str,
                        help='name of object to be cropped', default = 'license_plate')
    parser.add_argument('--img_ext', type=str,
                        help='extension of image files', default = 'jpg')

    return parser.parse_args(argv)


if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))
