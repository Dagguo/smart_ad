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
mkdir -p /home/gaoyuan/guoda/smart_ad/log/
smartyads_log=/home/gaoyuan/guoda/smart_ad/log/${start_date}-${end_date}.log
python3 /home/gaoyuan/guoda/smart_ad/dailyReportForSmartyAds.py -s ${start_date} -e ${end_date}  > ${smartyads_log} 2>&1
