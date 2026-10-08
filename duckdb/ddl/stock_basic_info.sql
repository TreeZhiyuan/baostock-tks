-- baostock query_all_stock(day=...)证券基础信息快照表
CREATE TABLE IF NOT EXISTS stock_basic_info (
    query_date DATE NOT NULL,
    code VARCHAR NOT NULL,
    trade_status TINYINT,
    code_name VARCHAR,
    PRIMARY KEY (query_date, code)
);

COMMENT ON TABLE stock_basic_info IS 'baostock指定日期的全部证券基础信息';
COMMENT ON COLUMN stock_basic_info.query_date IS '查询日期，对应baostock query_all_stock的day参数';
COMMENT ON COLUMN stock_basic_info.code IS '证券代码，例如sh.600000';
COMMENT ON COLUMN stock_basic_info.trade_status IS '交易状态：1为正常交易，0为停牌';
COMMENT ON COLUMN stock_basic_info.code_name IS '证券名称';
