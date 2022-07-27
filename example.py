import json

import okx.Account_api as Account
import okx.Funding_api as Funding
import okx.Market_api as Market
import okx.Public_api as Public
import okx.Trade_api as Trade
import okx.status_api as Status
import okx.subAccount_api as SubAccount
import okx.TradingData_api as TradingData
import okx.Broker_api as Broker
import okx.Convert_api as Convert
import okx.FDBroker_api as FDBroker
import okx.Rfq_api as Rfq
import okx.TradingBot_api as TradingBot

if __name__ == '__main__':
    api_key = "f76a1e05-cc56-43fd-aa6a-88aa3e51b6a2"
    secret_key = "A23C7CEB8046F39369CF73BDEBE985F5"
    passphrase = "Kangkang1_"

    # flag是实盘与模拟盘的切换参数 flag is the key parameter which can help you to change between demo and real trading.
    flag = '1'  # 模拟盘 demo trading
    # flag = '0'  # 实盘 real trading

    # account api
    accountAPI = Account.AccountAPI(api_key, secret_key, passphrase, False, flag)
    # 查看账户持仓风险 GET Position_risk
    # result = accountAPI.get_position_risk('SWAP')
    # 查看账户余额  Get Balance
    # result = accountAPI.get_account('USDT')
    # 查看持仓信息  Get Positions
    # result = accountAPI.get_positions('FUTURES', 'BTC-USD-210402')
    # 查看历史持仓信息
    # result = accountAPI.get_positions_history(instType = '', instId = '', mgnMode = '', type = '', after = '', before = '', limit = '')
    # 账单流水查询（近七天） Get Bills Details (recent 7 days)
    # result = accountAPI.get_bills_detail('FUTURES', 'BTC', 'cross')
    # 账单流水查询（近三个月） Get Bills Details (recent 3 months)
    # result = accountAPI.get_bills_details('FUTURES', 'BTC', 'cross')
    # 查看账户配置  Get Account Configuration
    # result = accountAPI.get_account_config()
    # 设置持仓模式  Set Position mode
    # result = accountAPI.get_position_mode('long_short_mode')
    # 设置杠杆倍数  Set Leverage
    # result = accountAPI.set_leverage(instId='BTC-USD-210402', lever='10', mgnMode='cross')
    # 获取最大可交易数量  Get Maximum Tradable Size For Instrument
    # result = accountAPI.get_maximum_trade_size('BTC-USDT-SWAP', 'cross', leverage='10')
    # 获取最大可用数量  Get Maximum Available Tradable Amount
    # result = accountAPI.get_max_avail_size('BTC-USDT-210402', 'isolated', 'BTC')
    # 调整保证金  Increase/Decrease margint
    # result = accountAPI.Adjustment_margin('BTC-USDT-210409', 'long', 'add', '100')
    # 获取杠杆倍数 Get Leverage
    # result = accountAPI.get_leverage('BTC-USDT-210409', 'isolated')
    # 获取交易产品最大可借  Get the maximum loan of instrument
    # result = accountAPI.get_max_load('BTC-USDT', 'cross', 'BTC')
    # 获取当前账户交易手续费费率  Get Fee Rates
    # result = accountAPI.get_fee_rates('FUTURES', '', category='1')
    # 获取计息记录  Get interest-accrued
    # result = accountAPI.get_interest_accrued('BTC-USDT', 'BTC', 'isolated', '', '', '10', '')
    # 获取用户当前杠杆借币利率 Get interest rate
    # result = accountAPI.get_interest_rate()
    # 期权希腊字母PA / BS切换  Set Greeks (PA/BS)
    # result = accountAPI.set_greeks('BS')
    # 逐仓交易设置 Set Isolated Mode
    # result = accountAPI.set_isolated_mode()
    # 查看账户最大可转余额  Get Maximum Withdrawals
    # result = accountAPI.get_max_withdrawal('')
    # 查看账户特定风险状态 Get account risk state (Only applicable to Portfolio margin account)
    # result = accountAPI.get_account_risk()
    # 尊享借币还币 GET Enjoy borrowing and returning money
    # result = accountAPI.borrow_repay('BTC', 'borrow', '10')
    # 获取尊享借币还币历史 Get the privileged currency borrowing and repayment history
    # result = accountAPI.get_borrow_repay_history(ccy = '', after = '', before = '', limit = '')
    # 获取借币利率与限额 GET Obtain borrowing rate and limit
    # result = accountAPI.get_interest_limits(type = '2', ccy = 'ETH')
    # 组合保证金的虚拟持仓保证金计算 POST Simulated Margin
    # result = accountAPI.get_simulated_margin()
    # 查看账户Greeks GET GREEKS
    # result = accountAPI.get_greeks()

    # funding api
    fundingAPI = Funding.FundingAPI(api_key, secret_key, passphrase, False, flag)
    # 获取充值地址信息  Get Deposit Address
    # result = fundingAPI.get_deposit_address('')
    # 获取资金账户余额信息  Get Balance
    # result = fundingAPI.get_balances('BTC')
    # 资金划转  Funds Transfer
    # result = fundingAPI.funds_transfer(ccy='', amt='', type='1', froms="", to="",subAcct='')
    # 获取资金划转状态 Transfer State
    # result = fundingAPI.transfer_state(transId='', type='')
    # 提币  Withdrawal
    # result = fundingAPI.coin_withdraw('usdt', '2', '3', '', '', '0')
    # 获取充值记录  Get Deposit History
    # result = fundingAPI.get_deposit_history()
    # 获取币种列表  Get Currencies
    # result = fundingAPI.get_currency()
    # 余币宝申购/赎回  PiggyBank Purchase/Redemption
    # result = fundingAPI.purchase_redempt('BTC', '1', 'purchase')
    # 资金流水查询  Asset Bills Details
    # result = fundingAPI.get_bills()
    # 获取余币宝余额 PIGGY BALABCE
    # result = fundingAPI.get_piggy_balance()
    # 闪电网络充币
    # result = fundingAPI.get_deposit_lightning(ccy='BTC',amt='0.01')
    # 闪电网络提币
    # result = fundingAPI.withdrawal_lightning(ccy='BTC',invoice='0.01',memo='')
    # 撤销提币 CANCEL_WITHDRAWAL
    # result = fundingAPI.cancel_withdrawal(wdId='BTC')
    # 获取提币记录  Get Withdrawal History
    # result = fundingAPI.get_withdrawal_history()
    # 小额资产兑换 CONVERT_DUST_ASSETS
    # result = fundingAPI.convert_dust_assets()
    # 获取账户资产估值 GET Obtain account asset valuation
    # result = fundingAPI.get_asset_valuation(ccy = 'USDT')
    # 设置余币宝借贷利率 POST SET LENDING RATE
    # result = fundingAPI.set_lending_rate(ccy = 'USDT',rate='')
    # 获取余币宝出借明细 GET LENDING HISTORY
    # result = fundingAPI.get_lending_rate(ccy = '')
    # 获取市场借贷信息（公共) GET LENDING RATE HISTORY
    # result = fundingAPI.get_lending_rate_history(ccy = '')
    # 获取市场借贷历史（公共）GET LENDING RATE SUMMARY
    # result = fundingAPI.get_lending_rate_summary(ccy = '')

    # convert api
    convertAPI = Convert.ConvertAPI(api_key, secret_key, passphrase, False, flag)
    # 获取闪兑币种列表  Get Currencies
    # result = convertAPI.get_currencies()
    # 获取闪兑币对信息  Get Currency-pair
    # result = convertAPI.get_currency_pair(fromCcy = 'USDT', toCcy = 'BTC')
    # 闪兑预估询价  Estimate-quote
    # result = convertAPI.estimate_quote(baseCcy = 'OKB', quoteCcy = 'USDT', side = 'sell', rfqSz = '1', rfqSzCcy = 'USDT', clQReqId = '')
    # 闪兑交易  Convert-trade
    # result = convertAPI.convert_trade(quoteId='quoterOKB-USDT16480319751107680', baseCcy='OKB', quoteCcy='USDT',
    #                                   side='sell', sz='1', szCcy='USDT', clTReqId='',tag='')
    # 获取闪兑交易历史  Get Convert-history
    # result = convertAPI.get_convert_history(after = '', before = '', limit = '')

    # market api
    marketAPI = Market.MarketAPI(api_key, secret_key, passphrase, True, flag)
    # 获取所有产品行情信息  Get Tickers
    # result = marketAPI.get_tickers('SWAP')
    # 获取单个产品行情信息  Get Ticker
    # result = marketAPI.get_ticker('BTC-USDT')
    # 获取指数行情  Get Index Tickers
    # result = marketAPI.get_index_ticker('BTC', 'BTC-USD')
    # 获取产品深度  Get Order Book
    # result = marketAPI.get_orderbook('BTC-USDT-210402', '400')
    # 获取所有交易产品K线数据  Get Candlesticks
    # result = marketAPI.get_candlesticks('BTC-USDT-210924', bar='1m')
    # 获取交易产品历史K线数据（仅主流币实盘数据）  Get Candlesticks History（top currencies in real-trading only）
    # result = marketAPI.get_history_candlesticks('BTC-USDT-SWAP')
    # 获取指数K线数据  Get Index Candlesticks
    # result = marketAPI.get_index_candlesticks('BTC-USDT')
    # 获取标记价格K线数据  Get Mark Price Candlesticks
    # result = marketAPI.get_markprice_candlesticks('BTC-USDT')
    # 获取交易产品公共成交数据  Get Trades
    # result = marketAPI.get_trades('BTC-USDT', '400')
    # 获取平台24小时成交总量  Get Platform 24 Volume
    # result = marketAPI.get_volume()
    # Oracle 上链交易数据 GET Oracle
    # result = marketAPI.get_oracle()
    # 获取指数成分数据 GET Index Components
    # result = marketAPI.get_index_components(index='')
    # 获取法币汇率 GET exchange rate in legal currency
    # result = marketAPI.get_exchange_rate()
    # 获取交易产品公共历史成交数据
    # result = marketAPI.get_history_trades(instId = 'BTC-USDT', after = '', before = '', limit = '')
    # 获取大宗交易所有产品行情信息
    # result = marketAPI.get_block_tickers(instType = 'SWAP', uly = 'BTC-USDT')
    # 获取大宗交易单个产品行情信息
    # result = marketAPI.get_block_ticker(instId = 'BTC-USDT')
    # 获取大宗交易公共成交数据
    # result = marketAPI.get_block_trades(instId = 'BTC-USDT')

    # public api
    publicAPI = Public.PublicAPI(api_key, secret_key, passphrase, False, flag)
    # 获取交易产品基础信息  Get instrument
    # result = publicAPI.get_instruments('SWAP', 'BTC-USDT')
    # 获取交割和行权记录  Get Delivery/Exercise History
    # result = publicAPI.get_deliver_history('FUTURES', 'BTC-USD')
    # 获取持仓总量  Get Open Interest
    # result = publicAPI.get_open_interest('SWAP')
    # 获取永续合约当前资金费率  Get Funding Rate
    # result = publicAPI.get_funding_rate('BTC-USD-SWAP')
    # 获取永续合约历史资金费率  Get Funding Rate History
    # result = publicAPI.funding_rate_history('BTC-USD-SWAP')
    # 获取限价  Get Limit Price
    # result = publicAPI.get_price_limit('BTC-USD-210402')
    # 获取期权定价  Get Option Market Data
    # result = publicAPI.get_opt_summary('BTC-USD')
    # 获取预估交割/行权价格  Get Estimated Delivery/Excercise Price
    # result = publicAPI.get_estimated_price('ETH-USD-210326')
    # 获取免息额度和币种折算率  Get Discount Rate And Interest-Free Quota
    # result = publicAPI.discount_interest_free_quota('')
    # 获取系统时间  Get System Time
    # result = publicAPI.get_system_time()
    # 获取平台公共爆仓单信息  Get Liquidation Orders
    # result = publicAPI.get_liquidation_orders('FUTURES', uly='BTC-USDT', alias='next_quarter', state='filled')
    # 获取标记价格  Get Mark Price
    # result = publicAPI.get_mark_price('FUTURES')
    # 获取合约衍生品仓位档位 Get Position Tiers
    # result = publicAPI.get_tier(instType='MARGIN', instId='BTC-USDT', tdMode='cross')
    # 获取杠杆利率和借币限额公共信息 Get Interest Rate and Loan Quota
    # result = publicAPI.get_interest_loan()
    # 获取合约衍生品标的指数 Get underlying
    # result = publicAPI.get_underlying(instType='FUTURES')
    # 获取尊享借币杠杆利率和借币限额 GET Obtain the privileged currency borrowing leverage rate and currency borrowing limit
    # result = publicAPI.get_vip_interest_rate_loan_quota()
    # 获取风险准备金余额
    # result = publicAPI.get_insurance_fund(instType = 'SWAP', type = '', uly = 'BTC-USDT', ccy = '', before = '', after = '', limit = '')
    # 张币转换
    # result = publicAPI.convert_contract_coin(type = '2', instId = 'BTC-USDT-SWAP', sz = '1', px = '', unit = '')

    # trading data
    tradingDataAPI = TradingData.TradingDataAPI(api_key, secret_key, passphrase, False, flag)
    # 获取支持币种 Get support coin
    # result = tradingDataAPI.get_support_coin()
    # 获取币币或衍生品主动买入/卖出情况 Get taker volume
    # result = tradingDataAPI.get_taker_volume(ccy='BTC', instType='SPOT')
    # 获取杠杆多空比 Get Margin lending ratio
    # result = tradingDataAPI.get_margin_lending_ratio('BTC')
    # 获取多空持仓人数比 Get Long/Short ratio
    # result = tradingDataAPI.get_long_short_ratio('BTC')
    # 获取持仓总量及交易量 Get contracts open interest and volume
    # result = tradingDataAPI.get_contracts_interest_volume('BTC')
    # 获取期权合约持仓总量及交易量 Get Options open interest and volume
    # result = tradingDataAPI.get_options_interest_volume('BTC')
    # 看涨/看跌期权合约 持仓总量比/交易总量比 Get Put/Call ratio
    # result = tradingDataAPI.get_put_call_ratio('BTC')
    # 看涨看跌持仓总量及交易总量（按到期日分） Get open interest and volume (expiry)
    # result = tradingDataAPI.get_interest_volume_expiry('BTC')
    # 看涨看跌持仓总量及交易总量（按执行价格分）Get open interest and volume (strike)
    # result = tradingDataAPI.get_interest_volume_strike('BTC', '20210924')
    # 看跌/看涨期权合约 主动买入/卖出量  Get Taker flow
    # result = tradingDataAPI.get_taker_flow('BTC')

    # trade api
    tradeAPI = Trade.TradeAPI(api_key, secret_key, passphrase, False, flag)
    # 下单  Place Order
    # result = tradeAPI.place_order(instId='BTC-USDT-210326', tdMode='cross', side='sell', posSide='short',
    #                               ordType='market', sz='100',tgtCcy='',banAmend='')
    # 批量下单  Place Multiple Orders
    # result = tradeAPI.place_multiple_orders([
    #     {'instId': 'BTC-USD-210402', 'tdMode': 'isolated', 'side': 'buy', 'ordType': 'limit', 'sz': '1', 'px': '17400',
    #      'posSide': 'long',
    #      'clOrdId': 'a12344', 'tag': 'test1210','tgtCcy':''},
    #     {'instId': 'BTC-USD-210409', 'tdMode': 'isolated', 'side': 'buy', 'ordType': 'limit', 'sz': '1', 'px': '17359',
    #      'posSide': 'long',
    #      'clOrdId': 'a12344444', 'tag': 'test1211','tgtCcy':''}
    # ])

    # 撤单  Cancel Order
    # result = tradeAPI.cancel_order('BTC-USD-201225', '257164323454332928')
    # 批量撤单  Cancel Multiple Orders
    # result = tradeAPI.cancel_multiple_orders([
    #     {"instId": "BTC-USD-210402", "ordId": "297389358169071616"},
    #     {"instId": "BTC-USD-210409", "ordId": "297389358169071617"}
    # ])

    # 修改订单  Amend Order
    # result = tradeAPI.amend_order()
    # 批量修改订单  Amend Multiple Orders
    # result = tradeAPI.amend_multiple_orders(
    #     [{'instId': 'BTC-USD-201225', 'cxlOnFail': 'false', 'ordId': '257551616434384896', 'newPx': '17880'},
    #      {'instId': 'BTC-USD-201225', 'cxlOnFail': 'false', 'ordId': '257551616652488704', 'newPx': '17882'}
    #      ])

    # 市价仓位全平  Close Positions
    # result = tradeAPI.close_positions('BTC-USDT-210409', 'isolated', 'long', '')
    # 获取订单信息  Get Order Details
    # result = tradeAPI.get_orders('BTC-USD-201225', '257173039968825345')
    # 获取未成交订单列表  Get Order List
    # result = tradeAPI.get_order_list()
    # 获取历史订单记录（近七天） Get Order History (last 7 days）
    # result = tradeAPI.get_orders_history('FUTURES')
    # 获取历史订单记录（近三个月） Get Order History (last 3 months)
    # result = tradeAPI.orders_history_archive('FUTURES')
    # 获取成交明细(三天)  Get Transaction Details
    # result = tradeAPI.get_fills
    # 获取成交明细(三个月)  Get Transaction Details History
    # result = tradeAPI.get_fills_history(instType='SPOT')
    # 策略委托下单  Place Algo Order
    # result = tradeAPI.place_algo_order('BTC-USDT-SWAP', 'isolated', 'buy', ordType='conditional',
    #                                    sz='100',posSide='long', tpTriggerPx='60000', tpOrdPx='59999',
    #                                   tpTriggerPxType = 'last', slTriggerPxType = 'last')
    # 撤销策略委托订单  Cancel Algo Order
    # result = tradeAPI.cancel_algo_order([{'algoId': '297394002194735104', 'instId': 'BTC-USDT-210409'}])
    # 撤销高级策略委托订单
    # result = tradeAPI.cancel_advance_algos([ {"algoId":"198273485","instId":"BTC-USDT"}])
    # 获取未完成策略委托单列表  Get Algo Order List
    # result = tradeAPI.order_algos_list('conditional', instType='FUTURES')
    # 获取历史策略委托单列表  Get Algo Order History
    # result = tradeAPI.order_algos_history('conditional', 'canceled', instType='FUTURES')

    # 子账户API subAccount
    subAccountAPI = SubAccount.SubAccountAPI(api_key, secret_key, passphrase, False, flag)
    # 查询子账户的交易账户余额(适用于母账户) Query detailed balance info of Trading Account of a sub-account via the master account
    # result = subAccountAPI.balances(subAcct='')
    # 查询子账户转账记录(仅适用于母账户) History of sub-account transfer(applies to master accounts only)
    # result = subAccountAPI.bills()
    # 查看子账户列表(仅适用于母账户) View sub-account list(applies to master accounts only)
    # result = subAccountAPI.view_list()
    # 子账户间划转 Transfer between subAccounts
    # result = subAccountAPI.subAccount_transfer(ccy='USDT', amt='1', froms='6', to='6', fromSubAccount='1',
    #                                            toSubAccount='2')
    # 查看被托管子账户列表 entrust-subaccount-list
    # result = subAccountAPI.entrust_subaccount_list(subAcct = '')

    # BrokerAPI
    BrokerAPI = Broker.BrokerAPI(api_key, secret_key, passphrase, False, flag)
    # 获取独立经纪商账户信息 GET Obtain independent broker account information
    # result = BrokerAPI.broker_info()
    # 创建子账户 Create sub account
    # result = BrokerAPI.create_subaccount(subAcct = 'qwerty', label = '', acctLv = '1')
    # 删除子账户 Delete sub account
    # result = BrokerAPI.delete_subaccount(subAcct = 'qwerty')
    # 获取子账户列表 Get sub account list
    # result = BrokerAPI.subaccount_info(page = '', subAcct = '', limit = '')
    # 设置子账户的账户等级 Set account level of sub account
    # result = BrokerAPI.set_subaccount_level(subAcct = 'qwerty', acctLv = '1')
    # 设置子账户的交易手续费费率 Set transaction fee rate of sub account
    # result = BrokerAPI.set_subaccount_fee_rate(subAcct = 'qwerty', instType = 'SPOT', chgType = 'absolute', chgTaker = '0.1bp', chgMaker = '', effDate = '')
    # 创建子账户充值地址 Create sub account recharge address
    # result = BrokerAPI.subaccount_deposit_address(subAcct = 'qwerty', ccy = 'BTC', chain = '', addrType = '', to = '')
    # 获取子账户获取充值记录 Get sub account recharge record
    # result = BrokerAPI.subaccount_deposit_history(subAcct = 'qwerty', ccy = 'BTC', txId = '', state = '', after = '', before = '', limit = '')
    # 获取子账户返佣记录 Get rebate record of sub account
    # result = BrokerAPI.rebate_daily(subAcct = 'qwerty', begin = '', end = '', page = '', limit = '')
    # 创建子账户的APIKEY Apikey for creating sub accounts
    # result = BrokerAPI.nd_create_apikey(subAcct = 'qwerty', label = '', passphrase = '', ip = '', perm = '')
    # 查询子账户的APIKEY
    # result = BrokerAPI.nd_select_apikey(subAcct = 'qwerty', apiKey = '')
    # 重置子账户的APIKEY
    # result = BrokerAPI.nd_modify_apikey(subAcct = 'qwerty', apiKey = '', label = '', perm = '', ip = '')
    # 删除子账户的APIKEY
    # result = BrokerAPI.nd_delete_apikey(subAcct = 'qwerty', apiKey = '')
    # 生成返佣明细下载链接
    # result = BrokerAPI.rebate_per_orders(begin = '', end = '')
    # 获取返佣明细下载链接
    # result = BrokerAPI.rebate_per_orders(type = '', begin = '', end = '')
    # 重置子账户充值地址
    # result = BrokerAPI.modify_subaccount_deposit_address(subAcct = 'qwert', ccy = 'BTC', chain = '', addr = '1', to = '6')

    # FDBrokerAPI
    FDBrokerAPI = FDBroker.FDBrokerAPI(api_key, secret_key, passphrase, False, flag)
    # 生成返佣明细下载链接
    # result = FDBrokerAPI.fd_rebate_per_orders(begin = '', end = '')
    # 获取返佣明细下载链接
    # result = FDBrokerAPI.fd_get_rebate_per_orders(type = '', begin = '', end = '')

    # 大宗交易(Rfq)API
    RfqAPI = Rfq.RfqAPI(api_key, secret_key, passphrase, False, flag)
    # 获取报价方信息
    # result = RfqAPI.counterparties()
    # 询价
    # result = RfqAPI.create_rfq(counterparties = ["TESTQ4","TESTQ2"], anonymous = False, clRfqId = '20220531test001', 
    #     legs = [{"instId":"BTC-USDT","sz":"1","side":"buy","tgtCcy":"base_ccy"},{"instId":"ETH-USDT","sz":"0.1","side":"buy","tgtCcy":"base_ccy"}])
    # 取消询价单
    # result = RfqAPI.cancel_rfq(rfqId = '3GIFPJ8', clRfqId = '')
    # 批量取消询价单
    # result = RfqAPI.cancel_batch_rfqs(rfqIds = '', clRfqIds = '')
    # 取消所有询价单
    # result = RfqAPI.cancel_all_rfqs()
    # 执行报价
    # result = RfqAPI.execute_quote(rfqId = '', quoteId = '')
    # 报价
    # result = RfqAPI.create_quote(rfqId = '', clQuoteId = '', quoteSide = 'buy', legs = [{"px":"39450.0","sz":"200000","instId":"BTC-USDT-SWAP","side":"buy"}])
    # 取消报价单
    # result = RfqAPI.cancel_quote(quoteId = '', clQuoteId = '')
    # 批量取消报价单
    # result = RfqAPI.cancel_batch_quotes(quoteIds = '', clQuoteIds = '')
    # 取消所有报价单
    # result = RfqAPI.cancel_all_quotes()
    # 获取询价单信息
    # result = RfqAPI.get_rfqs(rfqId = '', clRfqId = '', state = '', beginId = '', endId = '', limit = '')
    # 获取报价单信息
    # result = RfqAPI.get_quotes(rfqId = '', clRfqId = '', quoteId = '', clQuoteId = '', state = '', beginId = '', endId = '', limit = '')
    # 获取大宗交易信息
    # result = RfqAPI.get_rfq_trades(rfqId = '', clRfqId = '', quoteId = '', clQuoteId = '', state = '', beginId = '', endId = '', limit = '')
    # 获取大宗交易公共成交数据
    # result = RfqAPI.get_public_trades(beginId = '', endId = '', limit = '')

    # 网格交易
    TradingBot = TradingBot.TradingBotAPI(api_key, secret_key, passphrase, False, flag)
    # 网格策略下单
    # result = TradingBot.grid_order_algo(instId = 'BTC-USDT', algoOrdType = 'grid', maxPx = '100000', minPx = '10000', gridNum = '2', runType = '', tpTriggerPx = '', slTriggerPx = '', tag = '', baseSz = '1')
    # 修改网格策略订单
    # result = TradingBot.grid_amend_order_algo(algoId = '451791361361317888', instId = '', slTriggerPx = '', tpTriggerPx = '')
    # 网格策略停止
    # result = TradingBot.grid_stop_order_algo(algoId = '455784823937040384', instId = 'BTC-USDT', algoOrdType = 'grid', stopType = '1')
    # 获取未完成网格策略委托单列表
    # result = TradingBot.grid_orders_algo_pending(algoOrdType = 'grid', algoId = '', instId = '', instType = '', after = '', before = '', limit = '')
    # 获取历史网格策略委托单列表
    # result = TradingBot.grid_orders_algo_history(algoOrdType = 'grid', algoId = '', instId = '', instType = '', after = '', before = '', limit = '')
    # 获取网格策略委托订单详情
    # result = TradingBot.grid_orders_algo_details(algoOrdType = 'grid', algoId = '451805034968518656')
    # 获取网格策略委托子订单信息
    # result = TradingBot.grid_sub_orders(algoId = '451791361361317888', algoOrdType = 'grid', type = 'filled', groupId = '', after = '', before = '', limit = '')
    # 获取网格策略委托持仓
    # result = TradingBot.grid_positions(algoOrdType = '', algoId = '')
    # 现货网格提取利润
    # result = TradingBot.grid_withdraw_income(algoId = '455784823937040384')

    # 系统状态API(仅适用于实盘) system status
    Status = Status.StatusAPI(api_key, secret_key, passphrase, False, flag)
    # 查看系统的升级状态
    # result = Status.status()
    # print(json.dumps(result))
    # print(len(result['data']))

