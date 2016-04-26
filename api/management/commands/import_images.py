import StringIO
import os
from os.path import basename
import re

from wand.image import Image
from api.models import House

__author__ = 'schien'
import logging
from optparse import make_option
from django.core.management.base import BaseCommand, CommandError

logger = logging.getLogger(__name__)


def get_class(kls):
    parts = kls.split('.')
    module = ".".join(parts[:-1])
    m = __import__(module)
    for comp in parts[1:]:
        m = getattr(m, comp)
    return m


class Command(BaseCommand):
    args = '-d imagedir'
    option_list = BaseCommand.option_list + (
        make_option("-d", "--imagedir",
                    action="store", # optional because action defaults to "store"
                    dest="imagedir",
                    help="directory to read images from", ),
    )

    def handle(self, *args, **options):

        if options['imagedir'] == None:
            raise CommandError('No imagedir specified')

        if options['imagedir']:
            self.stdout.write("Staring import from {0}".format(options['imagedir']))

            self.run(options['imagedir'])

    def run(self, imgdir):
        """
        Iterate over all fields in the type and import all fields from the json file
        """

        for i in os.listdir(imgdir):
            filename = basename(i)
            num = int(re.sub(r'\D', "", filename))

            src_path = os.path.join(imgdir, i)
            with Image(filename=src_path) as img:
                #print(img.size)
                for r in [1]:
                    with img.clone() as i:
                        # scale height to 100px and preserve aspect ratio
                        dim = 100
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

                        houses = House.objects.filter(pk=num)
                        if len(houses) == 0:
                            logger.warn("no house found with id {0}".format(num))
                            continue
                        house = houses[0]

                        output = StringIO.StringIO()
                        i.format = 'png'
                        i.save(file=output)
                        contents = output.getvalue().encode("base64")
                        output.close()

                        house.image = contents
                        house.save()