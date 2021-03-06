# Utility scripts for YOLO

These scripts are designed to train and validate YOLO easily.

## List of scripts

Script  | Dataset | Detail
------------- | ------------- | -------------
[coco_make_subset.py](./coco_make_subset.py) | COCO 2017 | Generate txt files for target classes from JSON annotation files
[coco_make_subset_list.py](./coco_make_subset_list.py) | COCO 2017 | Generate a list of annotated images
[voc_make_subset.py](./voc_make_subset.py) | VOC 2007/2012 | Generate txt files for target classes from XML annotation files
[voc_make_list.py](./voc_make_list.py) | VOC 2007/2012 | Generate a list of annotated images
[voc_annotator.py](./voc_annotator.py) | - | VOC style GUI annotator
[voc_xml_to_txt.py](./voc_xml_to_txt.py) | - | Generate txt files from XML annotation files
[visualize_txt_annot.py](./visualize_txt_annot.py) | - | Visualize annotated images based on txt files

## Batch files

* [coco.bat](./coco.bat) generates annotation txt files for training and annotation in the folder containing COCO 2017 dataset, and lists of training and validation image files
* [voc.bat](./voc.bat) generates annotation txt files in the folder containing VOC 2007/2012 datasets, and a list of image files

### Important note
In our project, VOC 2007/2012 datasets are only used for training; therefore, we do not generate separate lists of image files.

## Annotator

[voc_annotator.py](./voc_annotator.py) script provides a GUI for annotating bounding boxes. You can draw a rectangle by clicking a left mouse button and dragging. Also, you can pop out the most recent rectangle by clicking a right mouse button. To remove a specific rectangle, you can left click the rectangle with <kbd>ctrl</kbd> button pressed. If you want to relocate a center of the rectangle during the dragging, you can press <kbd>space</kbd>. After you finish drawing the rectangle, a dialog to get the name of the object will pop up.

This annotator follows the XML structure for VOC 2007/2012 datasets. In the datasets, there are three more fields for annotation: pose, truncated, difficult. Currently, our implementation does not support any interfaces to fill those three fields.

### Keyboard shortcuts

Shortcut | Description
--- | --- |
<kbd>q</kbd> | Quit the GUI
<kbd>g</kbd> | Navigate to a certain frame
<kbd>F</kbd> | Retain current annotations and move to the next frame
<kbd>f</kbd> | Move to the next frame
<kbd>d</kbd> | Move to the previous frame
<kbd>c</kbd> | Clear annotations for current frame

### Examples
![example_00](/fig/example_voc_annotator_00.png)
![example_01](/fig/example_voc_annotator_01.png)

## Directory structure for datasets

### COCO 2017

You can download COCO 2017 dataset at [here](http://cocodataset.org/).

```bash
"coco_root_dir"
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
"voc_root_dir"
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