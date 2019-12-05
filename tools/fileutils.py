# !/usr/bin/env python3
# -*- coding: utf-8 -*-

""" 文档注释 """
import os
import time
import platform
from pyspark import SparkConf
from pyspark import SparkContext
__author__ = 'lvguangli'


def append_line_to_file_with_timestamp(line: str, output_path: str):
    """
    将line写入到文件file,会在行首添加时间戳
    :param line: 待写入的数据行,如果line不包括换行符，自动追加换行符
    :param output_path: 目标写入文件
    :return: 
    """
    fm_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    line_with_timestamp = fm_time + "\t" + line
    append_line_to_file(line=line_with_timestamp, output_path=output_path)


def append_line_to_file(line: str, output_path: str):
    """
    将line写入到文件file
    :param line: 待写入的数据行,如果line不包括换行符，自动追加换行符
    :param output_path: 目标写入文件
    :return: 
    """
    last_slash = output_path.rfind('/')
    output_dir = output_path[0:last_slash]
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    with open(output_path, 'a') as output:
        output.write(line)
        if line[-1] != '\n':
            output.write('\n')


def read_lines_from_file(input_path: str):
    """
    从file读取数据，返回list
    :param input_path: 源数据文件路径
    :return: 
    """
    if platform.system() == 'Linux' and input_path.startswith('hdfs'):
        conf = SparkConf().setAppName("read facebook user info from hdfs") \
            .set('spark.driver.cores', 1) \
            .set('spark.driver.memory', '1g') \
            .set('spark.executor.memory', '2g') \
            .set('spark.cores.max', 2)
        sc = SparkContext(conf=conf)
        lines = sc.textFile(input_path).collect()
        sc.stop()
    else:  # Darwin read from local
        with open(input_path, 'r') as input_file:
            lines = input_file.readlines()

    return lines
