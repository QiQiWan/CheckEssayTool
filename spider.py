"""基于百度爬虫的文章查重器.

    :Author: EatRice-万琪伟
    :Licence: GPL_V3
    :description: 定义了爬虫类和文章类
    """

from contextlib import redirect_stderr
from baiduspider import BaiduSpider
from process import progress
from win32com import client as wc
from keywords import keywords
import string
import docx
import os

# 要去除的符号
SymbolList = [
    " ",
    ".",
    "，",
    "。",
    "\n",
    "\r",
    "\u3000",
    "“",
    "”",
    "—",
    "-",
    ":",
    "：",
    "；",
    ";",
    "(",
    ")",
    "（",
    "）",
    "\b",
    "!",
    "?",
    "！",
    "…",
    "+",
    "、",
]


class essay:
    """
    文章类，包含文章名，内容，拆分后的句子，可用性等
    """

    name = ""
    content = ""
    sentence = []
    filepath = ""
    avaliable = False
    # 字数统计，包括中文字符和英文字母
    count = 0
    cheat = 0
    cheatinfo = {}
    

    def __init__(self, filepath):
        if not os.path.exists(filepath):
            return
        self.avaliable = True
        self.filepath = filepath
        extendname = os.path.splitext(filepath)[-1]
        self.name = os.path.splitext(filepath)[0].split("/")[-1]

        if extendname.lower() == ".txt":
            self.readtxt(filepath)
        elif extendname.lower() == ".doc":
            filepath = self.transformdoc(filepath)
            self.readdocx(filepath)
        elif extendname.lower() == ".docx":
            self.readdocx(filepath)
        else:
            print("仅支持 .txt | .doc | .docx 文件格式！")
            return

        content = self.content

        for symbol in SymbolList:
            content = content.replace(symbol, ",")

        self.sentence = content.split(",")
        count = 0
        for c in content:
            if c.isalpha() or c in string.ascii_letters:
                count = count + 1
        self.count = count

    def readtxt(self, filepath):
        with open(filepath, "r", encoding="UTF-8") as f:
            self.content = f.read()

    def readdocx(self, filepath):
        file = docx.Document(filepath)
        content = ""
        for para in file.paragraphs:
            content += para.text
        self.content = content

    def transformdoc(self, filepath):
        basedomain = os.getcwd() + '/'
        word = wc.Dispatch("Word.Application")
        doc = word.Documents.Open(basedomain + filepath)
        newpath = filepath.replace(".doc", ".docx")
        doc.SaveAs(basedomain + newpath, 12, False, "", True, "", False, False, False,
                   False)
        doc.Close()
        word.Quit()
        return newpath

    def setcheat(self, cheatinfo={}):
        cheat = 0
        for key in cheatinfo:
            cheat = cheat + len(key)
        self.cheat = cheat
        self.cheatinfo = cheatinfo

    def tocsvtable(self):
        return f"{self.filepath}, {self.count}, {self.cheat}, {int(self.cheat / self.count * 100)}%"

    def savedetail(self, savedir="result/"):
        if not os.path.exists(savedir):
            os.mkdir(savedir)
        filename = savedir + self.name + ".csv"
        if os.path.exists(filename):
            os.remove(filename)
        with open(filename, "w", encoding="utf-8-sig") as f:
            f.write("原句子, 网络重复句子, 重复长度, 来源 \n")
            for ori in self.cheatinfo:
                des = self.cheatinfo[ori]["des"]
                des = des.replace(",", "，")
                line = f'{ori}, {des}, {len(ori)}, {self.cheatinfo[ori]["url"]} \n'
                f.write(line)

    def checkessay(self, savedir="result/"):
        searchtool = spider()
        cheat = 0
        cheatinfo = {}
        print(f"开始查重文章：{self.filepath}")
        length = len(self.sentence)
        record = ""
        for i in range(length):
            # 打印进度条
            percent = int(i / length * 100) + 1
            if percent == 21:
                percent = 21
            progress(percent)
            # 检测关键词
            if self.sentence[i] in keywords:
                continue
            # 更新待检测内容
            newrecord = record + self.sentence[i]
            result = searchtool.BaiduSearch(newrecord)
            if result:
                if record in cheatinfo:
                    cheatinfo.pop(record)
                # 短语不收录
                if len(newrecord) >= 9:
                    cheatinfo[newrecord] = result
                if len(newrecord) > 100:
                    record = ""
                else:
                    record = newrecord
            else:
                record = self.sentence[i]
                result = searchtool.BaiduSearch(record)
                if result:
                    cheatinfo[record] = result
                else:
                    record = ""

        self.setcheat(cheatinfo=cheatinfo)
        self.savedetail(savedir=savedir)
        print("\n 本篇文章的统计结果为：")
        print(self.tocsvtable())

class spider:
    """
    爬虫类，定义了百度爬虫工具和搜索方法
    """

    baiduspider = BaiduSpider()
    repeat = 0

    def __init__(self):
        return

    def BaiduSearch(self, query=""):
        if len(query) < 5:
            return False  # 长度小于5的句子不检测

        result = self.baiduspider.search_web(query=query)["results"]
        if result == []:
            self.repeat += 1
            # 如果重复五次没有搜索到结果，则返回没有匹配
            if self.repeat >= 150:
                self.repeat = 0
                return False
            return self.BaiduSearch(query=query)
        for item in result:
            if item["type"] != "result":
                continue
            if not item["des"]:
                item["des"] = item["title"]
            des = item["des"]
            for symbol in SymbolList:
                des = des.replace(symbol, "")
            des = des.replace(",", "")
            if "的问题>>" in des:
                continue
            if query in des:
                return item

        return False
