#!/usr/bin/env bash
if [ $# = 2 ] ; then
    start_date=$1
    end_date=$2
elif [ $# = 1 ] ; then
    end_date=$1
    start_date=`date -d "0 days ${end_date}" +%Y%m`'01'
elif [ $# = 0 ] ; then

    start_date=`date -d "0 days ago" +%Y%m`'01'
    anchor_month=`date -d "1 days ago" +%m`
    this_month=`date -d "0 days ago" +%m`
    if [ ! ${anchor_month} == ${this_month} ];then
    	start_date=`date -d "1 days ago" +%Y%m`'01'
        end_date=`date -d "0 days ago" +%Y%m%d`
    else
        end_date=`date -d "0 days ago" +%Y%m%d`
    fi
else
    echo 'Usage: [start_date] [end_date]'
    exit 0
fi

echo ${start_date}
echo ${end_date}
source='webeye2'
dsp_name='webeye2'
utc_interval=0
#list='lvguangli@pku.edu.cn,guangli.lv@kikatech.com,lvguangli.pku@gmail.com'
#list='gaoyuan@kikatech.com,gaoyuanandy@163.com'
list='mia.yao@webeye.com,tina.yang@kikatech.com,gaoyuan@kikatech.com,846925213@qq.com'
mkdir -p /home/guoda/log/dsp/
dsp_log=/home/guoda/log/dsp/${dsp_name}_${start_date}-${end_date}.log
python3 /home/guoda/smart_ad/dailyReportForDSPWithSum.py -s ${start_date} -e ${end_date} -d ${source} -n ${dsp_name} -u ${utc_interval} -l ${list} > ${dsp_log} 2>&1
