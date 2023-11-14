from django.conf import settings
from django.shortcuts import render, redirect
from django.http import JsonResponse
# from dateutil import parser
# Date Time
from datetime import datetime, timedelta
import time
from calendar import monthrange
# File
from django.core.files.storage import FileSystemStorage
from pathlib import Path
import glob, os, shutil
import pyexcel as p # Excel
import io

import webbrowser
import subprocess
import wget

import random

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import matplotlib.pyplot as plt
import numpy as np

from pdf2image import convert_from_path

# Const
MAX_LOAD = 100 # Maximum amount of drawing file will be load
MAX_EXCEED_DAY = 3 # Maximum day of directory in media
EXCLUDE_EXTENSIONS = ['TMP'] # File with these extension won't be load
FIRST_SPLIT = ['CT'] # If fg_code start with this, use this as directory name
POPPLER_PATH = 'C:\\poppler-22.04.0\\Library\\bin'

class Drawing:
  def __init__(self, idx, file_name, name, extension, size, fsize, src_path, dst_path, date_created, date_modified):
    self.idx = idx
    self.file_name = file_name
    self.name = name
    self.extension = extension
    self.size = size
    self.fsize = fsize
    self.src_path = src_path
    self.dst_path = dst_path
    self.date_created = date_created
    self.date_modified = date_modified

def search(request, fg_code):
    dirs = os.listdir(settings.FILES_DIR)
    if ord(get_customer_name(fg_code)[0].upper()) > 77: # if first alphabet of customer name > M letter (Middle), reverse the list
        dirs = reversed(dirs)
    for dir_name in dirs:
        is_dir = os.path.isdir(settings.FILES_DIR + '\\' + dir_name)
        if is_dir:
            files = os.listdir(settings.FILES_DIR + '\\' + dir_name)
            for file_name in files:
                if fg_code in file_name:
                    return redirect('/' + str(dir_name) + '&' + str(fg_code))
    return redirect('/None&' + str(fg_code))

def drw(request, dir, fg_code):
    dir = None if dir == 'None' or dir == '' else dir
    fg_code = None if fg_code == 'None' or fg_code == '' else fg_code
    state = 'ERROR'
    drws = []
    if dir == None and fg_code == None:
        state = 'NODATA'
    elif fg_code == None:
        state = 'NOFGCODE'
    elif dir == None:
        state = 'NODIR'
        dir = get_customer_name(fg_code)
        src_dir = settings.FILES_DIR + '\\' + str(dir)
        if os.path.exists(src_dir):
            return redirect('/' + str(dir) + '&' + str(fg_code))
    else:
        state = 'DATAFOUND'
        is_dir_created = False
        load = 0
        src_dir = settings.FILES_DIR + '\\' + str(dir)
        dst_dir = settings.MEDIA_ROOT + '\\' + str(fg_code)
        files = filter( lambda x: os.path.isfile(os.path.join(src_dir, x)) and fg_code in x, os.listdir(src_dir))
        files = sorted( files, key = lambda x: os.path.getctime(os.path.join(src_dir, x)), reverse=True)
        for file_name in files:
            is_exclude = True if get_extension(file_name) in EXCLUDE_EXTENSIONS else False
            if not is_exclude and load < MAX_LOAD:
                # Create Directory && Delete Older Directory
                if not is_dir_created:
                    create_dst_dir(fg_code)
                    del_exceed_dirs()
                    is_dir_created = True
                src_path = src_dir + '\\' + file_name
                dst_path = dst_dir + '\\' + file_name
                # Copy File
                copy(src_path, dst_path)
                # Drawing Item
                idx = load
                name = get_name(file_name)
                extension = get_extension(file_name)
                date_created = datetime.fromtimestamp(os.path.getctime(src_path))
                date_modified = datetime.fromtimestamp(os.path.getmtime(src_path))
                size = os.path.getsize(src_path)
                fsize = convert_bytes(size)
                drw = Drawing(idx, file_name, name, extension, size, fsize, src_path, dst_path, date_created, date_modified)
                drws.append(drw)
                load = load + 1
        if len(drws) == 0:
            state = 'EMPTY'
    context = {
        'state': state,
        'dir': dir,
        'fg_code': fg_code,
        'drws': drws,
    }
    return render(request, 'drw.html', context)

def img(request, fg_code, file_name):
    name = get_name(file_name)
    extension = get_extension(file_name).upper()
    # If final file is exist (PNG), delete it <Prevent Wrong Timestamp>
    is_final_exists = os.path.exists(settings.MEDIA_ROOT + '\\' + str(fg_code) + '\\' + name + ".png")
    if is_final_exists:
        os.remove(settings.MEDIA_ROOT + '\\' + str(fg_code) + '\\' + name + ".png")
    # If it's PDF file and never been coverted, convert it to JPG
    is_jpg_exists = os.path.exists(settings.MEDIA_ROOT + '\\' + str(fg_code) + '\\' + name + ".jpg")
    if extension == 'PDF' and not is_jpg_exists:
        pages = convert_from_path(settings.MEDIA_ROOT + '\\' + str(fg_code) + '\\' + file_name, poppler_path=POPPLER_PATH)
        if pages:
            file_name = name + '.jpg'
        for page in pages:
            page.save(settings.MEDIA_ROOT + '\\' + str(fg_code) + '\\' + file_name, 'JPEG')

    if extension == 'JPG' or extension == 'PDF':
        draw_watermark(request, fg_code, file_name)
    context = {
        'fg_code': fg_code,
        'file_name': file_name,
        'name': name,
        'extension': extension,
    }
    return render(request, 'img.html', context)

def draw_watermark(request, fg_code, file_name):
    file = settings.MEDIA_ROOT + '\\' + str(fg_code) + '\\' + get_name(file_name) + '.jpg'
    image = Image.open(file).copy().convert("RGBA")
    txt = Image.new('RGBA', image.size, (255,255,255,0))
    draw = ImageDraw.Draw(txt)

    width, height = image.size
    font_size = int(width / 18)
    font = ImageFont.truetype('arial.ttf', font_size)

    text_1 = "UNCONTROLLED"
    textwidth, textheight = draw.textsize(text_1, font)
    x = (width / 2) - (textwidth / 2)
    y = (height / 2) - (textheight / 2) - font_size
    draw.text((x, y), text_1, font=font, fill=(255, 0, 0, 15))

    text_2 = get_client_ip(request)
    textwidth, textheight = draw.textsize(text_2, font)
    x = (width / 2) - (textwidth / 2)
    y = (height / 2) - (textheight / 2)
    draw.text((x, y), text_2, font=font, fill=(255, 0, 0, 15))

    text_3 = datetime.now().strftime("%Y-%m-%d %H:%M")
    textwidth, textheight = draw.textsize(text_3, font)
    x = (width / 2) - (textwidth / 2)
    y = (height / 2) - (textheight / 2) + font_size
    draw.text((x, y), text_3, font=font, fill=(255, 0, 0, 15))

    combined = Image.alpha_composite(image, txt)
    combined.save(settings.MEDIA_ROOT + '\\' + str(fg_code) + '\\' + get_name(file_name) + '.png')
    return

def del_exceed_dirs():
    dirs = os.listdir(settings.MEDIA_ROOT)
    for dir in dirs:
        path = settings.MEDIA_ROOT + '\\' + dir
        date_created = datetime.fromtimestamp(os.path.getctime(path))
        if (datetime.now() - date_created).days > MAX_EXCEED_DAY:
            shutil.rmtree(path)
            print('Remove => ' + str(dir))

def create_dst_dir(fg_code):
    if os.path.exists(settings.MEDIA_ROOT + '\\' + str(fg_code)):
        shutil.rmtree(settings.MEDIA_ROOT + '\\' + str(fg_code))
    os.mkdir(settings.MEDIA_ROOT + '\\' + str(fg_code))

def get_extension(file_name):
    exts = file_name.split('.')
    return exts[-1].upper()

def get_name(file_name):
    names = file_name.split('.')
    return "".join(names[0:-1])

def get_customer_name(fg_code):
    fgs = fg_code.split('-')
    if fgs[0] in FIRST_SPLIT:
        return fgs[0]
    elif len(fgs) > 1:
        return fgs[1]
    return fgs[0]

def convert_bytes(size):
    """ Convert bytes to KB, or MB or GB"""
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return "%3.1f %s" % (size, x)
        size /= 1024.0

def copy(src, dst):
    if os.path.isdir(dst):
        dst = os.path.join(dst, os.path.basename(src))
    shutil.copyfile(src, dst)

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
