import glob
import os
from os.path import basename
import re

from wand.image import Image


__author__ = 'schien'

unprocessed_folder = os.path.join(os.getcwd(), 'unprocessed')
processed_folder = os.path.join(os.getcwd(), 'processed')

if not os.path.exists(processed_folder):
    os.mkdir(processed_folder)

glob_glob = glob.glob(os.path.abspath(unprocessed_folder) + '/*.jpg')
for i in glob_glob:
    filename = basename(i)
    num = re.sub(r'\D', "", filename)
    # dst_file_base = "house_%04d" % (int(num))
    dst_file_base = "house_%d" % (int(num))

    src_path = os.path.join(unprocessed_folder, i)

    with Image(filename=src_path) as img:
        print(img.size)
        for r in [1]:
            with img.clone() as i:
                for dim in [150, 100]:
                    # scale height to 100px and preserve aspect ratio
                    dim = 150
                    i.transform(resize='x' + str(dim))
                    if i.width > i.height:
                        h = i.width / 2
                        v = i.height / 2

                        # crop out from the center
                        print i.width, i.height, h, v,
                        left = h - dim / 2
                        top = v - dim / 2
                        print left, top
                        i.crop(left, top, width=dim, height=dim)
                        # i.resize(int(i.width * r * 150), int(i.height * r * 150))
                    dst_path = os.path.join(processed_folder, dst_file_base + '.png')
                    # dst_path = os.path.join(processed_folder, dst_file_base + '_' + str(dim) + '.png')
                    print '%s - > %s' % (src_path, dst_path)
                    i.save(filename=dst_path)



