import os
import glob
import tqdm
import random
import argparse
import numpy as np
import cv2

# Assume you have the YOLO annotations for object detection in *.txt
# Assume your detection object is easily discernable just using opencv contour detection

def rotate_expand_image(image, angle):
    # Get new image size, rotation matrix
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])
    new_w = int((h * sin) + (w * cos))
    new_h = int((h * cos) + (w * sin))
    M[0, 2] += (new_w / 2) - center[0]
    M[1, 2] += (new_h / 2) - center[1]

    # Actually do the rotation
    rotated = cv2.warpAffine(image, M, (new_w, new_h))
    return rotated

def txt_to_list(filename: str):
    annotations = []
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()  # Remove any leading/trailing whitespace
            if not line:
                continue  # Skip empty lines
            parts = line.split(' ')
            class_id = int(parts[0])
            coordinates = [float(x) for x in parts[1:]]
            annotation = (class_id, *coordinates)  # Store as a tuple
            annotations.append(annotation)
    return annotations


def masks_from_img(image: np.ndarray, annot_list: list):
    ## INPUTS
    # image: np.ndarray type image from opencv
    # annot_list: list type (cls_id, x_c, y_c, w, h)
    ## OUTPUTS
    # output: mask_list = list of N masks, each mask is ndarray of W x H shape
    # output: cls_list = Class label of N masks
    W, H = image.shape
    N = len(annot_list)
    cls_list = []
    mask_list = np.zeros((N,W,H), dtype=np.uint8)
    for i in range(N):
        bbox_mask = np.zeros((W,H))
        annot = annot_list[i]
        (x_c, y_c, w, h) = annot[1:5]
        cls_list.append(annot[0])
        (L, B, R, T) = (int(W*(x_c - w/2)), int(H*(y_c - h/2)), int(W*(x_c + w/2)), int(H*(y_c + h/2)))
        bbox_mask[L:R, B:T] = 1
        
        # generate mask

        # TODO: Make masks that can actually capture the letter outline
        #  _, thresh = cv2.threshold(image*bbox_mask, 128, 255, cv2.THRESH_BINARY)
        # thresh=thresh.astype(np.uint8)
        # contour, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        mask=np.zeros_like(image)
        # cv2.drawContours(mask,contour,-1,255,thickness=cv2.FILLED)
        # mask_list[i] = mask

        # Optionally, set mask as the ellipse!
        cv2.ellipse(mask, (int((T+B)//2),int((L+R)//2)), (int((T-B)/2.2), int((R-L)/2.2)), angle=0, startAngle=0, endAngle=360, color=255, thickness=cv2.FILLED)
        
        mask_list[i] = mask

        # Apply MORPH_OPEN to the mask
        # kernel = np.ones((3,3), np.uint8)
        # mask_list[i] = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    return mask_list, cls_list


def masks_to_annot(rotated_masks,cls_list):
    N = len(cls_list)
    (W,H) = rotated_masks[0].shape
    bounding_boxes = []
    for i in range(N):
        rows, cols = np.where(rotated_masks[i]!=0)
        if len(rows)==0 or len(cols)==0:
            continue
        L, T, R, B = np.min(rows), np.min(cols), np.max(rows), np.max(cols)
        x_c, y_c, w, h = (L+R)/(2*W), (T+B)/(2*H), (R-L)/W, (B-T)/H
        bounding_boxes.append([cls_list[i], x_c, y_c, w, h])

    return bounding_boxes

def save_annot(bounding_boxes, new_annotname):
    N = len(bounding_boxes)
    for i in range(N):
        bb = bounding_boxes[i]
        out_file = open(new_annotname, 'a+')
        out_file.write('{} {:f} {:f} {:f} {:f}\n'.format(bb[0], bb[1], bb[2], bb[3], bb[4]))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rotation data augmentation by generating masks")

    parser.add_argument("--directory", type= str, default = "./test_plates")
    parser.add_argument("--img_ext", type= str, default = "png", help="desired image extension")
    parser.add_argument("--max_degree", type= float, default = 45.0, help="max degrees to rotate")
    parser.add_argument("--rotate_times", type= int, default = 3, help="max times to rotate")

    args = parser.parse_args()
    files_list = glob.glob(f'{args.directory}/*.{args.img_ext}')

    for image_file in tqdm.tqdm(files_list):
        filename = image_file[:image_file.rfind('.')]
        image = cv2.imread(image_file, cv2.IMREAD_GRAYSCALE)
        image = image.astype(np.uint8)

        # 1. Obtain letter masks from annotation
        # Continue if text file does not exist(very possible if all letters are not eligible)
        if not os.path.exists(f'{filename}.txt'):
            continue
        annot_list = txt_to_list(f'{filename}.txt')
        mask_list, cls_list = masks_from_img(image, annot_list)

        for i in range(args.rotate_times):
            # 2. Rotate the image and masks accordingly
            rotate_angle = random.uniform(-args.max_degree, args.max_degree)
            rotated_image = rotate_expand_image(image, rotate_angle)
            rotated_masks = []

            for j in range(len(cls_list)):
                rotated_masks.append(rotate_expand_image(mask_list[j], -rotate_angle))

            # 3. Re-create annotations from the masks
            bounding_boxes = masks_to_annot(rotated_masks,cls_list)

            # 4. Save the rotated image and annotation
            new_annotname = f'{filename}_rot{i:d}.txt'
            new_imagename = f'{filename}_rot{i:d}.{args.img_ext}'
            save_annot(bounding_boxes, new_annotname)
            cv2.imwrite(new_imagename, rotated_image)