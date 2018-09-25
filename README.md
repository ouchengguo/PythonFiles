# PythonFiles
Python实现的常用功能的实现

1、windows下搜索关键字(SearchKeyWord.py)
python3.6实现的windows下指定路径下搜索指定关键字功能实现，输出关键字所在文件名和行数；方便于开发人员查找指定关键字。

2、Print在Python2转换为Python3(PrintPython2ToPython3.py)
print写法在python2中和python3中不一样，导致编译会报错，通过该脚本，实现了自动转换。

3、解析coredump堆栈信息(stackParser)
当程序崩溃时，需要知道crash发生在哪里，crash时函数的调用栈细节等信息。Android程序崩溃时，会通过log系统输出crash时的寄存器和栈信息，部分机器会在/data/tombstones目录产生crash日志文件。将crash时产生的stack dump信息保存在stack.txt中,
ndk-stack -sym $SYMBOL_SO_PATH -dump crash.txt
arm-hisiv200-linux-addr2line -C -f -s -e android4.4.4_chromium_org/out/target/product/orange/symbols/system/lib/libsywebviewchromium.so 001cfb55
SYMBOL_SO_PATH是符号库目录，在Android源码中是out/target/product/xx/symbol/system/lib。

4、webkit中解析css配置文件（OptPraseDemo）
通过配置文件对所以的属性进行配置，python解析并生成指定格式的模板类文件。
eg: make_css_property_names.py ..\CSSProperty.in --output_dir "..\blink" --defines "\"ENABLE_EXPAND_HTML=0\""
