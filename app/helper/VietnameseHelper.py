"""app/helper/VietnameseHelper.py"""
import re
import unicodedata


class VietnameseHelper:
    """@VietnameseHelper"""

    def __init__(self):
        self.test = 'test'

    def no_accent(self, s):
        s = re.sub(u'Đ', 'D', s)
        s = re.sub(u'đ', 'd', s)
        return unicodedata.normalize('NFKD', str(s)).encode('ASCII', 'ignore')

    def no_accent_lower(self, s):
        s = s.lower()
        s = re.sub(u'đ', 'd', s)
        return unicodedata.normalize('NFKD', str(s)).encode('ASCII', 'ignore')
