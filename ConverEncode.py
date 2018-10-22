# -*- coding: utf-8 -*-

import codecs, chardet
import sys, os, fnmatch
import win32file, win32con

EncodeType = ["utf-8", "UTF-8", "GB2312", "gb2312", "GBK", "gbk", "Unicode", "ascii", "ASCII", "GB18030"]

class ConverFileEncode(object):
    def __init__(self, encoding, keyword, path):
        self.m_encoding = encoding
        self.m_keyword = keyword
        self.m_path = path
        if path == ".":
            self.m_path = os.path.abspath(path)

    def __call__(self):
        print("[__call__] function")
        self.FindConverFile()

    def isHiddenOrSystem(self, name):
        file_flag = win32file.GetFileAttributesW(name)
        is_hidden = file_flag & win32con.FILE_ATTRIBUTE_HIDDEN
        is_system = file_flag & win32con.FILE_ATTRIBUTE_SYSTEM
        # print('[isHiddenOrSystem] file_flag:%4d, is_hidden:%s, is_system:%s, name:%s' % (file_flag, is_hidden, is_system, name))
        return (is_hidden or is_system)

    def ConverFile(self, filepath):
        if (filepath == ''):
            return
        # Backup the origin file.
        #shutil.copyfile(filepath, filepath + '.bak')

        # convert file from the source encoding to target encoding
        content = codecs.open(filepath, 'rb').read()
        #print("[ConverFile] content:%s" % content)
        src_encoding = chardet.detect(content).get('encoding')
        print(("[ConverFile] filedetect:%s, src_encoding:%s, dest_encoding:%s, file:%s" % (chardet.detect(content), src_encoding, self.m_encoding, filepath)))
        new_content = content.decode(src_encoding, 'ignore').encode(self.m_encoding)
        #print("[ConverFile] new_content:%s" % new_content)
        codecs.open(filepath, 'wb').write(new_content)

    def FindConverFile(self):
        print(("[FindConverFile] path:%s" % self.m_path))
        if self.m_keyword.startswith('*'):
            for root, dirs, files in os.walk(self.m_path, topdown=True):
                if self.isHiddenOrSystem(root):
                    print(("[walkPath] root:[%s] isHiddenOrSystem Folder, overflow." % (root)))
                    continue
                for filename in files:
                    filepath = os.path.join(root, filename)
                    if os.path.isfile(filepath):
                        if (self.m_keyword == '*' or self.m_keyword == "*.*"):
                            self.ConverFile(filepath)
                        else:
                            if fnmatch.fnmatch(filepath, self.m_keyword):
                                self.ConverFile(filepath)
        else:
            filepath = os.path.join(self.m_path, self.m_keyword)
            self.ConverFile(filepath)

if __name__ == '__main__':
    if len(sys.argv) == 4:
        conver = ConverFileEncode(sys.argv[1], sys.argv[2], sys.argv[3])
        conver.FindConverFile()
    else:
        print("input error.")
        print("eg>> python ConverEncode.py \"utf-8\" \"*.py\" .")
        print("or:")
        print("eg>> python ConverEncode.py \"utf-8\" \"*.py\" \"D:\\SearchFolders\\\"")