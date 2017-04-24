# coding=utf-8
import re
import urlparse
import urllib2
import time
import datetime
import robotparser
from downloader import Downloader


def link_crawler(seed_url, link_regex=None, delay=5, max_depth=-1, max_urls=-1, user_agent='wswp', proxies=None,
                 num_retries=1, scrape_callback=None, cache=None):
    # 爬虫从给定的种子链接开始使用正则匹配

    # URL队列仍旧需要爬行的队列
    crawl_queue = [seed_url]
    # URL需要爬行的深度
    seen = {seed_url: 0}
    # 跟踪多少个URL已经被下载
    num_urls = 0
    rp = get_robots(seed_url)
    D = Downloader(delay=delay, user_agent=user_agent, proxies=proxies, num_retries=num_retries, cache=cache)

    while crawl_queue:
        url = crawl_queue.pop()
        depth = seen[url]
        # 检查URL能否通过robots文件的限制
        if rp.can_fetch(user_agent, url):
            html = D(url)
            links = []
            if scrape_callback:
                links.extend(scrape_callback(url, html) or [])

            if depth != max_depth:
                # 深度没到到的话仍需要进行爬行
                if link_regex:
                    # 过滤链接是都已经达到预计的期望
                    links.extend(link for link in get_links(html) if re.match(link_regex, link))

                for link in links:
                    link = normalize(seed_url, link)
                    # 检查是否已经爬行完了这个根链接
                    if link not in seen:
                        seen[link] = depth + 1
                        # 检查链接个根链接是否是同一个域
                        if same_domain(seed_url, link):
                            # 正确的链接,将他添加到队列
                            crawl_queue.append(link)

            # 检查是否达到了下载的最大值
            num_urls += 1
            if num_urls == max_urls:
                break
        else:
            print 'Blocked by robots.txt:', url


def normalize(seed_url, link):
    # 通过移除哈希值或者添加域来规范URL
    link, _ = urlparse.urldefrag(link)  # 移除哈希值来避免复用
    return urlparse.urljoin(seed_url, link)


def same_domain(url1, url2):
    # 如果链接输入同一个域,则真

    return urlparse.urlparse(url1).netloc == urlparse.urlparse(url2).netloc


def get_robots(url):
    # 初始化域名的robots文件
    rp = robotparser.RobotFileParser()
    rp.set_url(urlparse.urljoin(url, '/robots.txt'))
    rp.read()
    return rp


def get_links(html):
    # 冲HTML中返回链接列表
    # 从网页中提取链接的正则表达式
    webpage_regex = re.compile('<a[^>]+href=["\'](.*?)["\']', re.IGNORECASE)
    # 网页中的所有链接列表
    return webpage_regex.findall(html)


if __name__ == '__main__':
    link_crawler('http://192.168.5.109:8081/', '(show|list|Comments|)', delay=0, num_retries=1, max_depth=5, user_agent='GoodCrawler')