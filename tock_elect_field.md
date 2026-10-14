根据 Baostock 的 Python API 文档，你列出的指标可以分成三类：财务报表及财务比率、每日估值指标、需要自行计算的历史统计指标。

最重要的结论是：Baostock 可以直接提供不少基础财务指标，也能提供日线中的 PE、PB、PS 等估值数据；但扣非净利润、股息率、历史 PE/PB 分位等指标，不能简单认为都能通过一个接口直接获取，其中一些需要额外数据源或自行计算。

[image](https://www.google.com/s2/favicons?domain=https://github.com\&sz=32)

GitHub

+1



## 一、财务指标：对应哪些接口

主要使用以下接口：

- `query_profit_data()`：盈利能力
- `query_cash_flow_data()`：现金流量相关比率
- `query_balance_data()`：偿债能力
- `query_dupont_data()`：杜邦分析
- `query_history_k_data_plus()`：历史行情及部分估值指标

这些财务接口通常按股票代码、年份和季度查询，例如 `code="sh.600000", year=2025, quarter=4`。

[image](https://www.google.com/s2/favicons?domain=https://github.com\&sz=32)

GitHub

+1



| 你需要的指标 | Baostock 接口 / 字段                                         | 获取方式与注意事项                                                       |
| ------ | -------------------------------------------------------- | --------------------------------------------------------------- |
| 营业收入   | `query_profit_data()` → `MBRevenue`                      | 主营业务收入，单位通常为万元；不应直接等同于所有口径的营业总收入。                               |
| 净利润    | `query_profit_data()` → `netProfit`                      | 直接获取，注意核对其净利润口径。                                                |
| 扣非净利润  | 未发现对应的直接字段                                               | 需要额外数据源提供扣非净利润，或自行获取归母净利润及非经常性损益数据后计算。                          |
| 经营现金流  | `query_cash_flow_data()` → `CFOToOR`、`CFOToNP`、`CFOToGr` | 这些是经营现金净流量与收入、净利润的比率，不是经营活动现金流净额本身。                             |
| ROE    | `query_profit_data()` → `roeAvg`                         | 直接获取平均净资产收益率；也可参考 `query_dupont_data()` → `dupontROE`，注意口径可能不同。 |
| 毛利率    | `query_profit_data()` → `gpMargin`                       | 直接获取销售毛利率。                                                      |
| 净利率    | `query_profit_data()` → `npMargin`                       | 直接获取销售净利率。                                                      |
| 资产负债率  | `query_balance_data()` → `liabilityToAsset`              | 直接获取。                                                           |

字段和接口对应关系参照 Baostock 财务 API 文档。

[image](https://www.google.com/s2/favicons?domain=https://github.com\&sz=32)

GitHub

+1



### 关于经营现金流，需要特别注意

如果你要的是财务报表中的经营活动产生的现金流量净额，而不是现金流比率，那么不能直接把 `CFOToOR` 当成现金流金额。

同样，如果你做长期选股或网格交易标的质量筛选，扣非净利润也很重要：它用于观察企业主营经营的盈利质量，不能用普通净利润直接替代。

## 二、估值指标：PE、PB、PS、股息率

| 你需要的指标  | Baostock 接口 / 字段                                        | 获取方式与注意事项                     |
| ------- | ------------------------------------------------------- | ----------------------------- |
| PE（市盈率） | `query_history_k_data_plus()` → `peTTM`                 | 直接获取滚动市盈率 TTM。                |
| PB（市净率） | 同上 → `pbMRQ`                                            | 直接获取市净率，采用最近一期披露的净资产口径。       |
| PS（市销率） | 同上 → `psTTM`                                            | 直接获取滚动市销率 TTM。                |
| 股息率     | `query_dividend_data()` + `query_history_k_data_plus()` | 需要结合现金分红和股价计算，文档没有提供直接的股息率字段。 |

日线估值字段及其口径见官方 API 文档。

[image](https://www.google.com/s2/favicons?domain=https://github.com\&sz=32)

GitHub



### 股息率怎么计算？

`query_dividend_data()` 可以获取以下相关字段：

- `dividOperateDate`：除权除息日期
- `dividCashPsBeforeTax`：每股税前现金股利
- `dividCashPsAfterTax`：每股税后现金股利

可以据此计算股息率。

[image](https://www.google.com/s2/favicons?domain=https://github.com\&sz=32)

GitHub



常见计算方式：

\\[ \text{股息率}= \frac{\text{过去12个月每股现金分红}}{\text{当前股价}}\times100\\% \\]

注意：

1. 应明确采用税前还是税后股息。
2. 过去12个月股息率与最近一个完整财年的股息率不是同一个口径。
3. 现金分红应按实际分红方案及实施日期处理，避免将预案和已实施分红重复计入。

## 三、TTM PE、历史 PE 分位、历史 PB 分位

| 你需要的指标   | Baostock 能否直接获取 | 推荐实现方式                  |
| -------- | --------------- | ----------------------- |
| TTM PE   | 可以              | 日线 `peTTM`              |
| 历史 PE 分位 | 没有直接的分位字段       | 获取历史日线 `peTTM`，自行计算历史分位 |
| 历史 PB 分位 | 没有直接的分位字段       | 获取历史日线 `pbMRQ`，自行计算历史分位 |

其中，Baostock 的 `peTTM` 本身就是滚动市盈率，不需要再用季度净利润手工拼接 TTM PE。

[image](https://www.google.com/s2/favicons?domain=https://github.com\&sz=32)

GitHub



### 历史分位怎么计算？

例如，你想计算某只股票过去 5 年的 PE 分位：

1. 通过 `query_history_k_data_plus()` 获取近 5 年的 `date,peTTM`。
2. 去除空值、无效值，并按日期排序。
3. 取当前 PE 与历史 PE 分布进行比较。
4. 计算历史 PE 小于或等于当前 PE 的有效交易日占比。

\\[ \text{PE分位}= \frac{\\#\\{PE_i\le PE\_{\text{当前}}\\}} {\text{有效历史PE样本数}}\times100\\% \\]

PB 分位的计算方法相同，只需把 `peTTM` 替换成 `pbMRQ`。

举例：如果当前 PE 高于过去 5 年 80% 的有效交易日，那么当前 PE 的历史分位约为 80%。这不代表股票一定高估，只代表其估值在选定历史区间中相对偏高。

实际计算时还有两个细节：

- 对亏损公司的负 PE、极端 PE 值和空值，应预先制定统一处理规则，不能随意混入正常估值分布。
- 计算历史分位时，必须使用当时可获得的数据口径；如果把今天的财务信息倒灌到历史日期，可能产生前视偏差。

## 四、汇总：你需要调用的接口清单

1\. `query_history_k_data_plus()`

日线行情及估值

获取 `date, close, peTTM, pbMRQ, psTTM`，用于 PE/PB/PS、TTM PE 和历史估值分位。

2\. `query_profit_data()`

盈利能力

获取 `roeAvg, npMargin, gpMargin, netProfit, MBRevenue`。

3\. `query_cash_flow_data()`

现金流质量比率

获取 `CFOToOR, CFOToNP, CFOToGr`。注意它们是比率，不是现金流净额。

4\. `query_balance_data()`

偿债能力

获取 `liabilityToAsset`。

5\. `query_dividend_data()`

现金分红

获取每股现金股利及除权除息日期，配合股价计算股息率。

6\. `query_dupont_data()`（可选）

补充 ROE 分析

可用于获取 `dupontROE` 等杜邦分析指标，与 `roeAvg` 交叉参考。

如果你的目标是建立 A 股长期波段 / 网格交易选股程序，我建议先把这些指标分为“直接获取”“计算得到”“需要补充数据源”三类，并把财报发布日期、历史估值和现金分红的时间口径统一。这样后续才能可靠地做历史回测和每日更新。