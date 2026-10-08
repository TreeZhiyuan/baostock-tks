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

如果连接 Baostock 服务器失败，客户端默认自动重试 3 次（每次间隔 3 秒）。可通过 `--retries` 调整重试次数，例如 `--retries 5`；重试仍失败时命令会输出错误信息并以非零状态码退出。

## 交易日信息

本任务调用 [获取交易日信息](https://www.baostock.com/mainContent?file=StockBasicInfoAPI.md) 的 `query_trade_dates(start_date, end_date)` 接口，获取日期范围内每天是否为交易日。未传日期时使用 Baostock 默认范围（开始日期为 `2015-01-01`，结束日期为当前日期）。

| DuckDB表 | 字段 | 说明 |
| --- | --- | --- |
| `trade_calendar` | `calendar_date` | 日历日期，主键 |
| `trade_calendar` | `is_trading_day` | 是否交易日，`1` 为交易日，`0` 为非交易日 |

表结构及表、字段注释见 [`duckdb/ddl/trade_calendar.sql`](duckdb/ddl/trade_calendar.sql)。

查询默认日期范围并入库：

```powershell
python -m stock_basic_info.trade_calendar
```

查询指定日期范围：

```powershell
python -m stock_basic_info.trade_calendar --start-date 2026-09-01 --end-date 2026-09-30
```

同一日期重复执行时会更新 `is_trading_day`，不会产生重复记录。
