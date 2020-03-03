# Scrapy 框架

## 框架

[框架结构图](./asserts/2020-03-03-001.jpg)

1. Engine，引擎，用来处理整个系统的数据流处理，触发事务，是整个框架的核心。
2. Item，项目，它定义了爬取结果的数据结构，爬取的数据会被赋值成该对象。
3. Scheduler， 调度器，用来接受引擎发过来的请求并加入队列中，并在引擎再次请求的时候提供给引擎。
4. Downloader，下载器，用于下载网页内容，并将网页内容返回给蜘蛛。
5. Spiders，蜘蛛，其内定义了爬取的逻辑和网页的解析规则，它主要负责解析响应并生成提取结果和新的请求。
6. Item Pipeline，项目管道，负责处理由蜘蛛从网页中抽取的项目，它的主要任务是清洗、验证和存储数据。
7. Downloader Middlewares，下载器中间件，位于引擎和下载器之间的钩子框架，主要是处理引擎与下载器之间的请求及响应。
8. Spider Middlewares， 蜘蛛中间件，位于引擎和蜘蛛之间的钩子框架，主要工作是处理蜘蛛输入的响应和输出的结果及新的请求。

## 数据流

> Scrapy 中的数据流由引擎控制，其过程如下:

1. Engine 首先打开一个网站，找到处理该网站的 Spider 并向该 Spider 请求第一个要爬取的 URL。
2. Engine 从 Spider 中获取到第一个要爬取的 URL 并通过 Scheduler 以 Request 的形式调度。
3. Engine 向 Scheduler 请求下一个要爬取的 URL。
4. Scheduler 返回下一个要爬取的 URL 给 Engine，Engine 将 URL 通过 Downloader Middlewares 转发给 Downloader 下载。
5. 一旦页面下载完毕， Downloader 生成一个该页面的 Response，并将其通过 Downloader Middlewares 发送给 Engine。
6. Engine 从下载器中接收到 Response 并通过 Spider Middlewares 发送给 Spider 处理。
7. Spider 处理 Response 并返回爬取到的 Item 及新的 Request 给 Engine。
8. Engine 将 Spider 返回的 Item 给 Item Pipeline，将新的 Request 给 Scheduler。
9. 重复第二步到最后一步，直到 Scheduler 中没有更多的 Request，Engine 关闭该网站，爬取结束。
10. 通过多个组件的相互协作、不同组件完成工作的不同、组件对异步处理的支持，Scrapy 最大限度地利用了网络带宽，大大提高了数据爬取和处理的效率。


## 项目结构

- scrapy.cfg：它是 Scrapy 项目的配置文件，其内定义了项目的配置文件路径、部署相关信息等内容。
- items.py：它定义 Item 数据结构，所有的 Item 的定义都可以放这里。
- pipelines.py：它定义 Item Pipeline 的实现，所有的 Item Pipeline 的实现都可以放这里。
- settings.py：它定义项目的全局配置。
- middlewares.py：它定义 Spider Middlewares 和 Downloader Middlewares 的实现。
- spiders：其内包含一个个 Spider 的实现，每个 Spider 都有一个文件。
