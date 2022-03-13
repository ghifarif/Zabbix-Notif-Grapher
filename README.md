This script capture zabbix trend graph & share-link to slack each alert. Zabbix server in this case alse used to expose HTTPS apache htfile for slack.
Combine with orchestration such as Jenkins/Azure DevOps/AWS Pipeline (Zabbix in my case) for automatic graph notif each-trigger.
![image](https://user-images.githubusercontent.com/101460772/158056737-4920ea49-59e1-436d-8ad6-f2492ca34c1a.png)
Can be used for similiar case to other monitoring tools, provided API is supported.

Refference used/related in this repo:
- [Apache Web-server](https://httpd.apache.org/docs/2.4/bind.html)
- [Zabbix API](https://www.zabbix.com/documentation/current/en/manual/api)
