# !/usr/bin/env python3
# -*- coding: utf-8 -*-

""" 文档注释 """
import platform
import time
import random

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.remote.webelement import WebElement

from tools import sleep
from tools.log import Log
from tools import countrycode
from urllib.parse import quote

__author__ = 'lvguangli'


class FacebookCrawler:
    """
    目前仅支持爬取用户的简介信息，其他部分待扩展
    初始化对象时自动登录到facebook，支持选择浏览器UA和初始化时的sleep以及后期访问时sleep修改
    get_user_info 方法返回用户主页的简介部分的文字信息
    暂时不考虑使用代理及代理自动切换功能，因为facebook对异地登录敏感
    """
    __init = False
    __login = False
    __double = 2
    __facebook_homepage = 'https://www.facebook.com/'
    __user_agents = {
        'safari': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/604.4.7 (KHTML, like Gecko) Version/11.0.2 Safari/604.4.7'
        ,
        'chrome': 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36'
        , 'firefox': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:57.0) Gecko/20100101 Firefox/57.0'
        ,
        'edge': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:57.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2486.0 Safari/537.36 Edge/13.10586'
        ,
        'opera': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.98 Safari/537.36 OPR/44.0.2510.857 (Edition Baidu)'
    }
    __ips = ['172.31.11.2:8128'
             # , '172.31.22.225:8128', '172.31.30.43:8128'
             # {'httpProxy':'https://172.31.11.2:8128'},
             # {'httpProxy':'https://172.31.22.225:8128'},
             # {'httpProxy': 'https://172.31.30.43:8128'},
             # {'httpProxy': 'https://172.31.20.140:8128'},
             # {'httpProxy': 'https://172.31.25.67:8128'},
             # {'httpProxy': 'https://172.31.26.207:8128'},
             # {'httpProxy': 'https://172.31.19.236:8128'},
             # {'httpProxy': 'https://172.31.16.161:8128'},
             # {'httpProxy': 'https://172.31.28.19:8128'},
             # {'httpProxy': 'https://172.31.36.52:8128'},
             # {'httpProxy': 'https://172.31.12.245:8128'},
             # {'httpProxy': 'https://172.31.38.117:8128'},
             # {'httpProxy': 'https://172.31.1.17:8128'},
             # {'httpProxy': 'https://172.31.19.172:8128'},
             # {'httpProxy': 'https://172.31.4.25:8128'},
             # {'httpProxy': 'https://172.31.4.26:8128'},
             # 'https://172.31.44.142:8128'
             ]
    __dc = {
        'safari': DesiredCapabilities.SAFARI.copy()
        , 'chrome': DesiredCapabilities.CHROME.copy()
        , 'firefox': DesiredCapabilities.FIREFOX.copy()
        , 'edge': DesiredCapabilities.EDGE.copy()
        , 'opera': DesiredCapabilities.OPERA.copy()
    }
    __chrome_uas_bak = [
        'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36'
        ,
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1664.3 Safari/537.36'
        , 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.16 Safari/537.36'
        , 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1623.0 Safari/537.36'
        , 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.17 Safari/537.36'
        ,
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36'
    ]

    def __generate_browser_desired_capabilities(self, browser: str):
        """
        生成浏览器模拟参数
        :param browser: 浏览器类型
        :return: desired_capabilities对象
        """
        desired_capabilities = self.__dc[browser]

        headers = {'Accept': '*/*',
                   # 'accept-encoding': 'gzip, deflate, br',
                   'Accept-Language': 'en-US,en;q=0.8',
                   'Cache-Control': 'max-age=0',
                   'Connection': 'keep-alive',
                   }

        for key in headers:
            desired_capabilities['phantomjs.page.customHeaders.{}'.format(key)] = headers[key]

        desired_capabilities['phantomjs.page.settings.userAgent'] = (self.__user_agents[browser])
        desired_capabilities['javascriptEnabled'] = True
        if 'platform' not in desired_capabilities:
            desired_capabilities['platform'] = 'MAC'
        if browser == 'safari':
            desired_capabilities['version'] = '11.0.2'
        # 不载入图片，爬页面速度会快很多
        desired_capabilities["phantomjs.page.settings.loadImages"] = False
        return desired_capabilities
        # 利用DesiredCapabilities(代理设置)参数值, 提供的IP为线上服务器IP，所以本机不能使用
        # proxy = webdriver.Proxy()
        # proxy.proxy_type = ProxyType.MANUAL
        # proxy.http_proxy = random.choice(self.__ips)
        # proxy.add_to_capabilities(self.__desired_capabilities)

    def __get_desired_capabilities_by_param(self, browser):
        """
        通过参数选择相应的dc
        :param browser: 空或者浏览器类型字符串或者dc的词典dict
        :return: 
        """
        if browser is None:
            desired_capabilities = self.__generate_browser_desired_capabilities(browser='safari')
        elif isinstance(browser, dict):
            desired_capabilities = browser
        else:
            desired_capabilities = self.__generate_browser_desired_capabilities(browser=browser)
        return desired_capabilities

    def __init__(self, user_name: str, password: str, log: Log, browser=None, sleep_default: int = 1):
        self.__request_num = 0
        self.__request_max = 10
        self.__user_name = user_name
        self.__password = password
        # 设置日志对象，用于生成日志
        self.__log = log
        self.__sleep = sleep_default
        self.__desired_capabilities = self.__get_desired_capabilities_by_param(browser=browser)
        self.__browser = None
        self.__service_args = [
            '--proxy=' + random.choice(self.__ips),
            '--proxy-type=https',
        ]

    def init(self):
        if platform.system() == 'Linux':
            self.__browser = webdriver.PhantomJS(
                executable_path='/home/lvguangli/project/phantomjs-2.1.1-linux-x86_64/bin/phantomjs',
                desired_capabilities=self.__desired_capabilities, service_args=self.__service_args)
        elif platform.system() == 'Darwin':
            self.__browser = webdriver.PhantomJS(desired_capabilities=self.__desired_capabilities)
        else:
            self.__browser = webdriver.PhantomJS()
        self.__init = True

    def is_init(self):
        return self.__init

    def login_facebook(self):
        """
        登录到facebook
        :return: 
        """
        self.__browser.get(self.__facebook_homepage)
        # self.__log.debug("login_facebook open home page")
        sleep.random_sleep(self.__sleep * self.__double)
        # self.get_browser().save_screenshot('before_login.png')
        self.__browser.find_element_by_id('email').clear()
        self.__browser.find_element_by_id('pass').clear()
        self.__browser.find_element_by_id('email').send_keys(self.__user_name)
        self.__browser.find_element_by_id('pass').send_keys(self.__password)
        self.__browser.find_element_by_id('loginbutton').click()
        # self.__log.debug("login_facebook click")
        sleep.random_sleep(self.__sleep * self.__double)
        self.__login = True

    def __overview(self, nav_overview: WebElement, info_dict: dict):
        # nav_overview = _5pwrs[0]
        # 默认页面是overview，所以不需要点击事件
        # nav_overview.click()
        sleep.random_sleep(self.__sleep)
        # 收集概览信息
        pagelet_timeline_medley_about = self.__browser.find_element_by_id('pagelet_timeline_medley_about')
        lines = pagelet_timeline_medley_about.text.split('\n')
        # print(lines)
        context = lines[11:len(lines)]
        info_dict['nav_overview'] = '\n'.join(context)

    def __edu_work(self, nav_edu_work: WebElement, info_dict: dict):
        # nav_edu_work = _5pwrs[1]
        nav_edu_work.click()
        sleep.random_sleep(self.__sleep)
        pagelet_timeline_medley_about = self.__browser.find_element_by_id('pagelet_timeline_medley_about')
        lines = pagelet_timeline_medley_about.text.split('\n')
        context = lines[11:len(lines)]
        info_dict['nav_edu_work'] = '\n'.join(context)
        try:
            pagelet_eduwork = self.__browser.find_element_by_id('pagelet_eduwork')
            info_dict['pagelet_eduwork'] = pagelet_eduwork.text
        except NoSuchElementException:
            self.__log.debug('exception: pagelet_eduwork not find')

    def __places(self, nav_places: WebElement, info_dict: dict):
        # nav_places = _5pwrs[2]
        nav_places.click()
        sleep.random_sleep(self.__sleep)
        pagelet_timeline_medley_about = self.__browser.find_element_by_id('pagelet_timeline_medley_about')
        lines = pagelet_timeline_medley_about.text.split('\n')
        context = lines[11:len(lines)]
        info_dict['nav_places'] = '\n'.join(context)
        try:
            pagelet_hometown = self.__browser.find_element_by_id('pagelet_hometown')
            info_dict['pagelet_hometown'] = pagelet_hometown.text
        except NoSuchElementException:
            self.__log.debug('exception: pagelet_hometown not find')
        try:
            current_city = self.__browser.find_element_by_id('current_city')
            info_dict['current_city'] = current_city.text
        except NoSuchElementException:
            self.__log.debug('exception: current_city not find')
        try:
            hometown = self.__browser.find_element_by_id('hometown')
            info_dict['hometown'] = hometown.text
        except NoSuchElementException:
            self.__log.debug('exception: hometown not find')

    def __contact_basic(self, nav_contact_basic: WebElement, info_dict: dict):
        # nav_contact_basic = _5pwrs[3]
        nav_contact_basic.click()
        sleep.random_sleep(self.__sleep)
        pagelet_timeline_medley_about = self.__browser.find_element_by_id('pagelet_timeline_medley_about')
        lines = pagelet_timeline_medley_about.text.split('\n')
        context = lines[11:len(lines)]
        info_dict['nav_contact_basic'] = '\n'.join(context)
        try:
            pagelet_contact = self.__browser.find_element_by_id('pagelet_contact')
            info_dict['pagelet_contact'] = pagelet_contact.text
        except NoSuchElementException:
            self.__log.debug('exception: pagelet_contact not find')
        try:
            pagelet_basic = self.__browser.find_element_by_id('pagelet_basic')
            info_dict['pagelet_basic'] = pagelet_basic.text
        except NoSuchElementException:
            self.__log.debug('exception: pagelet_basic not find')

    def __all_relationships(self, nav_all_relationships: WebElement, info_dict: dict):
        # nav_all_relationships = _5pwrs[4]
        nav_all_relationships.click()
        sleep.random_sleep(self.__sleep)
        pagelet_timeline_medley_about = self.__browser.find_element_by_id('pagelet_timeline_medley_about')
        lines = pagelet_timeline_medley_about.text.split('\n')
        context = lines[11:len(lines)]
        info_dict['nav_all_relationships'] = '\n'.join(context)
        try:
            pagelet_relationships = self.__browser.find_element_by_id('pagelet_relationships')
            info_dict['pagelet_relationships'] = pagelet_relationships.text
        except NoSuchElementException:
            self.__log.debug('exception: pagelet_relationships not find')

    def __about(self, nav_about: WebElement, info_dict: dict):
        # nav_about = _5pwrs[5]
        nav_about.click()
        sleep.random_sleep(self.__sleep)
        pagelet_timeline_medley_about = self.__browser.find_element_by_id('pagelet_timeline_medley_about')
        lines = pagelet_timeline_medley_about.text.split('\n')
        context = lines[11:len(lines)]
        info_dict['nav_about'] = '\n'.join(context)
        try:
            pagelet_bio = self.__browser.find_element_by_id('pagelet_bio')
            info_dict['pagelet_bio'] = pagelet_bio.text
        except NoSuchElementException:
            self.__log.debug('exception: pagelet_bio not find')
        try:
            pagelet_pronounce = self.__browser.find_element_by_id('pagelet_pronounce')
            info_dict['pagelet_pronounce'] = pagelet_pronounce.text
        except NoSuchElementException:
            self.__log.debug('exception: pagelet_pronounce not find')
        try:
            pagelet_nicknames = self.__browser.find_element_by_id('pagelet_nicknames')
            info_dict['pagelet_nicknames'] = pagelet_nicknames.text
        except NoSuchElementException:
            self.__log.debug('exception: pagelet_nicknames not find')
        try:
            pagelet_quotes = self.__browser.find_element_by_id('pagelet_quotes')
            info_dict['pagelet_quotes'] = pagelet_quotes.text
        except NoSuchElementException:
            self.__log.debug('exception: pagelet_quotes not find')

    def __year_overviews(self, nav_year_overviews: WebElement, info_dict: dict):
        # nav_year_overviews = _5pwrs[6]
        nav_year_overviews.click()
        sleep.random_sleep(self.__sleep)
        pagelet_timeline_medley_about = self.__browser.find_element_by_id('pagelet_timeline_medley_about')
        lines = pagelet_timeline_medley_about.text.split('\n')
        context = lines[11:len(lines)]
        info_dict['nav_year_overviews'] = '\n'.join(context)
        fb_profile_edit_experiences = self.__browser.find_element_by_class_name('fbProfileEditExperiences')
        try:
            info_dict['fbProfileEditExperiences'] = fb_profile_edit_experiences.text
        except NoSuchElementException:
            self.__log.debug('exception: fbProfileEditExperiences not find')

    def is_login(self):
        return self.__login

    def get_browser(self):
        return self.__browser

    def set_sleep(self, sleep_default):
        """
        设置每次网页操作后服务器响应时的等待时间
        :param sleep_default: example 1
        :return: 
        """
        self.__sleep = sleep_default

    def restart(self, cause='request max, try to restart facebook crawler'):
        """
        防止phantomJS 请求次数过多导致缓存大量页面把内存耗尽，每次重启会释放（基于java回收）所有页面内存
        :return: 
        """
        self.__log.debug(cause)
        self.__request_num = 0
        # cookies = self.__browser.get_cookies()
        self.__browser.quit()
        self.__login = False
        if platform.system() == 'Linux':
            self.__browser = webdriver.PhantomJS(
                executable_path='/home/lvguangli/project/phantomjs-2.1.1-linux-x86_64/bin/phantomjs',
                desired_capabilities=self.__desired_capabilities, service_args=self.__service_args)
        elif platform.system() == 'Darwin':
            self.__browser = webdriver.PhantomJS(desired_capabilities=self.__desired_capabilities)
        else:
            self.__browser = webdriver.PhantomJS()
        sleep.random_sleep(self.__sleep * self.__double)
        self.login_facebook()
        sleep.random_sleep(self.__sleep * self.__double)

    def destroy(self):
        if self.__init:
            self.__browser.quit()

    def __collect(self, info_dict: dict):
        # 收集主页简介
        try:
            intro_container_id = self.__browser.find_element_by_id('intro_container_id')
            info_dict['intro_container_id'] = intro_container_id.text
        except NoSuchElementException:
            self.__log.debug('this user may not have intro_container_id')
        # 定位简介
        fb_timeline_headlines = self.__browser.find_element_by_id('fbTimelineHeadline').find_elements_by_class_name(
            '_6-6')
        about = fb_timeline_headlines[1]
        # 打开简介
        about.click()
        sleep.random_sleep(self.__sleep * self.__double)
        # self.__browser.save_screenshot('about.png')
        _5pwrs = self.__browser.find_elements_by_class_name('_5pwr')
        # print(_5pwrs)
        ###################################################################
        nav_overview = _5pwrs[0]
        self.__overview(nav_overview=nav_overview, info_dict=info_dict)
        # return info_dict
        ###################################################################
        nav_edu_work = _5pwrs[1]
        self.__edu_work(nav_edu_work=nav_edu_work, info_dict=info_dict)
        ###################################################################
        nav_places = _5pwrs[2]
        self.__places(nav_places=nav_places, info_dict=info_dict)
        ###################################################################
        nav_contact_basic = _5pwrs[3]
        self.__contact_basic(nav_contact_basic=nav_contact_basic, info_dict=info_dict)
        ###################################################################
        nav_all_relationships = _5pwrs[4]
        self.__all_relationships(nav_all_relationships=nav_all_relationships, info_dict=info_dict)
        ###################################################################
        nav_about = _5pwrs[5]
        self.__about(nav_about=nav_about, info_dict=info_dict)
        ###################################################################
        nav_year_overviews = _5pwrs[6]
        self.__year_overviews(nav_year_overviews=nav_year_overviews, info_dict=info_dict)
        return info_dict

    def open_homepage_by_url(self, user_homepage: str):
        """
        抓取用户主页的简介信息
        :param user_homepage: 用户主页
        :return: dict
        """
        self.__request_num = self.__request_num + 1
        if self.__request_num >= self.__request_max:
            self.restart()
        info_dict = dict()
        # 打开主页
        self.__browser.get(user_homepage)
        sleep.random_sleep(self.__sleep)
        info_dict = self.__collect(info_dict)
        return info_dict

    def __find_user_element(self, browse_results_container: list, filter: str):
        containers = list()
        for container in browse_results_container:
            try:
                desc = container.find_element_by_class_name('_42ef').text.lower()
                if filter.lower() in desc:
                    containers.append(container)
            except:
                self.__log.debug("no desc")
        return containers
        # may_user_element = container.find_element_by_class_name('_32mo')
        # containers_name = list()
        # for container in browse_results_container:
        #     may_user_element = container.find_element_by_class_name('_32mo')
        #     web_name = may_user_element.text
        #     if web_name.lower() == name.lower():
        #         containers_name.append(container)
        # print('len(containers)' + str(len(containers_name)))
        # if len(containers_name) == 0:
        #     return info_dict
        # elif len(containers_name) == 1:
        #     may_user_element = containers_name[0].find_element_by_class_name('_32mo')
        # else:
        #     for container in containers_name:
        #         desc = container.find_element_by_class_name('_42ef').text.lower()
        #         print(desc)
        #         print(city)
        #         if city.lower() in desc:
        #             may_user_element = container.find_element_by_class_name('_32mo')
        #         elif country_code in countrycode.country_code:
        #             country = countrycode.country_code[country_code]
        #             print(country)
        #             if country.lower() in desc:
        #                 may_user_element = container.find_element_by_class_name('_32mo')
        #         print('one done')

    def open_homepage_by_param(self, name: str, city: str, country_code: str):
        encode_name = quote(name)
        url_prefix = 'https://www.facebook.com/search/people/?'
        q = 'q=' + encode_name
        url = url_prefix + q
        self.__request_num = self.__request_num + 1
        if self.__request_num >= self.__request_max:
            self.restart()
        info_dict = dict()
        # 打开搜索页
        self.__log.debug("search url:" + url)
        self.__browser.get(url)
        sleep.random_sleep(self.__sleep)
        browse_results_container = self.__browser.find_element_by_id('BrowseResultsContainer') \
            .find_elements_by_class_name("_4p2o")
        self.__log.debug("len(browse_results_container)=" + str(len(browse_results_container)))
        containers = self.__find_user_element(browse_results_container=browse_results_container, filter=name)
        self.__log.debug("len(containers)=" + str(len(containers)))
        has_find = False
        if len(containers) == 1:
            has_find = True
            may_user_element = containers[0].find_element_by_class_name('_32mo')
        elif len(containers) > 1:
            if country_code in countrycode.country_code:
                country = countrycode.country_code[country_code]
                container_countrys = self.__find_user_element(browse_results_container=containers, filter=country)
                if len(container_countrys) == 1:
                    has_find = True
                    may_user_element = container_countrys[0].find_element_by_class_name('_32mo')
                elif len(container_countrys) > 1:
                    containers = container_countrys
            if not has_find:
                container_citys = self.__find_user_element(browse_results_container=containers, filter=city)
                if len(container_citys) == 1:
                    has_find = True
                    may_user_element = container_citys[0].find_element_by_class_name('_32mo')
        if not has_find:
            return info_dict
        may_user_element.click()
        sleep.random_sleep(self.__sleep)
        info_dict['homepage'] = self.__browser.current_url
        self.__log.debug('homepage=' + self.__browser.current_url)
        info_dict = self.__collect(info_dict)
        return info_dict


def browser_param(browser: str, email: str, pw: str):
    log = Log(error_path='error.log', debug_path='normal.log', json_path='info.log')
    log.set_level(Log.stdout_level)
    # for test
    log.debug('test ' + browser + '_' + email)
    start = time.time()
    crawler = FacebookCrawler(user_name=email, password=pw, log=log, browser=browser)
    crawler.init()
    crawler.login_facebook()
    # crawler.get_browser().save_screenshot('login.png')
    crawler.set_sleep(1)
    user_url = 'https://www.facebook.com/app_scoped_user_id/1758044224504993/'
    user_info = crawler.open_homepage_by_url(user_homepage=user_url)
    log.debug(user_info)
    end = time.time()
    log.debug('time cost:' + str(end - start) + ' s')


def main():
    qq_account = '1214933295@qq.com'
    kika_account = 'guangli.lv@kikatech.com'
    pku_account = 'lvguangli@pku.edu.cn'
    lvguangli_pw = 'baikefan'
    chenzhenpeng_account = '846913901@qq.com'
    chenzhenpeng_pw = 'czp123456'
    gaoyuan_account = 'yuangaopkucis@gmail.com'
    gaoyuan_pw = '7552188abcde'
    haokuixi_account = 'haokuixi@gmail.com'
    haokuixi_pw = 'Dragonfly1024'
    # browser_param('safari', haokuixi_account, haokuixi_pw)
    # browser_param('safari', chenzhenpeng_account, chenzhenpeng_pw)
    # browser_param('safari', qq_account, lvguangli_pw)
    # browser_param('safari', gaoyuan_account, gaoyuan_pw)
    see_url('safari', qq_account, lvguangli_pw)
    # code()


def code():
    str1 = '{"name":"users_location","args":"Cairo Egypt"}'
    str2 = 'الزجوي عبدلاه'
    from urllib.parse import quote
    str1 = quote(str1)
    str2 = quote(str2)
    print(str1)
    print(str2)
    url = 'https://www.facebook.com/search/people/?q=' + str2 + '&filters_city=' + str1
    print(url)


def see_url(browser: str, email: str, pw: str):
    log = Log(error_path='error.log', debug_path='normal.log', json_path='info.log')
    log.set_level(Log.stdout_level)
    # for test
    log.debug('test ' + browser + '_' + email)
    start = time.time()
    crawler = FacebookCrawler(user_name=email, password=pw, log=log, browser=browser)
    crawler.init()
    log.debug('init')
    crawler.login_facebook()
    log.debug('login')
    crawler.set_sleep(1)
    # info_dict = crawler.open_homepage_by_param(name='الزجوي عبدلاه', city='Cairo', country_code='EG')
    # print(info_dict)
    # info_dict = crawler.open_homepage_by_param(name='Angel Gunawan', city='Surabaya', country_code='ID')
    # print(info_dict)
    info_dict = crawler.open_homepage_by_param(name='Arman Ali', city='Gorakhpur', country_code='IN')
    print(info_dict)
    # info_dict = crawler.open_homepage_by_param(name='Jose Antonio Lara Gálvez', city='Jerez de la Frontera',
    #                                            country_code='ES')
    # print(info_dict)
    # info_dict = crawler.open_homepage_by_param(name='Elena Iuliana', city='Bucharest', country_code='RO')
    # print(info_dict)
    end = time.time()
    log.debug('time cost:' + str(end - start) + ' s')


if __name__ == '__main__':
    # browser_name = sys.argv[1]
    # user = sys.argv[2]
    # browser_test(browser_name, user)
    main()
