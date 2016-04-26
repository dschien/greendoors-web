import logging
from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from api.models import Message

__author__ = 'schien'

from greendoors.services.mail_service import SMTPConnection

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    args = '-f excelfile -m -b -g'
    option_list = BaseCommand.option_list + (
        make_option("-e", "--email",
                    action="store", # optional because action defaults to "store"
                    dest="sendmail",
                    help="excel file to import from ", ),
    )

    def handle(self, *args, **options):
        """
        entry method
        """
        self.stdout.write("Sending queued emails")
        if options['excelfile'] == None:
            raise CommandError('No excelfile specified')

        if options['sendmail']:
            self.stdout.write("Staring mail sending job ")
            self.send_mail()

    def send_mail(self):
        """
        send all emails that are currently queued
        """
        messages = Message.objects.filter(sent=False)

        if len(messages) == 0:
            logger.info('No messages to be sent.')
            return

        con = SMTPConnection()
        for message in messages:
            # send message
            logger.info('sending message {} from user {} to user {}'.format(message.pk, message.sender.pk,
                                                                            message.receiver.pk))
            # todo factor out, reuse instance

            con.send_email(recipient_address=message.receiver.email, subject="Greendoors Communications",
                           body=message.text)

            logger.info('Message queued.')