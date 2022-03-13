#!/bin/bash -x

# config
channel="$1"
title="$2"
params="$3"

##graph retrieval
item_id="`echo \"${params}\" | grep 'ITEM_ID: ' | awk -F'ITEM_ID: ' '{print $2}'`" 
if [ "${item_id}" != "" ]; then
    timestamp=$(date +%s)
    b=$(echo ${item_id} | sed 's/[^0-9]*//g')
    wget --save-cookies="/tmp/zc_${timestamp}" --keep-session-cookies --post-data "name=$NAME&password=$PASS&enter=Sign+in" -O /dev/null -q "https://$ZBXIP/index.php?login=1"
    wget --load-cookies="/tmp/zc_${timestamp}"  -O "/usr/share/zabbix/???????/${b}-${timestamp}.png" -q "https://$ZBXIP/chart.php?&itemids=${b}&width=1280&period=3600"
    chart_url="https://$ZBXIP/???????/${b}-${timestamp}.png"
    rm -f /tmp/zc_${timestamp}
fi

###variable retrieval
trigger_status="`echo \"${params}\" | grep 'TRIGGER_STATUS: ' | awk -F'TRIGGER_STATUS: ' '{print $2}'`"; ok="(OK)"; problem="(PROBLEM)"
trigger_severity="`echo \"${params}\" | grep 'TRIGGER_SEVERITY: ' | awk -F'TRIGGER_SEVERITY: ' '{print $2}'`"
host="`echo \"${params}\" | grep 'HOST: ' | awk -F'HOST: ' '{print $2}'`"
trigger_name="`echo \"${params}\" | grep 'TRIGGER_NAME: ' | awk -F'TRIGGER_NAME: ' '{print $2}'`"
datetime="`echo \"${params}\" | grep 'DATETIME: ' | awk -F'DATETIME: ' '{print $2}'`"
item_value="`echo \"${params}\" | grep 'ITEM_VALUE: ' | awk -F'ITEM_VALUE: ' '{print $2}'`"

##build payload and send to slack
payload="payload={
  \"channel\": \"YOURCHANNEL\",
  \"username\": \"试试\",
  \"attachments\": [
    {
      \"title\": \"${message} ${trigger_name}\",
      \"color\": \"#FF0000\",
      \"fields\": [
	{
            \"value\": \"Severity : ${trigger_severity}\", \"short\": true
        }, {
            \"value\": \"Host : ${host}\", \"short\": true
        }, {
            \"value\": \"Date/Time : ${datetime}\", \"short\": true
        }, {
            \"value\": \"Last Value : ${item_value}\", \"short\": true
        }],
     \"image_url\": \"${chart_url}\"
    }]
}"
curl -m 5 --data-urlencode "${payload}" "https://hooks.slack.com/services/$TENANT/$CHANNEL/$WEBHOOK"
