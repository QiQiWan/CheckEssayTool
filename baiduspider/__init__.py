"""BaiduSpider，爬取百度的利器.

:Author: Sam Zhang
:Licence: GPL_V3
:GitHub: https://github.com/samzhangjy
:GitLab: https://gitlab.com/samzhangjy
"""
import datetime
from glob import escape
import time as time_lib
from time import mktime, strptime, time
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup
from sympy import re

from baiduspider._spider import BaseSpider
from baiduspider.errors import ParseError, UnknownError
from baiduspider.parser import Parser

__all__ = ["BaiduSpider"]


class BaiduSpider(BaseSpider):
    def __init__(self) -> None:
        """爬取百度的搜索结果.

        本类的所有成员方法都遵循下列格式：

            {
                'results': <一个列表，表示搜索结果，内部的字典会因为不同的成员方法而改变>,
                'total': <一个正整数，表示搜索结果的最大页数，可能会因为搜索结果页码的变化而变化，因为百度不提供总共的搜索结果页数>
            }

        目前支持百度搜索，百度图片，百度知道，百度视频，百度资讯，百度文库，百度经验和百度百科，并且返回的搜索结果无广告。继承自``BaseSpider``。

        BaiduSpider.`search_web(self: BaiduSpider, query: str, pn: int = 1) -> dict`: 百度网页搜索

        BaiduSpider.`search_pic(self: BaiduSpider, query: str, pn: int = 1) -> dict`: 百度图片搜索

        BaiduSpider.`search_zhidao(self: BaiduSpider, query: str, pn: int = 1) -> dict`: 百度知道搜索

        BaiduSpider.`search_video(self: BaiduSpider, query: str, pn: int = 1) -> dict`: 百度视频搜索

        BaiduSpider.`search_news(self: BaiduSpider, query: str, pn: int = 1) -> dict`: 百度资讯搜索

        BaiduSpider.`search_wenku(self: BaiduSpider, query: str, pn: int = 1) -> dict`: 百度文库搜索

        BaiduSpider.`search_jingyan(self: BaiduSpider, query: str, pn: int = 1) -> dict`: 百度经验搜索

        BaiduSpider.`search_baike(self: BaiduSpider, query: str) -> dict`: 百度百科搜索
        """
        super().__init__()
        # 爬虫名称（不是请求的，只是用来表识）
        self.spider_name = "BaiduSpider"
        # 设置请求头
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36",
            "Referer": "https://www.baidu.com",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
        }
        self.parser = Parser()
        self.EMPTY = {"results": [], "pages": 0}

    def search_web(
        self, query: str, pn: int = 1, exclude: list = [], time: tuple = None
    ) -> dict:
        """百度网页搜索.

        - 简单搜索：
            >>> BaiduSpider().search_web('搜索词')
            {
                'results': [
                    {
                        'result': int, 总计搜索结果数,
                        'type': 'total'  # type用来区分不同类别的搜索结果
                    },
                    {
                        'results': [
                            'str, 相关搜索建议',
                            '...',
                            '...',
                            '...',
                            ...
                        ],
                        'type': 'related'
                    },
                    {
                        'process': 'str, 算数过程',
                        'result': 'str, 运算结果',
                        'type': 'calc'
                        # 这类搜索结果仅会在搜索词涉及运算时出现，不一定每个搜索结果都会出现的
                    },
                    {
                        'results': [
                            {
                                'author': 'str, 新闻来源',
                                'time': 'str, 新闻发布时间',
                                'title': 'str, 新闻标题',
                                'url': 'str, 新闻链接',
                                'des': 'str, 新闻简介，大部分情况为None'
                            },
                            { ... },
                            { ... },
                            { ... },
                            ...
                        ],
                        'type': 'news'
                        # 这类搜索结果仅会在搜索词有相关新闻时出现，不一定每个搜索结果都会出现的
                    },
                    {
                        'results': [
                            {
                                'cover': 'str, 视频封面图片链接',
                                'origin': 'str, 视频来源',
                                'length': 'str, 视频时长',
                                'title': 'str, 视频标题',
                                'url': 'str, 视频链接'
                            },
                            { ... },
                            { ... },
                            { ... },
                            ...
                        ],
                        'type': 'video'
                        # 这类搜索结果仅会在搜索词有相关视频时出现，不一定每个搜索结果都会出现的
                    },
                    {
                        'result': {
                            'cover': 'str, 百科封面图片/视频链接',
                            'cover-type': 'str, 百科封面类别，图片是image，视频是video',
                            'des': 'str, 百科简介',
                            'title': 'str, 百科标题',
                            'url': 'str, 百科链接'
                        },
                        'type': 'baike'
                        # 这类搜索结果仅会在搜索词有相关百科时出现，不一定每个搜索结果都会出现的
                    },
                    {
                        'result': {
                            'cover': 'str, 贴吧封面图片链接',
                            'des': 'str, 贴吧简介',
                            'title': 'str, 贴吧标题',
                            'url': 'str, 贴吧链接',
                            'followers': 'str, 贴吧关注人数（可能有汉字，如：1万）',
                            'hot': [{  # list, 热门帖子
                                'clicks': 'str, 帖子点击总数',
                                'replies': 'str, 帖子回复总数',
                                'title': 'str, 帖子标题',
                                'url': 'str, 帖子链接'
                            }],
                            'total': 'str, 贴吧总帖子数（可能有汉字，如：17万）'
                        },
                        'type': 'tieba'
                        # 这类搜索结果仅会在搜索词有相关贴吧时出现，不一定每个搜索结果都会出现的
                    },
                    {
                        'result': {
                            'blogs': [{  # list, 博客列表
                                'des': 'str, 博客简介，没有时为`None`',
                                'origin': 'str, 博客来源',
                                'tags': [  # list, 博客标签
                                    'str, 标签文字'
                                ],
                                'title': 'str, 博客标题',
                                'url': 'str, 博客链接'
                            }],
                            'title': 'str, 博客搜索标题',
                            'url': 'str, 博客搜索链接 (https://kaifa.baidu.com)'
                        },
                        'type': 'blog'
                        # 这类搜索结果仅会在搜索词有相关博客时出现，不一定每个搜索结果都会出现的
                    },
                    {
                        'result': {
                            'title': 'str, 仓库标题',
                            'des': 'str, 仓库简介',
                            'url': 'str, 仓库链接',
                            'star': int, 仓库star数,
                            'fork': int, 仓库fork数,
                            'watch': int, 仓库watch数,
                            'license': 'str, 仓库版权协议',
                            'lang': 'str, 仓库使用的编程语言',
                            'status': 'str, 仓库状态图表链接'
                        },
                        'type': 'gitee'
                        # 这类搜索结果仅会在搜索词有相关代码仓库时出现，不一定每个搜索结果都会出现的
                    },
                    {
                        'des': 'str, 搜索结果简介',
                        'origin': 'str, 搜索结果的来源，可能是域名，也可能是名称',
                        'time': 'str, 搜索结果的发布时间',
                        'title': 'str, 搜索结果标题',
                        'type': 'result',  # 正经的搜索结果
                        'url': 'str, 搜索结果链接'
                    },
                    { ... },
                    { ... },
                    { ... },
                    ...
                ],
                'total': int, 总计的搜索结果页数，可能会因为当前页数的变化而随之变化
            }

        - 带页码：
            >>> BaiduSpider().search_web('搜索词', pn=2)
            {
                'results': [ ... ],
                'total': ...
            }

        - 按需解析：
            >>> BaiduSpider().search_web('搜索词', exclude=['要屏蔽的子部件列表'])
            可选值：['news', 'video', 'baike', 'tieba', 'blog', 'gitee', 'related', 'calc']，
            分别表示：资讯，视频，百科，贴吧，博客，Gitee代码仓库，相关搜索，计算。
            当exclude=['all']时，将仅保留基本搜索结果和搜索结果总数。
            如果'all'在exclude列表里，则将忽略列表中的剩余部件，返回exclude=['all']时的结果。

        - 按时间筛选：
            >>> BaiduSpider().search_web('搜索词', time=(开始时间, 结束时间))
            其中，开始时间和结束时间均为datetime.datetime类型，或者是使用time.time()函数生成的时间戳。
            time参数也可以是以下任意一个字符串：['day', 'week', 'month', 'year']。它们分别表示：一天内、
            一周内、一月内、一年内。
            如果参数非法，BaiduSpider会忽略此次筛选。

        Args:
            query (str): 要爬取的搜索词.
            pn (int, optional): 爬取的页码. Defaults to 1.
            exclude (list, optional): 要屏蔽的控件. Defaults to [].

        Returns:
            dict: 爬取的返回值和搜索结果
        """
        error = None
        result = self.EMPTY
        # 按需解析
        if "all" in exclude:
            exclude = [
                "news",
                "video",
                "baike",
                "tieba",
                "blog",
                "gitee",
                "calc",
                "related",
            ]
        # 按时间筛选
        if type(time) == str:
            to = datetime.datetime.now()
            from_ = datetime.datetime(
                to.year, to.month, to.day, to.hour, to.minute, to.second, to.microsecond
            )
            if time == "day":
                from_ += datetime.timedelta(days=-1)
            elif time == "week":
                from_ += datetime.timedelta(days=-7)
            elif time == "month":
                from_ += datetime.timedelta(days=-31)
            elif time == "year":
                from_ += datetime.timedelta(days=-365)
        elif type(time) == tuple or type(time) == list:
            from_ = time[0]
            to = time[1]
        else:
            to = from_ = None
        results = {}
        if type(to) == datetime.datetime and type(from_) == datetime.datetime:
            FORMAT = "%Y-%m-%d %H:%M:%S"
            to = int(time_lib.mktime(time_lib.strptime(to.strftime(FORMAT), FORMAT)))
            from_ = int(
                time_lib.mktime(time_lib.strptime(from_.strftime(FORMAT), FORMAT))
            )
        try:
            text = quote(query, "utf-8")
            url = "https://www.baidu.com/s?wd=%s&pn=%d" % (text, (pn - 1) * 10)
            if to is not None and from_ is not None:
                url += "&gpc=" + quote(f"stf={from_},{to}|stftype=2")
            content = self._get_response(url)
            results = self.parser.parse_web(content, exclude=exclude)
        except Exception as err:
            error = err
        finally:
            # self._handle_error(error, "BaiduSpider", "parse-web")
            if 'results' in results.keys() and 'pages' in results.keys():
                return {"results": results["results"], "total": results["pages"]}
            else:
                if error:
                    results['res'] = False
                return {"results": {}, "total": {}}

    def search_pic(self, query: str, pn: int = 1) -> dict:
        """百度图片搜索.

        - 实例：
            >>> BaiduSpider().search_pic('搜索词')
            {
                'results': [
                    {
                        'host': 'str, 图片来源域名',
                        'title': 'str, 图片标题',
                        'url': 'str, 图片链接'
                    },
                    { ... },
                    { ... },
                    { ... },
                    ...
                ],
                'total': int, 搜索结果总计页码，可能会变化
            }

        - 带页码的搜索：
            >>> BaiduSpider().search_pic('搜索词', pn=2)
            {
                'results': [ ... ],
                'total': ...
            }

        Args:
            query (str): 要爬取的query
            pn (int, optional): 爬取的页码. Defaults to 1.

        Returns:
            dict: 爬取的搜索结果
        """
        error = None
        result = self.EMPTY
        try:
            url = "http://image.baidu.com/search/flip?tn=baiduimage&word=%s&pn=%d" % (
                quote(query),
                (pn - 1) * 20,
            )
            content = self._get_response(url)
            result = self.parser.parse_pic(content)
            result = result if result is not None else self.EMPTY
        except Exception as err:
            error = err
        finally:
            self._handle_error(error)
        return {"results": result["results"], "total": result["pages"]}

    def search_zhidao(self, query: str, pn: int = 1) -> dict:
        """百度知道搜索.

        - 普通搜索：
            >>> BaiduSpider().search_zhidao('搜索词')
            {
                'results': [
                    {
                        'count': int, 回答总数,
                        'date': 'str, 发布日期',
                        'des': 'str, 简介',
                        'title': 'str, 标题',
                        'url': 'str, 链接'
                    },
                    { ... },
                    { ... },
                    { ... },
                    ...
                ],
                'total': int, 搜索结果最大页数，可能会变化
            }

        - 带页码的搜索：
            >>> BaiduSpider().search_zhidao('搜索词', pn=2)  # `pn` !!
            {
                'results': [ ... ],
                'total': ...
            }

        Args:
            query (str): 要搜索的query
            pn (int, optional): 搜索结果的页码. Defaults to 1.

        Returns:
            dict: 搜索结果以及总页码
        """
        error = None
        result = self.EMPTY
        try:
            url = (
                "https://zhidao.baidu.com/search?lm=0&rn=10&fr=search&pn=%d&word=%s"
                % ((pn - 1) * 10, quote(query))
            )
            source = requests.get(url, headers=self.headers)
            # 转化编码
            source.encoding = "gb2312"
            code = source.text
            result = self.parser.parse_zhidao(code)
            result = result if result is not None else self.EMPTY
        except Exception as err:
            error = err
        finally:
            if error:
                self._handle_error(error)
        return {"results": result["results"], "total": result["pages"]}

    def search_video(self, query: str, pn: int = 1) -> dict:
        """百度视频搜索.

        - 普通搜索：
            >>> BaiduSpider().search_video('搜索词')
            {
                'results': [
                    {
                        'img': 'str, 视频封面图片链接',
                        'time': 'str, 视频时长',
                        'title': 'str, 视频标题',
                        'url': 'str, 视频链接'
                    },
                    { ... },
                    { ... },
                    { ... },
                    ...
                'total': int, 搜索结果最大页数，可能因搜索页数改变而改变
            }

        - 带页码：
            >>> BaiduSpider().search_video('搜索词', pn=2)  # <=== `pn`
            {
                'results': [ ... ],
                'total': ...
            }

        Args:
            query (str): 要搜索的query
            pn (int, optional): 搜索结果的页码. Defaults to 1.

        Returns:
            dict: 搜索结果及总页码
        """
        error = None
        result = self.EMPTY
        try:
            url = (
                "http://v.baidu.com/v?no_al=1&word=%s&pn=%d&ie=utf-8&db=0&s=0&fbl=800"
                % (quote(query), (60 if pn == 2 else (pn - 1) * 20))
            )
            # 获取源码
            source = requests.get(url, headers=self.headers)
            code = self._minify(source.text)
            result = self.parser.parse_video(code)
            result = result if result is not None else self.EMPTY
        except Exception as err:
            error = err
        finally:
            if error:
                self._handle_error(error)
        return {"results": result["results"], "total": result["pages"]}

    def search_news(self, query: str, pn: int = 1) -> dict:
        """百度资讯搜索.

        - 获取资讯搜索结果：
            >>> BaiduSpider().search_news('搜索词')
            {
                'results': [
                    {
                        'author': 'str, 资讯来源（作者）',
                        'date': 'str, 资讯发布时间',
                        'des': 'str, 资讯简介',
                        'title': 'str, 资讯标题',
                        'url': 'str, 资讯链接'
                    },
                    { ... },
                    { ... },
                    { ... },
                    ...
                ],
                'total': int, 搜索结果最大页码，可能会因为当前页数变化而变化
            }

        - 带页码：
            >>> BaiduSpider().search_news('搜索词', pn=2)
            {
                'results': [ ... ],
                'total': ...
            }

        Args:
            query (str): 搜索query
            pn (int, optional): 搜索结果的页码. Defaults to 1.

        Returns:
            dict: 爬取的搜索结果与总页码。
        """
        error = None
        result = self.EMPTY
        try:
            url = "https://www.baidu.com/s?rtt=1&bsst=1&tn=news&word=%s&pn=%d" % (
                quote(query),
                (pn - 1) * 10,
            )
            # 源码
            source = requests.get(url, headers=self.headers)
            # 压缩
            code = self._minify(source.text)
            result = self.parser.parse_news(code)
            result = result if result is not None else self.EMPTY
        except Exception as err:
            error = err
        finally:
            if error:
                self._handle_error(error)
        return {"results": result["results"], "total": result["pages"]}

    def search_wenku(self, query: str, pn: int = 1) -> dict:
        """百度文库搜索.

        - 普通搜索：
            >>> BaiduSpider().search_wenku('搜索词')
            {
                'results': [
                    {
                        'date': 'str, 文章发布日期',
                        'des': 'str, 文章简介',
                        'downloads': int, 文章下载量,
                        'pages': int, 文章页数,
                        'title': 'str, 文章标题',
                        'type': 'str, 文章格式，为全部大写字母',
                        'url': 'str, 文章链接'
                    },
                    { ... },
                    { ... },
                    { ... },
                    ...
                ],
                'total': int, 总计搜索结果的页数
            }

        - 带页码的搜索：
            >>> BaiduSpider().search_wenku('搜索词', pn=2)
            {
                'results': [ ... ],
                'total': ...
            }

        Args:
            query (str): 要搜索的query
            pn (int, optional): 搜索的页码. Defaults to 1.

        Returns:
            dict: 搜索结果和总计页数
        """
        error = None
        result = self.EMPTY
        try:
            url = "https://wenku.baidu.com/search?word=%s&pn=%d" % (
                quote(query),
                (pn - 1) * 10,
            )
            source = requests.get(url, headers=self.headers)
            source.encoding = "gb2312"
            code = self._minify(source.text)
            result = self.parser.parse_wenku(code)
            result = result if result is not None else self.EMPTY
        except Exception as err:
            error = err
        finally:
            if error:
                self._handle_error(error)
        return {"results": result["results"], "total": result["pages"]}

    def search_jingyan(self, query: str, pn: int = 1) -> dict:
        """百度经验搜索.

        - 例如：
            >>> BaiduSpider().search_jingyan('关键词')
            {
                'results': [
                    {
                        'title': 'str, 经验标题',
                        'url': 'str, 经验链接',
                        'des': 'str, 经验简介',
                        'date': 'str, 经验发布日期',
                        'category': 'str, 经验分类',
                        'votes': int, 经验的支持票数
                    },
                    { ... },
                    { ... },
                    { ... },
                    ...
                ],
                'total': int, 总计搜索结果页数
            }

        - 带页码的：
            >>> BaiduSpider().search_jingyan('搜索词', pn=2) # `pn` 是页码
            {
                'results': [ ... ],
                'total': ...
            }

        Args:
            query (str): 要搜索的关键词
            pn (int, optional): 搜索结果的页码. Defaults to 1.

        Returns:
            dict: 搜索结果以及总计的页码.
        """
        error = None
        result = self.EMPTY
        try:
            url = "https://jingyan.baidu.com/search?word=%s&pn=%d&lm=0" % (
                quote(query),
                (pn - 1) * 10,
            )
            source = requests.get(url, headers=self.headers)
            code = self._minify(source.text)
            result = self.parser.parse_jingyan(code)
            result = result if result is not None else self.EMPTY
        except Exception as err:
            error = err
        finally:
            if error:
                self._handle_error(error)
        return {"results": result["results"], "total": result["pages"]}

    def search_baike(self, query: str) -> dict:
        """百度百科搜索.

        - 使用方法：
            >>> BaiduSpider().search_baike('搜索词')
            {
                'results': {
                    [
                        'title': 'str, 百科标题',
                        'des': 'str, 百科简介',
                        'date': 'str, 百科最后更新时间',
                        'url': 'str, 百科链接'
                    ],
                    [ ... ],
                    [ ... ],
                    [ ... ]
                },
                'total': int, 搜索结果总数
            }

        Args:
            query (str): 要搜索的关键词

        Returns:
            dict: 搜索结果和总页数
        """
        error = None
        result = self.EMPTY
        try:
            url = "https://baike.baidu.com/search?word=%s" % quote(query)
            source = requests.get(url, headers=self.headers)
            code = self._minify(source.text)
            result = self.parser.parse_baike(code)
            result = result if result is not None else self.EMPTY
        except Exception as err:
            error = err
        finally:
            if error:
                self._handle_error(error)
        return {"results": result["results"], "total": result["pages"]}
