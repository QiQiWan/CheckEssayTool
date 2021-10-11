"""基于百度爬虫的文章查重器.

:Author: EatRice-万琪伟
:Licence: GPL_V3
:description: 本查重器基于百度爬虫，对文本进行重复率检测，基本原则是连续重复5字以上视为抄袭。为避免误杀，建立了关键词过滤机制，在关键词列表中的短句或短语不查重。本查重器包括三个部分：
1. essay文件夹，里面存放待查重的文件，必须为txt格式
2. result文件夹，输出查重结果，结果以excel表保存
3. keywords.py，关键词数据库，按照格式加入关键词或短语即可
4. process.py，打印进度条的方法
5. spider.py，定义了爬虫类和文章类型
6. baiduspider，开源的百度爬虫工具
"""

from spider import spider, essay
from process import progress
from keywords import keywords
import os

# 文章保存目录
essaydir = 'essay/'
# 查重结果保存目录
savedir = 'result/'

def oneprocesscheckessay(files=os.listdir(essaydir)):
    """
    单线程查重文章的方法，可以正确显示进度条，但是文章较多时速度较慢
    """
    essays = []
    for file in files:
        oneessay = essay(essaydir+file)
        if not oneessay.content:
            continue
        oneessay.checkessay()
        essays.append(oneessay)
    return essays

def multiprocesscheckessay(files=os.listdir(essaydir)):
    """
    多线程查重文章的方法，可以同时查重多篇文章，但是进度条可能不能正确显示
    """
    
if __name__=='__main__':
    files = os.listdir(essaydir)
    print('已扫描到以下文件：')
    for file in files:
        print(file) 
    
    input('输入回车键[enter]开始对以上文件进行查重，否则请直接关闭窗口！')
    
    essays = oneprocesscheckessay()
    
    filename = savedir + 'total.csv'
    if os.path.exists(filename):
        os.remove(filename)
        
        
    with open(filename, 'a') as f:
        f.write('文章文件名, 总中英文字数, 总重复字数, 重复率 \n')
        for e in essays:
            f.write(e.tocsvtable() + '\n')
            
    print('查重完成！')
    