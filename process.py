"""基于百度爬虫的文章查重器.

:Author: EatRice-万琪伟
:Licence: GPL_V3
:description: 定义了进度条打印方法
"""

import time
def progress(percent,width=50):
    '''进度打印功能'''
    if percent >= 100:
        percent=100
  
    show_str=('[%%-%ds]' %width) %(int(width * percent/100)*"#") #字符串拼接的嵌套使用
    print('\r%s %d%%' %(show_str,percent),end='')

