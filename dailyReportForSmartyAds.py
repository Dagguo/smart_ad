import pymysql
import os
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from optparse import OptionParser
from tools import fileutils
# import fileutils


def query_from_mysql(query_list: list):
    result_set = list()
    # 链接mysql
    # host_ip = 'kika-ad-data-mysql0.intranet.com'
    host_ip = '172.31.19.196'
    conn = pymysql.connect(
        host=host_ip,
        user='sparkuser',
        passwd='0~eFNp=VJnW1',
        db='bidder'
    )
    # 获取游标
    cur = conn.cursor()
    # 查询执行
    for sql in query_list:
        cur.execute(sql)
        result = cur.fetchall()
        if len(result) > 0:
            result_set.append(result)
    cur.close()
    conn.commit()
    conn.close()
    return result_set


def utc_plus_8_to_utc(time_utc_plus_8: int):
    utc = datetime.strptime(str(time_utc_plus_8), '%Y%m%d%H') + timedelta(hours=-8)
    return datetime.strftime(utc, '%Y%m%d%H')


def save_query_to_file(output_path: str, result_set: list, date_set: list):
    file_content = dict()
    line = 'date(UTC),impressions,spends($)'
    print(line)
    fileutils.append_line_to_file(line=line, output_path=output_path)
    file_content['date(UTC)'] = ('impressions', 'spends($)')
    result_date = list()
    date = ''
    sum_impression = 0
    sum_cost = 0.0
    for result in result_set:
        for (time_utc_plus_8, impression, cost) in result:
            time_utc = utc_plus_8_to_utc(time_utc_plus_8)
            if date != time_utc[0:8]:
                if date != '':
                    result_date.append((date, sum_impression, sum_cost))
                date = time_utc[0:8]
                sum_impression = 0
                sum_cost = 0.0
            sum_impression = sum_impression + impression
            sum_cost = sum_cost + cost
    if date != '':
        result_date.append((date, sum_impression, sum_cost))
    for result in result_date:
        (time_utc, impression, cost) = result
        file_content[time_utc] = (impression, cost)
    for date in date_set:
        if date not in file_content:
            file_content[date] = (0, 0.0)
    for date in date_set:
        (impression, cost) = file_content[date]
        line = date + ',' + str(impression) + ',' + ("%.3f" % cost)
        fileutils.append_line_to_file(line=line, output_path=output_path)
    return file_content


def get_args():
    parser = OptionParser()
    parser.add_option(
        '-s', '--start_date',
        action='store',
        dest='start_date',
        type='string',
        # default=datetime.now().strftime('%Y%m%d'),
        help='daily report start date'
    )
    parser.add_option(
        '-e', '--end_date',
        action='store',
        dest='end_date',
        type='string',
        # default=datetime.now().strftime('%Y%m%d'),
        help='daily report end date'
    )
    (opts, args) = parser.parse_args()
    return opts


def email(file_content: dict, file_name: str, date_set: list):
    sender = 'dag.guo@kikatech.com'
    # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
    # for test
    # receivers = ['1214933295@qq.com', 'lvguangli@pku.edu.cn', 'guangli.lv@kikatech.com']
    #receivers = ['finance@smartyads.com', 'inna.samko@smartyads.com',
    #             'kuixi.hao@kikatech.com', 'tina.yang@kikatech.com', 'gaoyuan@kikatech.com','846925213@qq.com']
    receivers = ['gaoyuanandy@163.com', 'tina.yang@kikatech.com', 'gaoyuan@kikatech.com']

    mail_msg = '<p>This report is generated by Kikatech. ' \
               'Please note that these numbers need not be final and can be adjusted towards the month end. ' \
               'Disclaimer: Please do not reply to this email.</p>' + '<table border="1">'

    date = 'date(UTC)'
    (impression, cost) = file_content[date]
    mail_msg = mail_msg \
               + '<tr><th>' \
               + date + '</th><th>' \
               + impression + '</th><th>' \
               + cost + '</th></tr>'
    for date in date_set:
        (impression, cost) = file_content[date]
        mail_msg = mail_msg \
                   + '<tr><td>' \
                   + date + '</td><td>' \
                   + str(impression) + '</td><td>' \
                   + ("%.3f" % cost) + '</td></tr>'
    mail_msg = mail_msg + '</table>'
    message = MIMEMultipart('related')
    text = MIMEText(mail_msg, 'html', 'utf-8')
    message.attach(text)
    message['From'] = formataddr(["kikatech", sender])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
    message['To'] = formataddr(["smartyads", receivers[0]])  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
    if len(receivers) > 1:
        message['Bcc'] = ','.join(receivers[1:])
    date_str = date_set[0]
    if len(date_set) > 1:
        date_str = date_str + '-' + date_set[-1]
    subject = 'Kikatech DSP stats for smartyads RTB ' + date_str
    message['Subject'] = Header(subject, 'utf-8')
    # 读取文件作为附件，open()要带参数'rb'，使文件变成二进制格式,从而使'base64'编码产生作用，否则附件打开乱码
    attach = MIMEText(open(file_name, 'rb').read(), 'base64', 'utf-8')
    attach['Content-Type'] = 'text/plain'
    attname = 'attachment; filename ="' + file_name.split('/')[-1] + '"'
    attach['Content-Disposition'] = attname
    #message.attach(attach)

    try:
        smtp_obj = smtplib.SMTP('localhost')
        smtp_obj.sendmail(sender, receivers, message.as_string())
        print("邮件发送成功" + message.as_string())
    except smtplib.SMTPException:
        print("Error: 无法发送邮件")


def main():
    # 获取参数，参数包括其实日期和结束日期
    options = get_args()
    start_date = options.start_date
    end_date = options.end_date
    father_dir = start_date + '-' + end_date
    # 如果只有一天的数据，就合并一下日期格式
    start = datetime.strptime(start_date, '%Y%m%d')
    end = datetime.strptime(end_date, '%Y%m%d')
    if end - start == timedelta(days=1):
        father_dir = start_date
    output_file = '/home/gaoyuan/guoda/smart_ad/data/' \
                  + father_dir + '/dailyReportOfSmartyAds.csv'
    # 删除旧数据
    if os.path.exists(output_file):
        os.remove(output_file)
    # 本地数据为utc+8的数据，所以取开始日期08时到结束日期08时数据，然后整体时间-8调整到utc
    start_time = start_date + '08'
    end_time = end_date + '08'
    query_list = list()
    # 在三张表格查询
    tables = ['cpm_log_all']  # 'bid_log', 'cpc_log',

    # 使用这种方式就不需要手动在代码里解析时区了，会更方便
    # select
    # app_key,
    # date_format(date_add(str_to_date(time, '%Y%m%d%H'),  interval -8 hour), '%Y%m%d') date,
    # date_format((str_to_date(time, '%Y%m%d%H') - INTERVAL 8 HOUR), '%Y%m%d') date2,
    # sum(wins) win_count,
    # sum(impressions) imp_count,
    # sum(price)/1000 cost
    # from cpm_log
    # where
    # time > '2018012407'
    # and time < '2018012608'
    # and app_key = '86025b8fa53dd7862f0fdae6418f753c'
    # group by app_key, date;

    for table in tables:
        sql = 'SELECT time, sum(win_count) impression, sum(win_price) cost ' \
              + 'FROM ' + table + ' ' \
              + 'WHERE time >= \'' + start_time + '\' ' \
              + 'AND time < \'' + end_time + '\' ' \
              + 'AND app_key = \'86025b8fa53dd7862f0fdae6418f753c\' ' \
              + 'GROUP BY time'
        query_list.append(sql)
    print(query_list)
    # 查询语句
    result_set = query_from_mysql(query_list=query_list)
    print(result_set)
    date_set = list()
    # 构建日期列表，如果查询所在时间段无任何数据，则利用日期列表生成空表
    start = datetime.strptime(start_date, '%Y%m%d')
    end = datetime.strptime(end_date, '%Y%m%d')
    while start < end:
        date_set.append(start.strftime('%Y%m%d'))
        start = start + timedelta(days=1)
    # 存文件，并将存文件的内容返回
    file_content = save_query_to_file(output_path=output_file, result_set=result_set, date_set=date_set)
    print(file_content)
    email(file_content=file_content, file_name=output_file, date_set=date_set)


if __name__ == '__main__':
    main()
