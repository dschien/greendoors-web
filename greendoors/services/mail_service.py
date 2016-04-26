import base64
import smtplib
from greendoors.services.oauth2_service import OAuthService

__author__ = 'schien'
import imaplib

import email


class ImapConnection(object):
    def __init__(self):
        oauth = OAuthService()
        self.email = oauth.email
        self.access_token = oauth.refresh_oauth_token()
        self.connect()
        self.select_inbox()

    def select_inbox(self):
        self.imap_conn.select('INBOX')

    def connect(self):
        # Read the config file
        auth_string = 'user=%s\1auth=Bearer %s\1\1' % (self.email, self.access_token)

        self.imap_conn = imaplib.IMAP4_SSL('imap.gmail.com')
        self.imap_conn.debug = 4
        self.imap_conn.authenticate('XOAUTH2', lambda x: auth_string)

    def read(self):
        typ, data = self.imap_conn.select('INBOX')
        # x msgs in inbox
        num_msgs = int(data[0])


    def emails_from(self, name):
        '''Search for all mail from name'''
        status, response = self.imap_conn.search(None, '(FROM "%s")' % name)
        email_ids = [e_id for e_id in response[0].split()]
        print 'Number of emails from %s: %i. IDs: %s' % (name, len(email_ids), email_ids)
        return email_ids

    def get_email(self, email_id):
        t, data = self.imap_conn.fetch(email_id, "(RFC822)")
        if t == 'OK':
            for response_part in data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_string(response_part[1])
                    for header in ['subject', 'to', 'from']:
                        print '%-8s: %s' % (header.upper(), msg[header])
                    msg_from = msg['from']
                    msg_to = msg['to']
                    varSubject = msg['subject']
                    varDate = msg['date']
                    ymd = email.utils.parsedate(varDate)[0:3]
                    print ymd
                    for part in email.iterators.typed_subpart_iterator(msg, 'text', 'plain'):
                        for body_line in email.iterators.body_line_iterator(part):
                            print body_line

    def get_emails(self, email_ids):
        data = []
        for e_id in email_ids:
            _, response = self.imap_conn.fetch(e_id, '(UID BODY[TEXT])')
            data.append(response[0][1])
        return data

    def get_subjects(self, email_ids):
        subjects = []
        for e_id in email_ids:
            _, response = self.imap_conn.fetch(e_id, '(body[header.fields (subject)])')
            subjects.append(response[0][1][9:])
        return subjects

    def get_thread(self, thread_id):
        type, data = self.imap_conn.search(None, 'TO', '"green-doors+{}@bristol.ac.uk"'.format(thread_id))
        # if not type == 'OK':
        #     raise Exception('thread search failed')
        print type
        return data

    def close(self):
        self.imap_conn.close()
        self.imap_conn.logout()


# if __name__=="__main__":
#     con = ImapConnection()
#     res = con.get_thread('1')


class SMTPConnection(object):
    def __init__(self):
        oauth = OAuthService()
        self.email = oauth.email
        self.access_token = oauth.refresh_oauth_token()

        xoauth2_string = 'user=%s\1auth=Bearer %s\1\1' % (self.email, self.access_token)
        url = "https://mail.google.com/mail/b/" + self.email + "/smtp/"

        self.conn = smtplib.SMTP('smtp.gmail.com', 587)
        self.conn.set_debuglevel(True)
        self.conn.ehlo()
        self.conn.starttls()
        self.conn.ehlo()
        self.conn.docmd('AUTH', 'XOAUTH2 ' + base64.b64encode(xoauth2_string))

    def send_email(self, recipient_address=None, subject=None, body=None, cc=None, bcc=None):
        header = 'To:' + recipient_address + '\n'
        header += 'From:' + self.email + '\n'
        if cc is not None:
            header += "CC: %s\r\n" % ",".join(cc)
        header += 'Subject:' + subject + ' \n'

        header += 'Content-Type: text/html; charset=UTF-8\n'
        msg = header + '\n ' + body + ' \n\n'
        toaddrs = [recipient_address]
        if cc is not None:
            toaddrs = toaddrs + [cc]
        if bcc is not None:
            toaddrs = toaddrs + [bcc]
        try:
            errs = self.conn.sendmail(self.email, toaddrs, msg)
        except:
            raise
        finally:
            self.conn.quit()
        return len(errs) == 0