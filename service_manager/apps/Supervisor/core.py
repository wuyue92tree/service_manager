#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Author: wuyue
# Email: wuyue@mofanghr.com

import json
from crwy.spider import Spider
from requests.auth import HTTPBasicAuth


class SupervisorCore(Spider):
    def __init__(self, host=None, port=9001, username=None, password=None):
        Spider.__init__(self)
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.url = "http://%s:%s" % (self.host, str(self.port))

    def status(self):
        res = self.html_downloader.download(
            self.url, auth=HTTPBasicAuth(self.username, self.password))
        if res.status_code == 200:
            return True
        return False

    def stop(self, app):
        url = self.url + "/index.html?processname=%s&action=stop" % app
        res = self.html_downloader.download(
            url, auth=HTTPBasicAuth(self.username, self.password))
        if "stopped" in res.url:
            return True
        return False

    def start(self, app):
        url = self.url + "/index.html?processname=%s&action=start" % app
        res = self.html_downloader.download(
            url, auth=HTTPBasicAuth(self.username, self.password))
        if "started" in res.url:
            return True
        return False

    def restart(self, app):
        url = self.url + "/index.html?processname=%s&action=restart" % app
        res = self.html_downloader.download(
            url, auth=HTTPBasicAuth(self.username, self.password))
        if "restarted" in res.url:
            return True
        return False

    def restart_all(self):
        url = self.url + "/index.html?&action=restartall"
        res = self.html_downloader.download(
            url, auth=HTTPBasicAuth(self.username, self.password))
        if "restarted" in res.url:
            return True
        return False

    def stop_all(self):
        url = self.url + "/index.html?&action=stopall"
        res = self.html_downloader.download(
            url, auth=HTTPBasicAuth(self.username, self.password))
        if "stopped" in res.url:
            return True
        return False

    def clearlog(self, app):
        url = self.url + "/index.html?processname=%s&action=clearlog" % app
        res = self.html_downloader.download(
            url, auth=HTTPBasicAuth(self.username, self.password))
        if "cleared" in res.url:
            return True
        return False

    def tail(self, app, limit=1024):
        url = self.url + "/tail.html?processname" \
                         "=%s&limit=%s" % (app, str(limit))
        res = self.html_downloader.download(
            url, auth=HTTPBasicAuth(self.username, self.password))
        soups = self.html_parser.parser(res.content).find('pre')
        return str(soups)

    def tail_f(self, app):
        url = self.url + "/logtail/%s" % app
        res = self.html_downloader.download(
            url, auth=HTTPBasicAuth(self.username, self.password), stream=True)
        return res.content
        # soups = self.html_parser.parser(res.content).find('pre')
        # return str(soups)

    def get_process_list(self):
        try:
            res = self.html_downloader.download(
                self.url, auth=HTTPBasicAuth(self.username, self.password),
                timeout=5)
            soups = self.html_parser.parser(res.content)
            lst = soups.find("tbody").find_all("tr")

            response_data = []
            for item in lst:
                response = dict()
                response["status"] = item.find("td",
                                               class_="status").text.encode(
                    'utf-8')
                response["description"] = item.find_all("td")[1].find(
                    "span").text.encode('utf-8')
                response["name"] = item.find_all("td")[2].find("a").text.encode(
                    'utf-8')
                response["url"] = self.url + "/" + item.find_all("td")[2].find(
                    "a").get("href").encode('utf-8')

                response_data.append(response)
            return json.dumps(response_data, indent=4)
        except:
            return None


if __name__ == '__main__':
    runner = SupervisorCore(host="172.16.25.9")
    runner.get_process_list()
