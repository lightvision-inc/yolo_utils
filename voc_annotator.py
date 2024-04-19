import os
import sys
import json
import argparse
import tkinter as tk

import cv2
import numpy as np
import keyboard
import xml.dom.minidom as minidom
import xml.etree.ElementTree as ET

from tkinter import messagebox, filedialog, simpledialog
from PIL import Image, ImageTk
from pathlib import Path

import draw_utils as utils


class MainWindow:
    def __init__(self, args):
        self.args = args

        self.tk = tk.Tk()
        self.tk.title('VOC annotator')

        x_factor, y_factor = self.args.aspect_ratio.split(':')
        x_factor = int(x_factor)
        y_factor = int(y_factor)

        # get a screen height
        screen_height = self.tk.winfo_screenheight()
        self.frame_height = int(screen_height * 0.9)
        self.frame_width = int(self.frame_height * x_factor / y_factor)

        # initialize empty image
        img = np.zeros((self.frame_height, self.frame_width, 3), np.uint8)
        img = Image.fromarray(img)
        self.disp_tk = ImageTk.PhotoImage(image=img)
        self.disp = tk.Label(self.tk, image=self.disp_tk)
        self.disp.pack(side='left')
        self.disp.config(cursor='none')

        frame = tk.Frame(self.tk)
        frame.pack(side='right', fill='both', expand=True)

        self.open_folder = tk.Button(
            frame, text='Open Folder', overrelief='solid', command=self._open_folder)
        self.open_folder.pack(side='top', fill='x')

        self.set_default_name = tk.Button(
            frame, text='Set default name', overrelief='solid', command=self._set_default_name)
        self.set_default_name.pack(side='top', fill='x')

        self.label_folder = tk.Label(frame)
        self.label_folder.pack(side='top', fill='x')

        self.label_file_idx = tk.Label(frame)
        self.label_file_idx.pack(side='top', fill='x')

        self.label_default_name = tk.Label(frame)
        self.label_default_name.pack(side='top', fill='x')

        self.listbox = tk.Listbox(frame, selectmode='browse')
        self.listbox.pack(side='left', fill='both', expand=True)
        self.listbox.bind('<<ListboxSelect>>', self._listbox_select)

        self.scrollbar = tk.Scrollbar(frame)
        self.scrollbar.pack(side='right', fill='both')

        self.listbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.listbox.yview)

        # self.is_full_screen = False
        self.tk.bind('f', self._forward)
        self.tk.bind('F', self._forward)
        self.tk.bind('d', self._backward)
        self.tk.bind('g', self._navigate)
        self.tk.bind('a', self._toggle_label)
        self.tk.bind('c', self._clear_annot)
        self.tk.protocol('WM_DELETE_WINDOW', self._save_info_and_exit)
        self.disp.bind('<Motion>', self._mouse_move_handler)
        self.disp.bind('<ButtonPress-1>', self._mouse_lbutton_press_handler)
        self.disp.bind('<ButtonPress-3>', self._mouse_rbutton_press_handler)
        self.disp.bind('<ButtonRelease-1>', self._mouse_button_release_handler)

        self.root = None
        self.info_path = None
        self.img_folder = None
        self.annot_folder = None
        self.info = {
            'file_idx': 0,
            'default_name': '',
            'draw_label': True
        }
        self.file_list = []
        self.info['file_idx'] = 0

        self.img_width = None
        self.img_height = None
        self.img = None
        self.xml = None
        self.xml_path = None
        self.prev_pos = None
        self.cur_pos = None
        self.ref_pos = None
        self.tl = []
        self.br = []
        self.names = []

    def _minmax(self, pos):
        x = min(max(0, pos[0]), self.img_width - 1)
        y = min(max(0, pos[1]), self.img_height - 1)
        return (x, y)

    def _mouse_move_handler(self, e):
        self.cur_pos = (e.x, e.y)

        # space: relocate top-left corner of the box
        if keyboard.is_pressed(' ') and self.ref_pos is not None:
            reloc_pos = np.add(self.ref_pos, np.subtract(
                self.cur_pos, self.prev_pos))
            self.ref_pos = tuple(self._minmax(reloc_pos))

        self.prev_pos = self.cur_pos
        self._display_image()

    def _mouse_lbutton_press_handler(self, e):
        if keyboard.is_pressed('ctrl'):
            for i in range(len(self.names)):
                if self.tl[i][0] < e.x and e.x < self.br[i][0] and self.tl[i][1] < e.y and e.y < self.br[i][1]:
                    del self.tl[i], self.br[i], self.names[i]
                    break
        else:
            self.ref_pos = (e.x, e.y)

    def _mouse_rbutton_press_handler(self, e):
        try:
            self.tl.pop()
            self.br.pop()
            self.names.pop()
            self._display_image()
        except IndexError:
            pass

    def _mouse_button_release_handler(self, e):
        if keyboard.is_pressed('ctrl'):
            self.ref_pos = None
            self._display_image()
            return

        if len(self.info['default_name']) == 0:
            name = simpledialog.askstring('Q', 'Enter object name')

            if name is None:
                self.ref_pos = None
                self._display_image()
                return

            self.names.append(name)
        else:
            self.names.append(self.info['default_name'])

        min_x = min(self.ref_pos[0], e.x)
        max_x = max(self.ref_pos[0], e.x)
        min_y = min(self.ref_pos[1], e.y)
        max_y = max(self.ref_pos[1], e.y)

        self.tl.append((min_x, min_y))
        self.br.append((max_x, max_y))

        self.ref_pos = None
        self._display_image()

    def _open_folder(self):
        self.root = filedialog.askdirectory(
            title='Select a directory containing videos and corresponding images')
        if len(self.root) == 0:
            return

        self.label_folder.config(text=self.root)
        self.info_path = os.path.join(self.root, self.args.info_file)
        if os.path.exists(self.info_path):
            self._load_info()

        self.img_folder = os.path.join(self.root, 'JPEGImages')
        if not os.path.exists(self.img_folder):
            messagebox.showerror('Error', 'JPEGImages folder cannot be found')

        self.annot_folder = os.path.join(self.root, 'Annotations')
        if not os.path.exists(self.annot_folder):
            os.makedirs(self.annot_folder)

        for e in os.listdir(self.img_folder):
            p = os.path.join(self.img_folder, e)
            if os.path.isdir(p):
                continue

            if e.endswith('.jpg') or e.endswith('.jpeg') or e.endswith('.png'):
                self.file_list.append(p)
                self.listbox.insert(tk.END, e)

        self._load_paired_data()

    def _update_default_name_label(self):
        self.label_default_name.config(
            text='Default name: ' + self.info['default_name'])

    def _set_default_name(self):
        if self.annot_folder is None:
            messagebox.showerror(
                'Error', 'Please set a default name after opening the folder')
            return

        default_name = simpledialog.askstring(
            'Q', 'Enter a default name of objects')

        if default_name is not None:
            self.info['default_name'] = default_name
            self._update_default_name_label()
            self._save_info()

    def _load_info(self):
        if self.info_path is None:
            return

        with open(self.info_path, 'r', encoding='utf8') as f:
            self.info = json.load(f)

        self._update_default_name_label()

    def _save_info(self):
        if self.info_path is None or len(self.file_list) == 0:
            return

        with open(self.info_path, 'w', encoding='utf8') as f:
            f.write(json.dumps(self.info, indent=4))

    def _listbox_select(self, event):
        widget = event.widget
        file_idx = int(widget.curselection()[0])
        self.info['file_idx'] = file_idx
        self._load_paired_data()

    def _construct_xml(self, img):
        data = ET.Element('annotation')

        sz = ET.SubElement(data, 'size')
        ET.SubElement(sz, 'width').text = str(img.shape[1])
        ET.SubElement(sz, 'height').text = str(img.shape[0])
        ET.SubElement(sz, 'depth').text = str(img.shape[2])

        ET.SubElement(data, 'segmented').text = '0'

        return data

    def _xml2array(self, xml):
        tl = []
        br = []
        names = []

        for e in xml.iter('object'):
            names.append(e.find('name').text)
            bb = e.find('bndbox')

            xmin = int(bb[0].text)
            ymin = int(bb[1].text)
            xmax = int(bb[2].text)
            ymax = int(bb[3].text)

            tl.append((xmin, ymin))
            br.append((xmax, ymax))

        return tl, br, names

    def _clear_xml(self, xml):
        del_list = [e for e in xml.iter('object')]
        for e in del_list:
            xml.remove(e)

        return xml

    def _array2xml(self, arr, xml):
        xml = self._clear_xml(xml)

        for tl, br, name in arr:
            obj = ET.SubElement(xml, 'object')
            ET.SubElement(obj, 'name').text = name
            ET.SubElement(obj, 'pose').text = 'Unspecified'
            ET.SubElement(obj, 'truncated').text = '0'
            ET.SubElement(obj, 'difficult').text = '0'

            bb = ET.SubElement(obj, 'bndbox')
            ET.SubElement(bb, 'xmin').text = str(tl[0])
            ET.SubElement(bb, 'ymin').text = str(tl[1])
            ET.SubElement(bb, 'xmax').text = str(br[0])
            ET.SubElement(bb, 'ymax').text = str(br[1])

        return xml

    def _load_paired_data(self, keep_annot=False):
        img_path = Path(self.file_list[self.info['file_idx']])
        self.xml_path = str(img_path.with_suffix('.xml')).replace(
            'JPEGImages', 'Annotations')

        # load image first
        stream = open(img_path, 'rb')
        buf = bytearray(stream.read())
        arr = np.asarray(buf, dtype=np.uint8)
        self.img = cv2.imdecode(arr, cv2.IMREAD_UNCHANGED)
        self.img = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)

        if keep_annot:
            self.xml = self._construct_xml(self.img)
        else:
            # load xml file
            if os.path.isfile(self.xml_path):
                self.xml = ET.parse(self.xml_path).getroot()
            else:
                self.xml = self._construct_xml(self.img)

            # convert xml to three arrays
            self.tl, self.br, self.names = self._xml2array(self.xml)

        # store width and height of original image
        self.img_width = self.img.shape[1]
        self.img_height = self.img.shape[0]

        # resize image to display properly
        self.img = cv2.resize(self.img, (self.frame_width, self.frame_height))

        self._display_image()
        self._update_file_idx()

    def _display_image(self):
        if self.img is None:
            return

        disp = self.img.copy()
        if self.cur_pos is not None:
            utils.draw_crosshair(disp, self.cur_pos)

        for i in range(len(self.names)):
            utils.draw_annot(
                disp, self.names[i], self.tl[i], self.br[i], draw_label=self.info['draw_label'])

        if self.ref_pos is not None:
            cv2.rectangle(disp, self.ref_pos, self.cur_pos, utils.G, 1)

        img = Image.fromarray(disp)
        self.disp_tk = ImageTk.PhotoImage(image=img)

        self.disp.config(image=self.disp_tk)
        self.disp.image = self.disp_tk

    def _update_file_idx(self):
        self.label_file_idx.config(
            text=f'{self.info["file_idx"] + 1} / {len(self.file_list)}')
        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(self.info['file_idx'])
        self.listbox.see(self.info['file_idx'])

    def _forward(self, event=None):
        self._export_annot_to_file()
        self.info['file_idx'] = \
            (self.info['file_idx'] + 1) % len(self.file_list)
        self._load_paired_data(keep_annot=keyboard.is_pressed('shift'))

    def _backward(self, event=None):
        self._export_annot_to_file()
        self.info['file_idx'] = self.info['file_idx'] - 1 \
            if self.info['file_idx'] > 0 else len(self.file_list) - 1
        self._load_paired_data()

    def _navigate(self, event=None):
        new_file_idx = simpledialog.askinteger(
            'Q', 'Enter the file index you want to navigate')
        if new_file_idx is None:
            return

        new_file_idx = int(new_file_idx)
        if 0 < new_file_idx < len(self.file_list):
            self._export_annot_to_file()
            self.info['file_idx'] = new_file_idx - 1
            self._load_paired_data()
        else:
            messagebox.showerror('Error', 'File index out of range')

    def _toggle_label(self, event=None):
        self.info['draw_label'] = not self.info['draw_label']
        self._display_image()

    def _clear_annot(self, event=None):
        msg_box = messagebox.askquestion(
            'Clear', 'Do you wish you clear annotation data?', icon='warning')
        if msg_box == 'yes':
            self.tl = []
            self.br = []
            self.names = []

    def _export_annot_to_file(self, event=None):
        if self.img_folder is None:
            return

        self.xml = self._array2xml(zip(self.tl, self.br, self.names), self.xml)

        with open(self.xml_path, 'w+', encoding='utf-8') as f:
            xml_str = ET.tostring(self.xml)
            xml_str = minidom.parseString(xml_str).toprettyxml()
            f.write(xml_str)

    def _save_info_and_exit(self):
        self._save_info()
        self._export_annot_to_file()
        self.tk.destroy()


def main(args):
    main_window = MainWindow(args)
    main_window.tk.mainloop()


def parse_arguments(argv):
    parser = argparse.ArgumentParser()

    parser.add_argument('--aspect_ratio', type=str, default='9:16')
    parser.add_argument('--info_file', type=str, default='info.json')

    return parser.parse_args(argv)


if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))
