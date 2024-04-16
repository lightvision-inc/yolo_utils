import os
import sys
import json
import shutil
import argparse
import tkinter as tk

import cv2
import numpy as np

from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
from pathlib import Path


class InputBox():
    def __init__(self):
        self.tk = None
        self.entry = None
        self.input = ''

    def show(self, master=None, img=None):
        self.tk = tk.Toplevel()

        tk.Label(self.tk, text='Enter the file index you want to navigate').pack(
            side='top', fill='x', padx=5, pady=5)

        self.entry = tk.Entry(self.tk)
        self.entry.bind('<Return>', self._ok)
        self.entry.bind('<Escape>', self._close)
        self.entry.pack(side='top', fill='x', padx=5, pady=5)
        self.entry.focus()

        tk.Button(self.tk, text='Ok', command=self._ok).pack(
            side='left', fill='x', expand=True, padx=5, pady=5)
        tk.Button(self.tk, text='Cancel', command=self._close).pack(
            side='left', fill='x', expand=True, padx=5, pady=5)

        self.tk.transient(master)
        self.tk.grab_set()
        if master is not None:
            master.wait_window(self.tk)

    def get_input(self):
        return self.input

    def _ok(self, event=None):
        self.input = self.entry.get().strip()
        self.tk.destroy()

    def _close(self, event=None):
        self.tk.destroy()


class MainWindow:
    def __init__(self, args):
        self.args = args

        self.tk = tk.Tk()
        self.tk.title('Image subsampler')

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

        frame = tk.Frame(self.tk)
        frame.pack(side='right', fill='both', expand=True)

        self.open_folder = tk.Button(
            frame, text='Open Folder', overrelief="solid", command=self._open_folder)
        self.open_folder.pack(side='top', fill='x')

        self.label_folder = tk.Label(frame)
        self.label_folder.pack(side='top', fill='x')

        self.label_file_idx = tk.Label(frame)
        self.label_file_idx.pack(side='top', fill='x')

        self.listbox = tk.Listbox(frame, selectmode='browse')
        self.listbox.pack(side='left', fill='both', expand=True)
        self.listbox.bind('<<ListboxSelect>>', self._listbox_select)

        self.scrollbar = tk.Scrollbar(frame)
        self.scrollbar.pack(side='right', fill='both')

        self.listbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.listbox.yview)

        # self.is_full_screen = False
        self.tk.bind('f', self._forward)
        self.tk.bind('d', self._backward)
        self.tk.bind('g', self._navigate)
        self.tk.bind('s', self._save)
        self.tk.protocol('WM_DELETE_WINDOW', self._save_info_and_exit)

        self.root = None
        self.info_path = None
        self.save_path = None
        self.info = {
            'file_idx': 0,
            'saved_idx': []
        }
        self.file_list = []
        self.info['file_idx'] = 0

    def _open_folder(self):
        self.root = filedialog.askdirectory(
            title='Select a directory containing videos and corresponding images'
        )
        if len(self.root) == 0:
            return

        self.label_folder.config(text=self.root)
        self.info_path = os.path.join(self.root, self.args.info_file)
        if os.path.exists(self.info_path):
            self._load_info()

        self.save_path = os.path.join(self.root, self.args.save_folder)
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)

        annot_dir = []
        for e in os.listdir(self.root):
            p = os.path.join(self.root, e)
            if not os.path.isdir(p):
                continue

            if e.endswith('_annot'):
                annot_dir.append(p)

        for d in annot_dir:
            for e in os.listdir(d):
                if e.endswith('.jpg') or e.endswith('.jpeg') or e.endswith('.png'):
                    self.file_list.append(os.path.join(d, e))
                    self.listbox.insert(tk.END, e)

        self._load_image()

    def _load_info(self):
        if self.info_path is None:
            return

        with open(self.info_path, 'r', encoding='utf8') as f:
            self.info = json.load(f)

    def _save_info(self):
        if self.info_path is None or len(self.file_list) == 0:
            return

        with open(self.info_path, 'w', encoding='utf8') as f:
            f.write(json.dumps(self.info))

    def _listbox_select(self, event):
        widget = event.widget
        file_idx = int(widget.curselection()[0])
        self.info['file_idx'] = file_idx
        self._load_image()

    def _load_image(self):
        stream = open(self.file_list[self.info['file_idx']], 'rb')
        buf = bytearray(stream.read())
        arr = np.asarray(buf, dtype=np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_UNCHANGED)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (self.frame_width, self.frame_height))

        img = Image.fromarray(img)
        self.disp_tk = ImageTk.PhotoImage(image=img)

        self.disp.config(image=self.disp_tk)
        self.disp.image = self.disp_tk

        self._update_file_idx()

    def _update_file_idx(self):
        self.label_file_idx.config(
            text=f'{self.info["file_idx"] + 1} / {len(self.file_list)}')
        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(self.info['file_idx'])
        self.listbox.see(self.info['file_idx'])

    def _forward(self, event=None):
        self.info['file_idx'] = \
            (self.info['file_idx'] + 1) % len(self.file_list)
        self._load_image()

    def _backward(self, event=None):
        self.info['file_idx'] = self.info['file_idx'] - 1 \
            if self.info['file_idx'] > 0 else len(self.file_list) - 1
        self._load_image()

    def _navigate(self, event=None):
        inputbox = InputBox()
        inputbox.show(master=self.tk)
        new_file_idx = inputbox.get_input()
        if len(new_file_idx) == 0:
            return

        try:
            new_file_idx = int(new_file_idx)
            if 0 < new_file_idx < len(self.file_list):
                self.info['file_idx'] = new_file_idx - 1
                self._load_image()
            else:
                messagebox.showerror('Error', 'File index out of range')
        except ValueError:
            messagebox.showerror('Error', 'Please enter the positive integer')

    def _save(self, event=None):
        if self.save_path is None:
            return

        file_path = self.file_list[self.info['file_idx']]
        parent = str(Path(file_path).parent).replace('_annot', '_org')
        name = Path(file_path).name

        shutil.copy(os.path.join(parent, name),
                    os.path.join(self.save_path, name))
        messagebox.showinfo('Successfully saved', name)
        self.tk.focus_force()

    def _save_info_and_exit(self):
        self._save_info()
        self.tk.destroy()


def main(args):
    main_window = MainWindow(args)
    main_window.tk.mainloop()


def parse_arguments(argv):
    parser = argparse.ArgumentParser()

    parser.add_argument('--aspect_ratio', type=str, default='9:16')
    parser.add_argument('--info_file', type=str, default='info.json')
    parser.add_argument('--save_folder', type=str, default='subsampled')

    return parser.parse_args(argv)


if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))
