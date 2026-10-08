-- baostock query_trade_dates交易日信息表
CREATE TABLE IF NOT EXISTS trade_calendar (
    calendar_date DATE NOT NULL PRIMARY KEY,
    is_trading_day TINYINT NOT NULL
);

COMMENT ON TABLE trade_calendar IS 'Baostock交易日历及交易日标志';
COMMENT ON COLUMN trade_calendar.calendar_date IS '日历日期';
COMMENT ON COLUMN trade_calendar.is_trading_day IS '是否交易日：1为交易日，0为非交易日';
