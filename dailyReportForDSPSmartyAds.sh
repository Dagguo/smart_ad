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
source='smartyads'
dsp_name='smartyads'
utc_interval=0
list='846925213@qq.com'
#list='finance@smartyads.com,inna.samko@smartyads.com,kuixi.hao@kikatech.com,tina.yang@kikatech.com,gaoyuan@kikatech.com,846925213@qq.com'
#list='lvguangli@pku.edu.cn,guangli.lv@kikatech.com,lvguangli.pku@gmail.com,gaoyuan@kikatech.com,gaoyuanandy@163.com'
# mkdir -p /home/lvguangli/spark/log/dsp/
# ssp_log=/home/lvguangli/spark/log/dsp/${dsp_name}_${start_date}-${end_date}.log
# python3 /home/lvguangli/project/facebook_crawler/dailyReportForDSP.py -s ${start_date} -e ${end_date} -d ${source} -n ${dsp_name} -u ${utc_interval} -l ${list} > ${ssp_log} 2>&1


mkdir -p /home/guoda/log/dsp/
ssp_log=/home/guoda/log/dsp/${dsp_name}_${start_date}-${end_date}.log
python3 /home/gaoyuan/guoda/smart_ad/dailyReportForDSP.py -s ${start_date} -e ${end_date} -d ${source} -n ${dsp_name} -u ${utc_interval} -l ${list} > ${ssp_log} 2>&1
