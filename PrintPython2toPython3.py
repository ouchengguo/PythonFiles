import os
allFileNum = 0
def printPath(level, path):
    global allFileNum
    '''
    打印一个目录下的所有文件夹和文件
    '''
    # 所有文件夹，第一个字段是次目录的级别
    dirList = []
    # 所有文件
    fileList = []
    # 所有文件 包含路径
    filePathList = []
    # 返回一个列表，其中包含在目录条目的名称(google翻译)
    files = os.listdir(path)
    # 先添加目录级别
    dirList.append(str(level))
    for f in files:
        if(os.path.isdir(path + '/' + f)):
            # 排除隐藏文件夹。因为隐藏文件夹过多
            if(f[0] == '.'):
                pass
            else:
                # 添加非隐藏文件夹
                dirList.append(f)
        if(os.path.isfile(path + '/' + f)):
            # 添加文件
            fileList.append(f)
            filePathList.append(path + '/' + f)
    # 当一个标志使用，文件夹列表第一个级别不打印
    i_dl = 0
    for dl in dirList:
        if(i_dl == 0):
            i_dl = i_dl + 1
        else:
            # 打印至控制台，不是第一个的目录
            print ('-' * (int(dirList[0])), dl)
            # 打印目录下的所有文件夹和文件，目录级别+1
            printPath((int(dirList[0]) + 1), path + '/' + dl)
    for fl in fileList:
        # 打印文件
        print ('-' * (int(dirList[0])), fl)
        #fixPrint(fl)
        # 随便计算一下有多少个文件
        allFileNum = allFileNum + 1
    for fl in filePathList:
       fixPrint(fl)
def fixPrint(path):
    file  = open(path,"r",encoding="utf-8")
    newLines = [];
    all_the_text = file.readlines( )
    for line in all_the_text:
        index = line.find("print")
        #检查当前行是否有print 同时是否已经有()了
        if(index>=0 and line[index+5:index+8].find('(')==-1):
            #对有print的数据进行处理,
            line = line.replace("print","print (")
            if(line.find("\n")>0):
                 line =  line.replace("\n"," )" +"\n")
            else:
                line+=")"
        newLines.append(line)
    file.close()

     #直接覆盖掉原来的文件
    newFile = open(path,"w",encoding="utf-8")
    for line in newLines:
      newFile.write(line)
    newFile.close()

if __name__ == '__main__':
    printPath(1, "D:/PycharmProjects/PythonTest")