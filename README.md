# baostock-tks

从 [Baostock](https://www.baostock.com/) 拉取沪深证券数据保存到项目根目录duckdb文件 `./duckdb/sharp_market.duckdb`。
如果数据并不是实时的可自行调用相关接口刷新duckdb（后续是否包含其他市场股票证券信息待定）

## 证券基础信息

本任务调用 [获取某日所有证券信息](https://www.baostock.com/mainContent?file=StockBasicInfoAPI.md) 的 `query_all_stock(day=...)` 接口，按指定日期获取全部证券代码、交易状态和证券名称。结果按日期保存为快照；同一日期和证券代码重复执行时会更新该行。

| DuckDB表 | 字段 | 说明 |
| --- | --- | --- |
| `stock_basic_info` | `query_date` | 查询日期，对应接口的 `day` 参数 |
| `stock_basic_info` | `code` | 证券代码，如 `sh.600000` |
| `stock_basic_info` | `trade_status` | 交易状态，`1` 为正常交易，`0` 为已结束交易 |
| `stock_basic_info` | `code_name` | 证券名称 |

表结构及表、字段注释见 [`duckdb/ddl/stock_basic_info.sql`](duckdb/ddl/stock_basic_info.sql)。

## 安装与运行

使用 Python 3.10 环境安装依赖：

```powershell
python -m pip install -r requirements.txt
```

查询今天的数据：

```powershell
python -m stock_basic_info.stock_basic
```

查询指定日期，并可指定 DuckDB 文件：

```powershell
python -m stock_basic_info.stock_basic --date 2024-01-02
python -m stock_basic_info.stock_basic --date 2024-01-02 --database .\duckdb\sharp_market.duckdb
```

Baostock 日期参数使用 `YYYY-MM-DD`。接口客户端负责登录、查询和退出；DuckDB 仓储模块负责初始化 DDL 与幂等写入。
