import os
import requests
import random
import _thread as thread
from uuid import uuid4

import numpy as np
import skimage
from skimage.filters import gaussian
from PIL import Image

def compress_image(image, path_original):
    size = 960, 540
    width = 960
    height = 540

    name = os.path.basename(path_original).split('.')
    first_name = os.path.join(os.path.dirname(path_original), name[0] + '.jpg')

    if image.size[0] > width and image.size[1] > height:
        image.thumbnail(size, Image.ANTIALIAS)
        image.save(first_name, quality=85)
    elif image.size[0] > width:
        wpercent = (width/float(image.size[0]))
        height = int((float(image.size[1])*float(wpercent)))
        image = image.resize((width,height), PIL.Image.ANTIALIAS)
        image.save(first_name,quality=85)
    elif image.size[1] > height:
        wpercent = (height/float(image.size[1]))
        width = int((float(image.size[0])*float(wpercent)))
        image = image.resize((width,height), Image.ANTIALIAS)
        image.save(first_name, quality=85)
    else:
        image.save(first_name, quality=85)


def convertToJPG(path_original):
    img = Image.open(path_original)
    name = os.path.basename(path_original).split('.')
    first_name = os.path.join(os.path.dirname(path_original), name[0] + '.jpg')

    if img.format == "JPEG":
        image = img.convert('RGB')
        compress_image(image, path_original)
        img.close()

    elif img.format == "GIF":
        i = img.convert("RGBA")
        bg = Image.new("RGBA", i.size)
        image = Image.composite(i, bg, i)
        compress_image(image, path_original)
        img.close()

    elif img.format == "PNG":
        try:
            image = Image.new("RGB", img.size, (255,255,255))
            image.paste(img,img)
            compress_image(image, path_original)
        except ValueError:
            image = img.convert('RGB')
            compress_image(image, path_original)
        
        img.close()

    elif img.format == "BMP":
        image = img.convert('RGB')
        compress_image(image, path_original)
        img.close()



def blur(image, x0, x1, y0, y1, sigma=1, multichannel=True):
    y0, y1 = min(y0, y1), max(y0, y1)
    x0, x1 = min(x0, x1), max(x0, x1)
    im = image.copy()
    sub_im = im[y0:y1,x0:x1].copy()
    blur_sub_im = gaussian(sub_im, sigma=sigma, multichannel=multichannel)
    blur_sub_im = np.round(255 * blur_sub_im)
    im[y0:y1,x0:x1] = blur_sub_im
    return im


class DownloadPrecheckFailed(Exception):
    pass


DOWNLOAD_MAX_SIZE = 5 * 1024 * 1024


def download(url, filename):
    r = requests.get(url, stream=True)
    # Precheck
    content_type = r.headers.get('Content-Type')
    if not content_type or content_type not in (
        'image/jpeg',
        'image/jpg',
        'image/png',
    ):
        raise DownloadPrecheckFailed('Non-image url is not supported.')
    content_length = int(r.headers.get('Content-Length', 0))
    if not content_length or content_length > DOWNLOAD_MAX_SIZE:
        raise DownloadPrecheckFailed('Size of file should be less than 5Mb.')
    downloaded_size = 0
    with open(filename, 'wb') as handler:
        for data in r.iter_content():
            handler.write(data)
            downloaded_size += len(data)
            if downloaded_size > DOWNLOAD_MAX_SIZE:
                raise DownloadPrecheckFailed('Size of file should be less than 5Mb.')
    return filename


def generate_random_filename(upload_directory, extension):
    filename = str(uuid4())
    filename = os.path.join(upload_directory, filename + "." + extension)
    return filename


def clean_me(filename):
    if os.path.exists(filename):
        os.remove(filename)


def clean_all(files):
    for me in files:
        clean_me(me)


def create_directory(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)


def get_model_bin(url, output_path):
    if not os.path.exists(output_path):
        create_directory(output_path)
        cmd = "wget -O %s %s" % (output_path, url)
        print(cmd)
        os.system(cmd)

    return output_path


#model_list = [(url, output_path), (url, output_path)]
def get_multi_model_bin(model_list):
    for m in model_list:
        thread.start_new_thread(get_model_bin, m)

