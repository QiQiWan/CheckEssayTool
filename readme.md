# 基于百度爬虫的小作文查重器

本工具基于[BaiduSpider](https://github.com/BaiduSpider/BaiduSpider)项目，衍生出了基于百度爬虫的小作文查重工具。该工具仅用于南昌工程学院瑶湖学院的小作文查重，不作商业用途。

# 用法

## 文件结构

`essay`文件夹用于保存待查重的文章文件，支持`.doc | .docx | .txt`三种文件格式的文档。
`result`文件夹用于存放查重结果，查重结果以excel表格的形式保存，包括总表和细节表。

## 原理

连续重复字数9个以上则判定为重复。过滤部分敏感词，关键词。

## 依赖

一些python依赖包：

```
BeautifulSoup 4
requests
process
contextlib
win32com
python-docx
```