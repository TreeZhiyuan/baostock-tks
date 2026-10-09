# Agent Notes

本项目是 [baostock](https://www.baostock.com/) 数据拉取任务集合，并将证券股票信息保存在项目根目录下「./duckdb/sharp_market.duckdb`」

## 约定和规则

- 项目实现要求不同模块功能和代码的高内聚低耦合，该项目目前模块主要包含：「baostock客户端」「duckdb数据库操作」
- 在接入 baostock 接口获取相关证券股票信息时，需要根据接口定义生成duckdb数据库表DDL保存在`./duckdb/ddl`，并为表和字段添加注释
- 每新接入一个接口都要明确尽可能把baostock接口出入参保留，需要将接口信息、具体用法和对应的数据库表信息更新到README.md
