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


def query_from_mysql_on_new_sql(query_list: list):
    result_set = list()
    # 链接mysql
    # host_ip = '34.226.218.239'
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


def read_dsp_request(start_date: str, end_date: str, utc_interval: int, ad_source: str):
    from sqlalchemy.engine import create_engine
    from sqlalchemy.orm import sessionmaker
    engine = create_engine('druid://172.31.26.30:8082/druid/v2/sql/')
    Session = sessionmaker(bind=engine)
    session = Session()
    if utc_interval >= 0:
        if len(str(utc_interval)) == 1:
            utc_interval = '+0' + str(utc_interval) + ':00'
        else:
            utc_interval = '+' + str(utc_interval) + ':00'
    else:
        utc_interval = -utc_interval
        if len(str(utc_interval)) == 1:
            utc_interval = '-0' + str(utc_interval) + ':00'
        else:
            utc_interval = '-' + str(utc_interval) + ':00'
    sql_template = "select " \
                   "time_format(__time, 'yyyyMMdd','{0}'), " \
                   "sum(dsp_req_count) as sum_req_count " \
                   "from cpm_log " \
                   "where " \
                   "__time >= TIME_PARSE('{1} 00', 'yyyyMMdd HH','{0}') " \
                   "and __time < TIME_PARSE('{2} 00', 'yyyyMMdd HH','{0}') " \
                   "and ad_source='{3}' " \
                   "group by " \
                   "time_format(__time, 'yyyyMMdd','{0}')"
    sql = sql_template.format(utc_interval, start_date, end_date, ad_source)
    print(sql)
    result = session.execute(sql).fetchall()
    result_set=[('20191201', 0), ('20191202', 0), ('20191203', 0), ('20191204', 0), ('20191205', 0)]
    if len(result) > 0:
        result_set=result_set+result
    session.close()
    print(result_set)
    return result_set


def save_query_to_file(output_path: str, utc_interval: int, result_set: list, date_set: list):
    file_content = dict()
    utc_str = str(utc_interval)
    if utc_interval == 0:
        utc_str = ''
    line = 'date(UTC' + utc_str + '),requests,impressions,revenue($)'
    print(line)
    fileutils.append_line_to_file(line=line, output_path=output_path)
    file_content['date(UTC' + utc_str + ')'] = ('requests', 'impressions', 'spends($)')
    # result_date = list()
    total_requests = 0
    total_impressions = 0
    total_revenue = 0
    for (local_date, requests, impression, revenue) in result_set:
        file_content[local_date] = (requests, impression, revenue)
        total_requests = total_requests + requests
        total_impressions = total_impressions + impression
        total_revenue = total_revenue + revenue
    for date in date_set:
        if date not in file_content and len(file_content) == 1:
            file_content[date] = (0, 0, 0.0)
    file_content['sum'] = (total_requests, total_impressions, total_revenue)
    for date in date_set:
    	if date in file_content:
        	(request, impression, revenue) = file_content[date]
        	line = date + ',' + str(request) + ',' + str(impression) + ',' + ("%.3f" % revenue)
        	fileutils.append_line_to_file(line=line, output_path=output_path)
    	else:
        	line = date + ',' + str(0) + ',' + str(0) + ',' + "0"
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
    parser.add_option(
        '-d', '--source',
        action='store',
        dest='source',
        type='string',
        help='daily report source'
    )
    parser.add_option(
        '-n', '--dsp_name',
        action='store',
        dest='dsp_name',
        type='string',
        help='daily report dsp name'
    )
    parser.add_option(
        '-u', '--utc_interval',
        action='store',
        dest='utc_interval',
        type='int',
        help='daily report utc interval'
    )
    parser.add_option(
        '-l', '--list',
        action='store',
        dest='list',
        type='string',
        help='daily report email list'
    )

    (opts, args) = parser.parse_args()
    return opts


def email(file_content: dict, file_name: str, date_set: list, dsp_name: str, utc_interval: int, email_list: list):
    sender = 'dag.guo@kikatech.com'
    # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
    # for test
    # receivers = ['1214933295@qq.com', 'lvguangli@pku.edu.cn', 'guangli.lv@kikatech.com']
    receivers = email_list

    mail_msg = '<p>This report is generated by Kikatech. ' \
               'Please note that these numbers need not be final and can be adjusted towards the month end. ' \
               'Disclaimer: Please do not reply to this email.</p>' + '<table border="1">'

    utc_str = str(utc_interval)
    if utc_interval == 0:
        utc_str = ''
    date = 'date(UTC' + utc_str + ')'
    (requests, impression, revenue) = file_content[date]
    mail_msg = mail_msg \
               + '<tr><th>' \
               + date + '</th><th>' \
               + requests + '</th><th>' \
               + impression + '</th><th>' \
               + revenue + '</th></tr>'
    for date in date_set:
    	if date in file_content:
	        (requests, impression, revenue) = file_content[date]
	        mail_msg = mail_msg \
	                   + '<tr><td>' \
	                   + date + '</td><td>' \
	                   + str(requests) + '</td><td>' \
	                   + str(impression) + '</td><td>' \
	                   + ("%.3f" % revenue) + '</td></tr>'
    mail_msg = mail_msg + '</table>'
    message = MIMEMultipart('related')
    text = MIMEText(mail_msg, 'html', 'utf-8')
    message.attach(text)
    message['From'] = formataddr(["kikatech", sender])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
    message['To'] = formataddr([dsp_name, receivers[0]])  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
    if len(receivers) > 1:
        message['Bcc'] = ','.join(receivers[1:])
    date_str = date_set[0]
    if len(date_set) > 2:
        date_str = date_str + '-' + date_set[-2]
    subject = 'Kikatech stats for ' + dsp_name + ' RTB ' + date_str
    message['Subject'] = Header(subject, 'utf-8')
    # 读取文件作为附件，open()要带参数'rb'，使文件变成二进制格式,从而使'base64'编码产生作用，否则附件打开乱码
    attach = MIMEText(open(file_name, 'rb').read(), 'base64', 'utf-8')
    attach['Content-Type'] = 'text/plain'
    attname = 'attachment; filename ="' + file_name.split('/')[-1] + '"'
    attach['Content-Disposition'] = attname
    message.attach(attach)

    try:
        smtp_obj = smtplib.SMTP('localhost')
        smtp_obj.sendmail(sender, receivers, message.as_string())
        print("邮件发送成功" + message.as_string())
    except smtplib.SMTPException:
        print("Error: 无法发送邮件")


def main():
    # 获取参数，参数包括其实日期和结束日期
    options = get_args()
    source = str(options.source)
    dsp_name = str(options.dsp_name)
    utc_interval = int(options.utc_interval)
    start_date = str(options.start_date)
    end_date = str(options.end_date)
    email_list = str(options.list).split(',')
    father_dir = start_date + '-' + end_date
    # 如果只有一天的数据，就合并一下日期格式
    start = datetime.strptime(start_date, '%Y%m%d')
    end = datetime.strptime(end_date, '%Y%m%d')
    if end - start == timedelta(days=1):
        father_dir = start_date[0:8]
    output_file = '/home/guoda/smart_ads/data/dailyReportFor' + dsp_name + '/' \
                  + father_dir + '/dailyReportOf' + dsp_name + '.csv'
    # 删除旧数据
    if os.path.exists(output_file):
        os.remove(output_file)
    request_set = read_dsp_request(start_date, end_date, utc_interval, source)
    # 本地数据为utc+8的数据，所以取开始日期08时到结束日期08时数据，然后整体时间-8+utc_interval调整到utc_interval
    interval = 8 - utc_interval
    start_time = datetime.strptime(start_date, '%Y%m%d')
    start_time = start_time + timedelta(hours=interval)
    start_time = start_time.strftime('%Y%m%d%H')

    end_time = datetime.strptime(end_date, '%Y%m%d')
    end_time = end_time + timedelta(hours=interval)
    end_time = end_time.strftime('%Y%m%d%H')

    # 在三张表格查询
    tables = ['cpm_log_all']
    result_set = list()
    for table in tables:
        bidder_sql = 'select date_format((str_to_date(time,\'%Y%m%d%H\') - INTERVAL {0} HOUR),\'%Y%m%d\') date,' \
                     '     sum(win_count) wins,' \
                     '     sum(revenue) revenue' \
                     '     from {1}' \
                     '     where time >= \'{2}\'' \
                     '     and time < \'{3}\'' \
                     '     and ad_source = \'{4}\'' \
                     '     group by date;'.format(str(interval), table, start_time, end_time, source)
        query_list = list()
        query_list.append(bidder_sql)
        print(query_list)
        # 查询语句
        raw=(('20191201',0,0),('20191202',0,0),('20191203',0,0),('20191204',0,0),('20191205',0,0))
        bidder_set = raw+query_from_mysql_on_new_sql(query_list=query_list)[0]
        print(bidder_set)
        for bidder in bidder_set:
            for (bidder_date, bidder_win, bidder_revenue) in bidder:
                find_req = False
                for request in request_set:
                    for (request_date, request_count) in request:
                        if bidder_date == request_date:
                            find_req = True
                            result_set.append((bidder_date, request_count, bidder_win, bidder_revenue))
                if not find_req:
                    result_set.append((bidder_date, 0, bidder_win, bidder_revenue))
    date_set = list()
    # 构建日期列表，如果查询所在时间段无任何数据，则利用日期列表生成空表
    start = datetime.strptime(start_date, '%Y%m%d')
    end = datetime.strptime(end_date, '%Y%m%d')
    while start < end:
        date_set.append(start.strftime('%Y%m%d'))
        start = start + timedelta(days=1)
    # 存文件，并将存文件的内容返回
    date_set.append("sum")
    file_content = save_query_to_file(output_path=output_file, utc_interval=utc_interval, result_set=result_set,
                                      date_set=date_set)
    print(file_content)
    email(file_content=file_content, file_name=output_file, date_set=date_set, dsp_name=dsp_name,
          utc_interval=utc_interval, email_list=email_list)


if __name__ == '__main__':
    main()
