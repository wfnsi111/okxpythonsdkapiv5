import okx.Account_api as Account
import okx.Trade_api as Trade


class AccountInfo:
    def __init__(self, api_key, secret_key, passphrase, status, use_server_time=False, flag='0'):
        self.accountAPI = Account.AccountAPI(api_key, secret_key, passphrase, use_server_time, flag)
        self.tradeAPI = Trade.TradeAPI(api_key, secret_key, passphrase, use_server_time, flag)
        self.passphrase = passphrase
        self.api_key = api_key
        self.secret_key = secret_key
        self.use_server_time = use_server_time
        self.flag = flag
        self.flag = status
        self.balance = 0
        self.msg = []
        self.order_info = []
        self.sz = 0
        self.algoID = None
        self.status = ''

    def get_my_balance(self):
        result = self.accountAPI.get_account('USDT')
        data = result.get('data')[0].get('details')[0]
        mybalance = data.get('availEq')
        frozenBal = data.get('frozenBal')
        return round(float(mybalance), 2), frozenBal

    def get_positions(self):
        result = self.accountAPI.get_positions('SWAP')
        order_lst = result.get('data', [])
        if order_lst:
            return order_lst
        return False
