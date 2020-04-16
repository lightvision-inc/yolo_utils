# Utility scripts for YOLOv3

These scripts are designed to train and validate YOLOv3 easily.

## List of scripts

Script  | Dataset | Detail
------------- | ------------- | -------------
[coco_make_subset.py](./coco_make_subset.py) | COCO 2017 | Generate annotation files for target classes
[coco_make_subset_list.py](./coco_make_subset_list.py) | COCO 2017 | Generate a list of subset images
[voc_make_subset.py](./voc_make_subset.py) | VOC 2007/2012 | Generate annotation files for target classes
[voc_make_subset_list.py](./voc_make_subset_list.py) | VOC 2007/2012 | Generate a list of subset images

## Batch files

* [coco.bat](./coco.bat) generates annotation txt files for training and annotation in the folder containing COCO 2017 dataset, and lists of training and validation image files
* [voc.bat](./voc.bat) generates annotation txt files in the folder containing VOC 2007/2012 datasets, and a list of image files

### Important note
In our project, VOC 2007/2012 datasets are only used for training; therefore, we do not generate separate lists of image files.

## Directory structure for datasets

### COCO 2017

You can download COCO 2017 dataset at [here](http://cocodataset.org/).

```bash
"coco_root_path"
├── annotations
│   ├── instances_train2017.json
│   └── instances_val2017.json
├── train2017
│   ├── 000000000009.jpg
│   ├── ...
│   └── 000000581929.jpg
├── val2017
│   ├── 000000000139.jpg
│   ├── ...
│   └── 000000581781.jpg
└── test2017
    ├── 000000000001.jpg
    ├── ...
    └── 000000581918.jpg
```

### VOC 2007/2012

You can download VOC 2007/2012 datasets at [here](http://host.robots.ox.ac.uk/pascal/VOC/).

```bash
"voc_root_path"
├── VOC2007
│   ├── Annotations
│   │   ├── 000001.xml
│   │   ├── ... 
│   │   └── 009963.xml
│   ├── ImageSets
│   │   ├── Layout
│   │   │   ├── test.txt
│   │   │   ├── train.txt
│   │   │   ├── trainval.txt
│   │   │   └── val.txt
│   │   ├── Main
│   │   │   ├── aeroplane_test.txt
│   │   │   ├── ...
│   │   │   └── val.txt
│   │   └── Segmentation
│   │       ├── test.txt
│   │       ├── train.txt
│   │       ├── trainval.txt
│   │       └── val.txt
│   ├── JPEGImages
│   │   ├── 000001.png
│   │   ├── ... 
│   │   └── 009963.png
│   ├── SegmentationClass
│   │   ├── 000032.png
│   │   ├── ... 
│   │   └── 009950.png
│   └── SegmentationObject
│       ├── 000032.png
│       ├── ... 
│       └── 009950.png
└── VOC2012
    ├── Annotations
    │   ├── 2007_000027.xml
    │   ├── ... 
    │   └── 2012_004331.xml
    ├── ImageSets
	│   ├── Action
    │   │   ├── jumping_test.txt
    │   │   ├── ...
    │   │   └── walking_val.txt
    │   ├── Layout
    │   │   ├── test.txt
    │   │   ├── train.txt
    │   │   ├── trainval.txt
    │   │   └── val.txt
    │   ├── Main
    │   │   ├── aeroplane_test.txt
    │   │   ├── ...
    │   │   └── val.txt
    │   └── Segmentation
    │       ├── test.txt
    │       ├── train.txt
    │       ├── trainval.txt
    │       └── val.txt
    ├── JPEGImages
    │   ├── 2007_000027.png
    │   ├── ... 
    │   └── 2012_004331.png
    ├── SegmentationClass
    │   ├── 2007_000032.png
    │   ├── ... 
    │   └── 2011_003271.png
    └── SegmentationObject
        ├── 2007_000032.png
        ├── ... 
        └── 2011_003271.png

```