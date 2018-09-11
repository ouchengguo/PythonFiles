

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = ''
__author__ = 'Administrator'
__mtime__ = '2018/6/30'
# find keyword string in filter file, list line context.
"""
import sys
import os, time, fnmatch
import win32file, win32con

class SearchFile(object):
    def __init__(self, keyword, filefilter, path):
        self._path=path
        if path == '.':
            path=os.path.abspath(self._path) # 默认当前目录
        self.search_path = path
        self.search_string = keyword
        self.file_filter = filefilter

    def __call__(self):
        print("[__init__] Search string '%s' in filter '%s' path '%s' " % (self.search_string, self.file_filter, self.search_path))
        time_begin = time.time()
        file_count = self.walkPath()   # 查找带指定字符的文件
        print("[__init__] %s files searched in %0.2fsec." % (file_count, (time.time() - time_begin)))

    def isHiddenOrSystem(self, name):
        file_flag = win32file.GetFileAttributesW(name)
        is_hidden = file_flag & win32con.FILE_ATTRIBUTE_HIDDEN
        is_system = file_flag & win32con.FILE_ATTRIBUTE_SYSTEM
        #print('[isHiddenOrSystem] file_flag:%4d, is_hidden:%s, is_system:%s, name:%s' % (file_flag, is_hidden, is_system, name))
        return (is_hidden or is_system)

    def walkPath(self):
        file_count = 0
        filelist = []
        for root, dirs, files in os.walk(self.search_path, topdown=True):
            if self.isHiddenOrSystem(root):
                print("[walkPath] root:[%s] isHiddenOrSystem Folder, overflow." % (root))
                continue
            for name in files:
                filelist.append(os.path.join(root, name))
            for filename in filelist:
                if self.isHiddenOrSystem(filename):
                    print("[walkPath] filename:[%s] isHiddenOrSystem file, overflow." % (filename))
                    continue
                if os.path.isfile(filename):
                    if fnmatch.fnmatch(filename, self.file_filter):
                        self.searchStringInFile(os.path.join(root, filename))
                        file_count += 1
        return file_count

    def searchStringInFile(self, filename):
        #print("[searchStringInFile] filename %s" % (filename))
        file = open(filename, "r", encoding="utf8", errors="ignore")
        #content = file.read()
        #lines = file.readlines()  # 读取全部内容
        for linenumber,line in enumerate(file):
            #print("[searchStringInFile] the linenumber:%s,the line is %s" % (linenumber, line))
            if self.search_string in line:
                print("[searchStringInFile] %s:%s:  %s" % (filename, linenumber, line))
        file.close()

if __name__ == "__main__":
    if len(sys.argv) == 4:
        search=SearchFile(sys.argv[1], sys.argv[2], sys.argv[3])
        search()
    else:
        print("input error.")
        print("eg>> python FindStr.py \"__main__\" \"*.py\" .")
        print("or:")
        print("eg>> python FindStr.py \"__main__\" \"*.py\" \"D:\\SearchFolders\\\"")
