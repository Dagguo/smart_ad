#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" 文档注释 """

import requests

__author__ = 'lvguangli'
# url_templet = 'https://hammer.kikaops.com/commonutils/sendmail?fromuser=error@Kikaops.com&touser=guangli.lv@kikatech.com&message=[msg]&subject=[sbj]'


class Message:
    msg_crawler_fail = 'facebook crawler failed, please check your account and fix it'
    msg_login_fail = 'facebook login failed, please check your account and fix it'

    def __init__(self):
        self.__url = 'https://hammer.kikaops.com/commonutils/sendmail'
        self.__params = dict()
        self.__params['fromuser'] = 'error@Kikaops.com'
        self.__params['touser'] = 'guangli.lv@kikatech.com'
        self.__emails = ['guangli.lv@kikatech.com', '1214933295@qq.com']

    def send_msg(self, account, msg=msg_crawler_fail):
        subject = 'Account ' + account + ' crawler failed'
        self.__params['subject'] = subject
        self.__params['message'] = msg
        for email in self.__emails:
            self.__params['touser'] = email
            requests.get(self.__url, self.__params)


if __name__ == '__main__':
    message = Message()
    message.send_msg('1214933295@qq.com', 'fail')