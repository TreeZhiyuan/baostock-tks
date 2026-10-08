-- baostock query_history_k_data_plus历史A股K线统一表
CREATE TABLE IF NOT EXISTS history_k_data (
    trade_date DATE NOT NULL,
    trade_time VARCHAR NOT NULL DEFAULT '',
    code VARCHAR NOT NULL,
    frequency VARCHAR NOT NULL,
    open DOUBLE,
    high DOUBLE,
    low DOUBLE,
    close DOUBLE,
    preclose DOUBLE,
    volume BIGINT,
    amount DOUBLE,
    adjustflag TINYINT NOT NULL,
    turn DOUBLE,
    tradestatus TINYINT,
    pct_chg DOUBLE,
    pe_ttm DOUBLE,
    ps_ttm DOUBLE,
    pcf_ncf_ttm DOUBLE,
    pb_mrq DOUBLE,
    is_st TINYINT,
    PRIMARY KEY (code, frequency, adjustflag, trade_date, trade_time),
    CHECK (frequency IN ('d', 'w', 'm', '5', '15', '30', '60')),
    CHECK (adjustflag IN (1, 2, 3))
);

COMMENT ON TABLE history_k_data IS 'Baostock query_history_k_data_plus历史A股日、周、月及分钟K线数据';
COMMENT ON COLUMN history_k_data.trade_date IS '交易所行情日期，对应接口date字段';
COMMENT ON COLUMN history_k_data.trade_time IS '交易所行情时间，对应分钟线time字段；日、周、月线为空字符串';
COMMENT ON COLUMN history_k_data.code IS '证券代码，例如sh.600000；分钟线不支持指数';
COMMENT ON COLUMN history_k_data.frequency IS 'K线周期：d日、w周、m月、5/15/30/60分钟';
COMMENT ON COLUMN history_k_data.open IS '开盘价，单位人民币元';
COMMENT ON COLUMN history_k_data.high IS '最高价，单位人民币元';
COMMENT ON COLUMN history_k_data.low IS '最低价，单位人民币元';
COMMENT ON COLUMN history_k_data.close IS '收盘价，单位人民币元';
COMMENT ON COLUMN history_k_data.preclose IS '前收盘价；周、月及分钟线接口不返回时为空';
COMMENT ON COLUMN history_k_data.volume IS '成交量，单位股；分钟线为时间范围内累计成交量';
COMMENT ON COLUMN history_k_data.amount IS '成交额，单位人民币元；分钟线为时间范围内累计成交额';
COMMENT ON COLUMN history_k_data.adjustflag IS '复权状态：1后复权、2前复权、3不复权';
COMMENT ON COLUMN history_k_data.turn IS '换手率百分比；分钟线接口不返回时为空';
COMMENT ON COLUMN history_k_data.tradestatus IS '交易状态：1正常交易、0停牌；周、月及分钟线接口不返回时为空';
COMMENT ON COLUMN history_k_data.pct_chg IS '涨跌幅百分比；分钟线接口不返回时为空';
COMMENT ON COLUMN history_k_data.pe_ttm IS '滚动市盈率，对应API的peTTM；接口不返回时为空';
COMMENT ON COLUMN history_k_data.ps_ttm IS '滚动市销率，对应API的psTTM；接口不返回时为空';
COMMENT ON COLUMN history_k_data.pcf_ncf_ttm IS '滚动市现率，对应API的pcfNcfTTM；接口不返回时为空';
COMMENT ON COLUMN history_k_data.pb_mrq IS '市净率，对应API的pbMRQ；接口不返回时为空';
COMMENT ON COLUMN history_k_data.is_st IS '是否ST：1是、0否；周、月及分钟线接口不返回时为空';
