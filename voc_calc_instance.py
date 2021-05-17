import sys
import glob
import argparse
import xml.etree.ElementTree as ET


parser = argparse.ArgumentParser()

parser.add_argument('--list_file', type=str,
                    help='file that contains a list of annotated images', default='train_car.txt')

args = parser.parse_args(sys.argv[1:])

stat = {}
with open(args.list_file) as f:
    for l in f.readlines():
        l = l.rstrip()
        l = l.replace('JPEGImages', 'Annotations')
        l = l.replace('jpg', 'xml')
        l = l.replace('png', 'xml')

        xml = ET.parse(l).getroot()
        for e in xml.iter('object'):
            name = e.find('name').text
            if name in stat:
                stat[name] = stat[name] + 1
            else:
                stat[name] = 0

print(stat)
