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

## 历史 A 股 K 线数据

本任务调用 [获取历史 A 股 K 线数据](https://www.baostock.com/mainContent?file=stockKData.md) 的 `query_history_k_data_plus(code, fields, start_date, end_date, frequency, adjustflag)` 接口。支持的 `frequency` 为：`d` 日线、`w` 周线、`m` 月线、`5`/`15`/`30`/`60` 分钟线；`adjustflag` 为 `1` 后复权、`2` 前复权、`3` 不复权。日期范围两端均包含，未提供日期时使用 Baostock 接口默认范围。

调用命令如下。默认一次请求七种周期；可以重复 `--frequency` 只请求指定周期，也可以重复 `--code` 批量保存证券。分钟线不支持指数代码。

```powershell
python -m stock_basic_info.history_k_data --code sh.600000 --start-date 2024-01-01 --end-date 2024-01-31
python -m stock_basic_info.history_k_data --code sh.600000 --frequency d --frequency 5 --adjustflag 2
python -m stock_basic_info.history_k_data --code sh.600000 --code sz.000001 --database .\duckdb\sharp_market.duckdb
```

接口客户端按周期选择对应字段：日线包含 `preclose`、`tradestatus`、`pctChg`、`peTTM`、`psTTM`、`pcfNcfTTM`、`pbMRQ`、`isST`；周/月线包含 `preclose`、`tradestatus`、`pctChg`、`peTTM`、`psTTM`、`pcfNcfTTM`、`pbMRQ`、`isST`；分钟线包含 `time` 并请求全部统一表字段。不同周期由接口不提供的字段转换为 `NULL`，并在一次登录会话中完成所选周期的查询；仓储模块负责初始化 DDL 和幂等写入。

| DuckDB表 | 字段 | 说明 |
| --- | --- | --- |
| `history_k_data` | `trade_date` | 交易所行情日期，对应 API 的 `date` |
| `history_k_data` | `trade_time` | 分钟线交易所时间，对应 API 的 `time`；日/周/月线为空字符串 |
| `history_k_data` | `code` | 证券代码，如 `sh.600000` |
| `history_k_data` | `frequency` | `d`、`w`、`m`、`5`、`15`、`30` 或 `60` |
| `history_k_data` | `open`/`high`/`low`/`close` | 开盘、最高、最低、收盘价，人民币元 |
| `history_k_data` | `preclose` | 前收盘价；周/月/分钟线没有此字段时为 `NULL` |
| `history_k_data` | `volume` | 成交量，单位股；分钟线为时间范围内累计值 |
| `history_k_data` | `amount` | 成交额，单位人民币元；分钟线为时间范围内累计值 |
| `history_k_data` | `adjustflag` | 复权状态：1 后复权、2 前复权、3 不复权 |
| `history_k_data` | `turn` | 换手率百分比；接口不返回时为 `NULL` |
| `history_k_data` | `tradestatus` | 交易状态：1 正常交易、0 停牌；接口不返回时为 `NULL` |
| `history_k_data` | `pct_chg` | 涨跌幅百分比，对应 API 的 `pctChg` |
| `history_k_data` | `pe_ttm` | 滚动市盈率，对应 API 的 `peTTM` |
| `history_k_data` | `ps_ttm` | 滚动市销率，对应 API 的 `psTTM` |
| `history_k_data` | `pcf_ncf_ttm` | 滚动市现率，对应 API 的 `pcfNcfTTM` |
| `history_k_data` | `pb_mrq` | 市净率，对应 API 的 `pbMRQ` |
| `history_k_data` | `is_st` | 是否 ST：1 是、0 否，对应 API 的 `isST` |

表的唯一键为 `code + frequency + adjustflag + trade_date + trade_time`，同一请求重复运行会更新对应 K 线。表结构和表、字段注释见 [`duckdb/ddl/history_k_data.sql`](duckdb/ddl/history_k_data.sql)。
