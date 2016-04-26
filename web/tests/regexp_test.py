import re
from unittest import TestCase
import tldextract

__author__ = 'schien'


class RegexpTest(TestCase):

    def test_email_indent(self):
        text = """This is a test email.
There are several lines, here.

They should be escaped.
        """

        reg = re.sub(r'\n', '\n> ', text)
        print reg

    def test_replace_line_breaks(self):
        text = """This is a test email.
        There are several lines, here.

        They should be escaped.
                """

        text = '\n' + text
        reg = re.sub(r'\r?\n', '<br>\n> ', text)
        print reg

    def test_barcode_regexp(self):
        barcode = "https://greendoors.cs.bris.ac.uk/frome2014/code/00010011"

    def test_supplier_urls(self):
        text = """Harridge Woodstoves in Shepton Mallet supplied stove and flue.  Very helpful and I'd recommend them.
                """

        urls = """
                http://www.kensaengineering.com/
                http://www.yell.com/biz/randall-of-beckington-ltd-frome-3386060/
                        """

        urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', urls)
        # print urls

        extracted = tldextract.extract(urls[0]).domain.capitalize()
        # print extracted

        track_url_pattern = "{{% trackurl '{0}' '{1}' %}}"

        out = ""

        for url in urls:
            out += track_url_pattern.format(url, tldextract.extract(url).domain.capitalize()) + "\n"
        out += text

        print out