import json
from api.models import Scan


__author__ = 'schien'
import logging
from optparse import make_option
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)


def get_class(kls):
    parts = kls.split('.')
    module = ".".join(parts[:-1])
    m = __import__(module)
    for comp in parts[1:]:
        m = getattr(m, comp)
    return m


class Command(BaseCommand):
    args = '-m modelname'
    option_list = BaseCommand.option_list + (
        make_option("-f", "--jsonfile",
                    action="store", # optional because action defaults to "store"
                    dest="jsonfile",
                    help="json file to import from ", ),
        make_option('-m', '--model',
                    action='store',
                    dest='model',
                    default=False,
                    help='Target model'),
    )

    def handle(self, *args, **options):

        self.stdout.write("Staring clearing up duplicates")
        # if options['jsonfile'] == None:
        #     raise CommandError('No jsonfile specified')

        # if options['model']:
        #     self.stdout.write("Staring import to model {0} from {1}".format(options['model'], options['jsonfile']))
        #     k = False
        #     if 'keep' in options:
        #         k = options['keep']
        #     self.run(options['jsonfile'], options['model'], keep=k)
        self.run()

    def run(self, jsonfile=None, model=None, keep=False):
        """
        Iterate over all fields in the type and import all fields from the json file
        """
        if jsonfile:
            json_data = open(jsonfile)
            data = json.load(json_data)

            for entry in data:
            # skip first row

                instance = get_class(model)()

                for field in instance._meta.fields:
                    logger.info('setting field {0} for instance of type {1}'.format(field, instance.__class__.__name__))
                    setattr(instance, field.name, entry[field.name])

                instance.save()

        done = False
        while not done:
            scans = Scan.objects.all()
            for scan in scans:
                unique = Scan.objects.get(user=scan.user, timestamp=scan.timestamp)
                if len(unique) > 0:
                    for i, delete in unique:
                        if i > 0:
                            unique.delete()
                    # break inner, i.e. start again with outer loop
                    break
            else:
                done = True