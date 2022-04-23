# from distutils.log import Log, debug
import json
from unicodedata import decimal
from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware
from pathlib import Path
import time
import requests
import os
import decimal
import random
from LocalStorage import *
from Logger import *

class WebThree:
    def __init__(self):
        self.ls = LocalStorage()
        self.basic = '0x00'
        self._init()

    def _init(self):
        self.suffix = '.json'
        self.base_path = os.path.dirname(__file__) + os.sep
        self.network_base = self.base_path + 'network' + os.sep
        self.network_file = self.network_base + 'network' + self.suffix
        self.default_setting = self.ls.get_default_setting()

    def _init_network(self, network_name, apikey = '', rpc_url = ''):
        self.network_name = network_name
        self.network_path = self.base_path + 'network' + os.sep + network_name + os.sep
        self.contract_path = self.network_path + 'contract' + os.sep
        self.network_info_file = self.network_path + 'base.json'
        network = json.loads(self.ls.read_file(self.network_info_file))
        if apikey != '':
            network['apikey'] = apikey
        if rpc_url != '':
            network['rpc_url'] = rpc_url

        if apikey != '' or rpc_url != '':
            self.ls.w_file(json.dumps(network), self.network_info_file)
       
        self.w3 = Web3(Web3.HTTPProvider(network['rpc_url']))
        if network['app_env'] == 'test': 
            self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)  # 注入poa中间件 正式网络可去除

        self.network = network
        return network
    
    def get_network_info(self, network_name):
        network_info_file = self.base_path + 'network' + os.sep + network_name + os.sep + 'base.json'
        network = json.loads(self.ls.read_file(network_info_file))
        return network
    
    def _init_exchange(self, network_name, exchange_name):
        self.exchange_name = exchange_name
        exchange_path = self.network_base + network_name + os.sep + exchange_name + os.sep
        exchange_file = exchange_path + 'version' + self.suffix
        self.exchange = json.loads(self.ls.read_file(exchange_file))
        return self.exchange

    def _init_user(self, account, private_key):
        self.user = {
            'account' : account,
            'private_key' : private_key
        }
        
    def get_exchange(self):
        return self.ls.read_file()

    def import_contract(self, contract):
        try:
            Logger.info('导入合约：' + contract)
            info = self._contract_info(contract)
            # print(self.network)
            if info:
                return self.ls.import_contract(contract, info['symbol'], self.network['chain_name'])
            return []
        except Exception as e:
            Logger.info(e)
        return []

    def _contract_info(self, token):
        contract_base = self.network_path + 'contract/'+token+'/base' + self.suffix
        content = self.ls.read_file(contract_base)
        # print(content)
        if content:
            return json.loads(content)
        
        factory_address = ''
        router_address = ''
        for item in self.exchange:
            factory_ins = self.contract_instance(item['factory_address'])
            # print(factory_ins)
            pair_address = self.get_pair(factory_ins, token)
            if '0x0000000000000000000000000000000000000000' != pair_address:
                router_address = item['router_address']
                factory_address = item['factory_address']
                break
        
        if '0x0000000000000000000000000000000000000000' == pair_address:
            return []

        Logger.info('PAIR地址：' + pair_address)
        #pair合约实例
        pair_ins = self.contract_instance(pair_address)
        Logger.info('初始化pair合约实例')
        #获取交易对的顺序
        tokens = self.get_tokens(pair_ins)
        Logger.info('获取交易对的顺序')
        ins = self.contract_instance(token)
        Logger.info('初始化合约实例')
        arr = {
            'address' : token,
            'is_base' : 0,
            'decimals' : ins.functions.decimals().call(),
            'symbol' : ins.functions.symbol().call(),
            'name' : ins.functions.name().call(),
            'token1' : tokens[0],
            'token2' : tokens[1],
            'pair_address' : pair_address,
            'factory_address' : factory_address,
            'router_address' : router_address
        }
        self.ls.w_file(json.dumps(arr), contract_base)
        # 导入之后立即授权
        self.approve(ins, router_address, 10 * 10 ** 30)
        return arr
    
    def get_contract_pair(self, addr):
        pair_address = self.get_pair(self.factory_ins, addr, self.network['weth_address'])
        #pair合约实例
        pair_ins = self.contract_instance(pair_address)
        #获取交易对的顺序
        tokens = self.get_tokens(pair_ins)
        return [pair_address, pair_ins, tokens]

    def headers(self):
        my_headers = [  
            {'User-Agent': "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Win64; x64; Trident/6.0)"},
            {'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36"},
            {"User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Mobile Safari/537.36"},
            {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1'},
            {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'},
            {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36'},
            {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'}
        ]
        return random.choice(my_headers)

    def get_ad(self):
        url = 'http://www.pureland.me?q=ad'
        # print(url)
        # print(randdom_header)
        r = requests.get(url, headers=self.headers(), verify=False, timeout=10)
        if r:
            return r.json()
        else:
            return []

    #通过合约地址获取ABI
    def get_abi(self, contract_addr):
        abi_path = self.contract_path + contract_addr
        abi_file_path = abi_path + os.sep + 'abi' + self.suffix
        abi = ''
        if Path(abi_file_path).exists():
            abi = self.ls.read_file(abi_file_path)
        else:
            url = self.network['api_url'] + '/api?module=contract&action=getabi&address='+contract_addr+'&apikey='+self.network['apikey']
            # print(url)
            # print(randdom_header)
            r = requests.get(url, headers=self.headers(), verify=False, timeout=10)
            # print(r)
            if r:
                r = r.json()
                if int(r['status']) == 1:
                    abi = r['result']            
                    os.makedirs(abi_path, 0o777)
                    self.ls.w_file(abi, abi_file_path)
                else:
                    abi = ''
            else:
                abi = ''
        return abi

    #初始化合约
    def contract_instance(self, address):
        Logger.info('初始化合约:' + address)
        return self.w3.eth.contract(address=self.w3.toChecksumAddress(address), abi = self.get_abi(address))

    def get_nonce(self):
        nonce = self.w3.eth.getTransactionCount(self.user['account'], 'pending')
        return int(nonce) 

    def gas_price(self):
        return int(self.w3.eth.gasPrice * self.default_setting['gas_multiple']) # 获取当前交易费

    def gas_limit(self):
        return int(self.default_setting['gas_limit']) # 获取当前交易费

    #构建基础交易信息
    def build_transaction(self):
        gas_price = self.gas_price()
        gas_limit = self.gas_limit()
        nonce = self.get_nonce()
        Logger.info('nonce:' + str(nonce) + '  gas_price:' + str(gas_price) + '  gas_limit:' + str(gas_limit))
        return {"gasPrice": gas_price, "gas": gas_limit, "nonce": nonce}

    def build_swap_transaction(self, amount):
        gas_price = self.gas_price()
        gas_limit = self.gas_limit()
        nonce = self.get_nonce()
        Logger.info('nonce:' + str(nonce) + '  gas_price:' + str(gas_price) + '  gas_limit:' + str(gas_limit) + '  eth:' + str(amount))
        return {"from": self.user['account'], "gasPrice": gas_price, "gas": gas_limit,  "nonce": nonce, "value": self.w3.toWei(amount, 'ether')}

    def build_from_transaction(self):
        gas_price = self.gas_price()
        gas_limit = self.gas_limit()
        nonce = self.get_nonce()
        Logger.info('nonce:' + str(nonce) + '  gas_price:' + str(gas_price) + '  gas_limit:' + str(gas_limit))
        return {"from": self.user['account'], "gasPrice": gas_price, "gas": gas_limit,  "nonce": nonce}

    def build_router_transaction(self):
        gas_price = self.gas_price()
        gas_limit = self.gas_limit()
        nonce = self.get_nonce()
        Logger.info('nonce:' + str(nonce) + '  gas_price:' + str(gas_price) + '  gas_limit:' + str(gas_limit))
        return {"from": self.contract['router_address'], "gasPrice": gas_price, "gas": gas_limit,  "nonce": nonce}


    #构建交易
    def transfer(self, contract, to_address, amount):
        return contract.functions.transfer(to_address, self.w3.toWei(amount, 'ether')).buildTransaction(self.build_transaction())

    #创建钱包
    def create_account(self, pwd=''):
        account = self.w3.eth.account.create(pwd)
        return {
            'account': account._address,
            'private_key': (account._private_key).hex()
        }

    #获取钱包
    def get_account_by_key(self, key):
        # print(Web3.toChecksumAddress(key))
        account = self.w3.eth.account.privateKeyToAccount(key)
        Logger.info('获取钱包地址:' + account.address)
        return {
            'account': account.address,
            'private_key': (account.privateKey).hex()
        }

    #对交易签名
    def sign_txn(self, transaction):
        return self.w3.eth.account.signTransaction(transaction, self.user['private_key'])  # 返回签名

    #发送交易 返回交易hash
    def send(self, signed_txn):
        txn_hash = self.w3.eth.sendRawTransaction(signed_txn.rawTransaction)  # txn_hash 返回交易hash
        return txn_hash.hex()

    #通过hash获取交易结果
    def get_transaction_receipt(self, txn_hash):
        return self.w3.eth.getTransactionReceipt(txn_hash)  # txn_hash 返回交易hash

    #授权路由交易数量
    def approve(self, contract_ins, amount = 10 * 10 ** 30):
        try:
            transaction = contract_ins.functions.approve(self.contract['router_address'], amount * 10).buildTransaction(self.build_from_transaction())
            signed_txn = self.sign_txn(transaction)
            hash = self.send(signed_txn)
            Logger.info('授权哈希: ' + hash)
            return hash
        except Exception as e:
            Logger.info(e)
            return False
    
    #获取授权路由的数量
    def allowance(self, contract_ins, router_address):
        res = contract_ins.functions.allowance(self.w3.toChecksumAddress(self.user['account']), self.w3.toChecksumAddress(router_address)).call()
        if res == None or res == 'None':
            return 0
        return res

    #授权路由交易数量
    def transfer_from(self, contract_ins, amount):
        # print(self.user['account'], self.contract['router_address'], amount)

        transaction = contract_ins.functions.transferFrom(self.contract['router_address'], self.user['account'], amount).buildTransaction(self.build_from_transaction())
        # print(transaction)
        signed_txn = self.sign_txn(transaction)
        hash = self.send(signed_txn)
        Logger.info('确认交易金额: ' + hash)
        return transaction

    #发起基本币购买交易 
    def swapExactETHForTokens(self, router_ins, contract_address, buyer_addr, amount, min_amount):
        transaction = router_ins.functions.swapExactETHForTokens(self.w3.toWei(min_amount, 'ether'), [self.network['weth_address'], contract_address], buyer_addr, int(time.time()) + 60).buildTransaction(self.build_swap_transaction(amount))
        signed_txn = self.sign_txn(transaction)
        return self.send(signed_txn)

    #发起令牌兑换基本币
    def swapExactTokensForETH(self, router_ins, contract_address, seller_addr, amount, min_amount):
        transaction = router_ins.functions.swapExactTokensForETH(self.w3.toWei(amount, 'ether'), self.w3.toWei(min_amount, 'ether'), [
            self.w3.toChecksumAddress(contract_address),  #合约地址
            self.w3.toChecksumAddress(self.network['weth_address']) #weth地址
            ], self.w3.toChecksumAddress(seller_addr), #卖出用户地址
            int(time.time()) + 60).buildTransaction(self.build_from_transaction())
        signed_txn = self.sign_txn(transaction)
        return self.send(signed_txn)

    #bnb -> wbnb
    def deposit(self, contract, amount): 
        transaction = contract.functions.deposit().buildTransaction(self.build_swap_transaction(amount))
        signed_txn = self.sign_txn(transaction)
        return self.send(signed_txn)
    
    #wbnb -> bnb
    def withdraw(self, contract, amount): 
        transaction = contract.functions.withdraw(self.w3.toWei(amount, 'ether')).buildTransaction(self.build_transaction())
        signed_txn = self.sign_txn(transaction)
        return self.send(signed_txn)

    #查询主币余额
    def balance(self, addr):
        balance = '0'
        if addr:
            balance = self.w3.eth.getBalance(addr) / (10 ** self.network['decimals'])
        return balance

    #查询代币余额
    def balance_of(self, contract_addr, account):
        if account:
            ins = self.contract_instance(contract_addr)
            balance = ins.functions.balanceOf(account).call()
            decimals = ins.functions.decimals().call()
            return self.num_format(balance / (10 ** decimals))
        return '0'

    def num_format(self, value):
        return '{:.10f}'.format(value)

    #批量创建账户
    def batch_create(self, str = ''):
        while 1:
            res = self.create_account()
            if str in res['account']:
                Logger.info(res['account'] + "\t" + res['private_key'])
                # print(res['account'] + "\t" + res['private_key'])
                exit() 

    #获取交易对地址
    def get_pair(self, contract_ins, addr1):
        return contract_ins.functions.getPair(addr1, self.network['weth_address']).call()

    #获取资金池
    def get_pair_poor(self, pair_address):
        #通过交易对查看是否添加流动池 如果没有检测到循环检测
        pair_ins = self.contract_instance(pair_address)
        return self.get_poor_by_cyclic(pair_ins)

    #获取资金池
    def get_poor_by_cyclic(self, contract, i = 1):
        Logger.info('循环检测LP:' + str(i))
        i += 1
        lp = contract.functions.getReserves().call()
        if lp[0] > 0:
            return lp
        return self.get_liquidity_poor(contract, i)

     #获取资金池
    def get_poor_by_one(self, contract):
        lp = contract.functions.getReserves().call()
        if lp[0] > 0:
            return lp
        return []

    #获取交易对的两种币合约
    def get_tokens(self, contract):
        token0 = contract.functions.token0().call()
        token1 = contract.functions.token1().call()
        return [token0, token1]

    #获取结果
    def get_result(self, trans_hash):
        # Logger.info('获取交易结果：' + trans_hash)
        try:
            trans_res = self.get_transaction_receipt(trans_hash)
            if trans_res['status'] == 1:
                Logger.info('交易成功：' + trans_hash)
                return 1
            else:
                Logger.info('交易失败:' + json.dumps(trans_res))
                return 2
        except Exception as e:
            Logger.info(e)
            time.sleep(0.5)
            return self.get_result(trans_hash)

    #本币购买令牌
    def eth_for_token(self, amount, min_amount, trans_fail_num = 20):
        if trans_fail_num < 1:
            Logger.info('交易次数完成，交易失败')
            return 2
        trans_fail_num -= 1
        try:
            #发送交易
            trans_hash = self.swapExactETHForTokens(self.router_ins, self.contract['address'], self.user['account'], amount, min_amount)
            Logger.info('交易哈希：' + trans_hash)
            #获取结果
            res = self.get_result(trans_hash)
            if res == 1:
                return 1
            if res == 2:
                return self.eth_for_token(amount, min_amount, trans_fail_num)
        except Exception as e:
            Logger.info(e)
            return self.eth_for_token(amount, min_amount, trans_fail_num)

    #令牌卖出本币
    def token_for_eth(self, amount, min_eth, trans_fail_num = 20):
        if trans_fail_num < 1:
            Logger.info('交易次数完成，失败返回')
            return 2
        trans_fail_num -= 1
        try:
            trans_hash = self.swapExactTokensForETH(self.router_ins, self.contract['address'], self.user['account'], amount, min_eth)
            Logger.info('交易哈希：' + trans_hash)
            res = self.get_result(trans_hash)
            if res == 1:
                return 1
            if res == 2:
                return self.token_for_eth(amount, min_eth, trans_fail_num)
        except Exception as e:
            Logger.info(e)
            return self.token_for_eth(amount, min_eth, trans_fail_num)

    #令牌卖出本币
    def token_for_token(self, amount, min_eth, trans_fail_num = 20):
        pass

    #前端获取价格
    def get_pair_num(self, contract_info):
        #通过交易对查看是否添加流动池 如果没有检测到循环检测
        pair_ins = self.contract_instance(contract_info['pair_address'])
        major_coin = decimal.Decimal(0)
        contract_coin = decimal.Decimal(0)
        liquidity_poor = self.get_poor_by_one(pair_ins)
        if liquidity_poor:
            #判断交易对里 令牌的前后顺序 判断liquidity_poor令牌余额的前后顺序
            if contract_info['address'] == contract_info['token2']:
                major_coin = decimal.Decimal(liquidity_poor[0]) 
                contract_coin = decimal.Decimal(liquidity_poor[1])
            else:
                major_coin = decimal.Decimal(liquidity_poor[1])
                contract_coin = decimal.Decimal(liquidity_poor[0])

            major_coin = major_coin / 10 ** self.network['decimals']
            contract_coin = contract_coin / 10 ** contract_info['decimals'] * decimal.Decimal(1 - 0.003) #妈的，计算价格要减去工厂合约收取的0.3%的税 测试0.00276
            Logger.info('LP: Token0=' + str(major_coin) + '| Token1=' + str(contract_coin))

        return [major_coin, contract_coin]
    
    def get_price(self, amount, trans_type, liquidity_poor):
        #判断交易对里 令牌的前后顺序 判断liquidity_poor令牌余额的前后顺序
        if self.network['weth_address'] == self.contract['token1']:
            major_coin = decimal.Decimal(liquidity_poor[0]) / 10 ** self.network['decimals']
            contract_coin = decimal.Decimal(liquidity_poor[1]) / 10 ** self.contract['decimals'] * decimal.Decimal(1 - 0.003) #妈的，计算价格要减去工厂合约收取的0.3%的税
        else:
            major_coin = decimal.Decimal(liquidity_poor[1]) / 10 ** self.network['decimals']
            contract_coin = decimal.Decimal(liquidity_poor[0]) / 10 ** self.contract['decimals'] * decimal.Decimal(1 - 0.003) #妈的，计算价格要减去工厂合约收取的0.3%的税

        if trans_type == 'buy':
            contract_coin -= amount
        elif trans_type == 'sell':
            contract_coin += amount
        else:
            return 0
        return round(major_coin / contract_coin, self.network['decimals'])

    def swap(self, addr1, addr2, amount_in, slippage_tolerance, trans_fail_num):
        self.default_setting = self.ls.get_default_setting()
        if amount_in == 0 or amount_in == '':
            return 
        slippage_tolerance = decimal.Decimal(slippage_tolerance) / 100
        amount = decimal.Decimal(amount_in)

        if addr1 == self.basic and addr2 == self.network['major_address']:
            Logger.info('充值开始。。。')
            ins = self.contract_instance(self.network['major_address'])
            self.deposit(ins, amount)
        elif addr2 == self.basic and addr1 == self.network['major_address']:
            Logger.info('提现开始。。。')
            ins = self.contract_instance(self.network['major_address'])
            self.withdraw(ins, amount)
        elif addr1 == self.basic:
            self.contract = self._contract_info(addr2)
            Logger.info('交易开始: WETH -> ' + self.contract['symbol'])
            self.router_ins = self.contract_instance(self.contract['router_address'])
            liquidity_poor = self.get_pair_poor(self.contract['pair_address'])
            price = self.get_price(amount, 'buy', liquidity_poor)
             #购买将要得要的令牌数量
            get_amount = amount / price
            #购买允许得到的最少数量
            min_amount = get_amount - get_amount * slippage_tolerance
            Logger.info('买入: ' + str(amount) + ' | 最少收益:' + str(min_amount) + ' | 价格:'  + str(price))
            return self.eth_for_token(amount, min_amount, trans_fail_num)
        elif addr2 == self.basic:
            self.contract = self._contract_info(addr1)
            Logger.info('交易开始: ' + self.contract['symbol'] + ' -> WETH')

            #调用合约授权路由 卖出
            contract_ins = self.contract_instance(addr1)
            res = self.allowance(contract_ins, self.contract['router_address'])
            #检测是否有授权路由
            allowance_amount = decimal.Decimal(res)
            allowance_amount = allowance_amount / 10 ** self.contract['decimals']
            if allowance_amount < amount:
                res = self.approve(contract_ins, self.contract['router_address'], 10 * 10 ** 30)
                if res == False:
                    return 3
                result = self.get_result(res)
                if result != 1:
                    return 3

            liquidity_poor = self.get_pair_poor(self.contract['pair_address'])
            price = self.get_price(amount, 'sell', liquidity_poor)
            self.router_ins = self.contract_instance(self.contract['router_address'])
            amount = round(amount, self.contract['decimals'])
            #卖出数量
            get_eth = amount * price
            
            #卖出允许得到的最少基本币
            min_eth = round(get_eth - get_eth * slippage_tolerance, self.network['decimals'])

            Logger.info('卖出: ' + str(amount) + ' | 最少收益:' + str(min_eth) + ' | 价格:'  + str(price))
            return self.token_for_eth(amount, min_eth, trans_fail_num)
        else:
            self.token_for_token()

# if __name__ == "__main__":
#      w3 = WebThree()
#      ls = LocalStorage()
#      default_setting_info = ls.get_default_setting()
#      w3._init_network(default_setting_info['network'])
#      w3._init_exchange(default_setting_info['network'], default_setting_info['exchange'])
#      w3._contract_info('0x7ef95a0FEE0Dd31b22626fA2e10Ee6A223F8a684')


#     from_address = "0xb7ef288F8B422AeD51FF21415Ef1D283B39FE8D8"
#     from_private_key = "0x4fa8f778818f41d63840687d662a32fd1e65917774d8fe9ed8b01590ff4b667a"
#     contract_address = "0x3A999Af3348Ba1e336289b46Eae2FDbA5026D0ed"
#     contract_address = "0x1B368993a5C464f3E40c877fcaa9610e2cC33dBb"
#     amount = decimal.Decimal(100038) #交易金额
#     slippage_tolerance = 20  #滑点
#     trans_type = 'sell' #sell trans
#     trans_fail_num = 10
#     factory_type = 1 #工厂合约版本
#     slippage_tolerance = decimal.Decimal(slippage_tolerance) / 100

