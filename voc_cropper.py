# Crops specified objects from VOC annotated image
# By default, this will act as license plate cropper.

import os
import sys
import argparse
import xml.etree.ElementTree as ET
from PIL import Image
import imagehash

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
    os.makedirs(current_path + '/cropped/', exist_ok=True)
    image_path = current_path+img_name+img_ext_str
    image = Image.open(image_path)
    for i in range(len(annotations)):
        annotation = annotations[i]
        crop_path = current_path + '/cropped/' + img_name + '_{}'.format(i) + img_ext_str
        cropped_image = image.crop((annotation['xmin'], annotation['ymin'], 
                                    annotation['xmax'], annotation['ymax']))
        width, height = image.size
        max_dim = max(width, height)
        multiple = 416//max_dim
        if multiple>1:
            cropped_image = cropped_image.resize(width*(multiple+1),height*(multiple+1))
        cropped_image.save(crop_path)

def main(args):
    path = args.root_dir + args.imgs_subdir
    for _, _, f in os.walk(path):
        for file in f:
            img_ext_str = '.{}'.format(args.img_ext)
            if img_ext_str in file:
                img_name = file[:-4]
                xml_file = file.replace(img_ext_str, '.xml')
                xml_path = args.root_dir + args.annots_subdir + xml_file
                annotation = extract_annotation(args.obj_name, xml_path)
                save_annot = []
                for i in range(len(annotation)):
                    if ((annotation[i]['ymax'] - annotation[i]['ymin']>30)
                        and (annotation[i]['xmax'] - annotation[i]['xmin'])>30):
                        save_annot.append(annotation[i])
                save_crops(path, img_name, img_ext_str, save_annot)
        break

    if args.dupe_scan:
        print("Cropping done, looking for near-identical images and deleting them ...")
        cropped_path = args.root_dir + args.imgs_subdir + '/cropped/'
        hashes = {}
        for _, _, files in os.walk(cropped_path):
            for file in files:
                if img_ext_str in file:
                    image = Image.open(cropped_path+file)
                    h = imagehash.average_hash(image)
                    if h in hashes:
                        print(f"Duplicate found: {file} and {hashes[h]}")
                        os.remove(cropped_path+file)  # Uncomment to actually delete the file
                    else:
                        hashes[h] = file
            break
        print("Near-identical images deleted. Cropper exiting with success.")

def parse_arguments(argv):

    parser = argparse.ArgumentParser()

    parser.add_argument('--root_dir', type=str,
                        help='root of VOC development kit', default='E:/VOCdevkit')
    parser.add_argument('--imgs_subdir', type=str,
                        help='subdirectory for images', default='/JPEGImages/')
    parser.add_argument('--annots_subdir', type=str,
                        help='subdirectory for xml annotations', default='/Annotations/')
    parser.add_argument('--obj_name', type=str,
                        help='name of object to be cropped', default = 'license_plate')
    parser.add_argument('--img_ext', type=str,
                        help='extension of image files', default = 'jpg')
    parser.add_argument('--dupe_scan', type=bool,
                        help='looks for duplicated crops and deletes them', default = False)

    return parser.parse_args(argv)


if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))
