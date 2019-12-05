# !/usr/bin/env python3
# -*- coding: utf-8 -*-

""" 文档注释 """
import time
import random
import logging
import traceback

__author__ = 'lvguangli'


def random_sleep(sleep_center: int, seg=4):
    """
    在sleep_center为中心，默认左右四分之一的时间区间内选择一个点进行sleep
    :param sleep_center: 休眠时间区间的中心
    :param seg: 休眠区间的分段
    :return:
    """
    sleep_list = [n for n in range(int(sleep_center - sleep_center / seg), int(sleep_center + sleep_center / seg + 1))]
    time.sleep(random.choice(sleep_list))


if __name__ == '__main__':
    # random_sleep(1)
    # sleep_test = 4
    # print([n for n in range(int(sleep_test - sleep_test / 4), int(sleep_test + sleep_test / 4 + 1))])
    # start = time.time()
    # random_sleep(sleep_test)
    # end = time.time()
    # print(str(start))
    # print(str(end))
    try:
        raise Exception("test")
    except Exception as e:
        traceback.print_exc()
        msg = traceback.format_exc()
        print('msg=' + msg)
    print('finish')
    exit(1)
