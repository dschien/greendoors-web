from unittest import TestCase
import email

__author__ = 'schien'

data_zero_one = '''
'''

data_all = '''
'''

class EmailTest(TestCase):

    def test_single_msg(self):
        msg = email.message_from_string(data_all)

        for part in email.iterators.typed_subpart_iterator(msg, 'text', 'plain'):
            for body_line in email.iterators.body_line_iterator(part):
                print body_line
