import inspect
import os


def handle_err(func):  # pragma: no cover
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as err:
            if bool(int(os.environ.get("DEBUG", 0))):
                raise err
            func_name = (
                func.__name__.strip("parse_").strip("_block")
                if "block" in func.__name__
                else None
            )
            if func_name is not None:
                print(
                    f"\033[33mWARNING: An error occurred while parsing the {func_name} subcomponent of BaiduSpider.{inspect.stack()[1][0].f_code.co_name}, "
                    "which is currently ignored. However, the rest of the parsing process is still being executed normally. "
                    "This is most likely an inner parse failure of BaiduSpider. For more details, please set the environment "
                    "variable `DEBUG` to `1` to see the error trace and open up a new issue at https://github.com/BaiduSpider/"
                    "BaiduSpider/issues/new?assignees=&labels=bug%2C+help+wanted&template=bug_report.md&title=%5BBUG%5D.\033[0m"
                )
            else:
                print(
                    f"\033[33mWARNING: An error occurred while executing function BaiduSpider.{inspect.stack()[1][0].f_code.co_name}, "
                    "which is currently ignored. However, the rest of the parsing process is still being executed normally. "
                    "This is most likely an inner parse failure of BaiduSpider. For more details, please set the environment "
                    "variable `DEBUG` to `1` to see the error trace and open up a new issue at https://github.com/BaiduSpider/"
                    "BaiduSpider/issues/new?assignees=&labels=bug%2C+help+wanted&template=bug_report.md&title=%5BBUG%5D.\033[0m"
                )

    return wrapper
