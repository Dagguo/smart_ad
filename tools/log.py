# !/usr/bin/env python3
# -*- coding: utf-8 -*-

""" 文档注释 """

from tools import fileutils

__author__ = 'lvguangli'


class Log:
    file_level = 1
    stdout_level = 2
    mix_level = 3

    def __init__(self, error_path: str, debug_path: str, json_path: str):
        self.__error_path = error_path
        self.__debug_path = debug_path
        self.__json_path = json_path
        self.__log_level = 1

    # def __init__(self, error_path: str, debug_path: str, info_path: str, json_path: str = ''):
    #     self.__error_path = error_path
    #     self.__debug_path = debug_path
    #     self.__info_path = info_path
    #     self.__json_path = json_path
    #     if self.__json_path == '':
    #         self.__json_path = self.__info_path.replace('history', 'history/json') + '.json'
    #     self.__log_level = 1
    #

    def set_level(self, level: int):
        """
        设置log级别，目前仅支持不同的log设置相同级别
        :param level: 
        :return: 
        """
        self.__log_level = level
        if self.__log_level > 3:
            self.__log_level = 3
        return self

    def info_json(self, line):
        """
                用于记录正常的数据
                :param line:
                :return:
                """
        if self.__log_level & self.stdout_level == self.stdout_level:
            print(line)
        if self.__log_level & self.file_level == self.file_level:
            fileutils.append_line_to_file_with_timestamp(line=line, output_path=self.__json_path)

    # def info(self, line):
    #     """
    #     用于记录正常的数据
    #     :param line:
    #     :return:
    #     """
    #     if self.__log_level & self.stdout_level == self.stdout_level:
    #         print(line)
    #     if self.__log_level & self.file_level == self.file_level:
    #         fileutils.append_line_to_file_with_timestamp(line=line, output_path=self.__info_path)

    def error(self, line):
        """
        用于记录错误的数据
        :param line: 
        :return: 
        """
        if self.__log_level & self.stdout_level == self.stdout_level:
            print(line)
        if self.__log_level & self.file_level == self.file_level:
            fileutils.append_line_to_file_with_timestamp(line=line, output_path=self.__error_path)

    def debug(self, line):
        """
        用于记录debug信息
        :param line: 
        :return: 
        """
        if self.__log_level & self.stdout_level == self.stdout_level:
            print(line)
        if self.__log_level & self.file_level == self.file_level:
            fileutils.append_line_to_file_with_timestamp(line=line, output_path=self.__debug_path)

    def detail(self, line):
        print('this mothed is  closed for now')
        print(self.__log_level)
        print(line)


if __name__ == '__main__':
    # log = Log(error_path='error.log', debug_path='normal.log', info_path='info.log')
    # log.set_level(Log.file_level)
    # log.debug('test file level')
    # log.set_level(Log.stdout_level)
    # log.debug('test stdout level')
    # log.set_level(Log.mix_level)
    # log.debug('test mix level')
    up = 'İskenderun'
    low = up.lower()
    print(low)
