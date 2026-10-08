anaconda python3目录: C:\Users\cuizy52127\AppData\Local\miniconda3\envs\python3.10
阅读baostock-tks下AGENTS.md关于项目的约定
从 [baostock - A股K线数据 - 获取历史A股K线数据
](https://www.baostock.com/mainContent?file=stockKData.md) 调用接口实现历史A股K线信息入库到duckdb
要求入库的历史A股K线需要包括 d=日、w=周、m=月、5=5分钟、15=15分钟、30=30分钟、60=60分钟k线数据，请详细阅读接口文档进行表结构设计和baostock客户端