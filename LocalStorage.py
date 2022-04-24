from pathlib import Path
import os
from posixpath import split
import json
from Logger import *

class LocalStorage:
    def __init__(self):
        self._init()

    def _init(self):
        self.base_path = os.path.dirname(__file__) + os.sep
        self.user_path = self.base_path + 'user' + os.sep
        self.default = self.user_path + 'default_account.json'
        self.default_setting_path = self.user_path + 'default_setting.json'
        self.keys_path = self.user_path + 'private_keys.json'
    
    def import_contract(self, contract, name, network):
        contract_file = self.base_path + 'network' + os.sep + network + os.sep + 'contracts.json'
        content = self.get_content_by_file(contract_file)
        exists = {}
        index = 0
        for item in content:
            index += 1
            if contract == item['address']:
                exists = item
                break

        if exists:
            return exists

        current = {
            'name' :name,
            'address' :contract,
            'index' :index
        }
        content.append(current)
        self.w_file(json.dumps(content), contract_file)
        return current

    def get_contarct_list(self, network):
        self.contract_file = self.base_path + 'network' + os.sep + network + os.sep + 'contracts.json'
        content = self.get_content_by_file(self.contract_file)
        # print(content)
        res = []
        for item in content:
            str = ''
            res.append(item['name'] + str)
        return res
    
    def get_addr_by_indexs(self, index1, index2):
        content = self.get_content_by_file(self.contract_file)
        # print(content)
        addr1 = ''
        addr2 = ''
        for item in content:
            if item['index'] == index1:
                addr1 = item['address']
            if item['index'] == index2:
                addr2 = item['address']
            if addr1 and addr2:
                break
        return [addr1, addr2]
    
    def get_addr_by_index(self, index):
        content = self.get_content_by_file(self.contract_file)
        # print(content)
        addr1 = ''
        for item in content:
            if item['index'] == index:
                addr1 = item['address']
                break
        return addr1

    def get_private_keys(self):
        content = self.get_private_keys1()
        return self.keys_list(content)

    def keys_list(self, keys):
        res = []
        for item in keys:
            res.append(item['account'][0:6] + '...' + item['account'][38:42])
        return res

    def get_private_keys1(self):
        content_str = self.read_file(self.keys_path)
        content = []
        if content_str:
            content = json.loads(self.read_file(self.keys_path))
        return content

    def set_account(self, account):
        accounts = self.get_private_keys1()
        if accounts:
            is_insert = True
            i = 0
            for a in accounts:
                if a['account'] == account['account']:
                    account['index'] = i
                    is_insert = False
                    break
                i += 1
            if is_insert == True:
                accounts.append(account)
                account['index'] = i
        else:
            accounts = [account]
            account['index'] = 0
        
        self.w_file(json.dumps(account), self.default)
        res = {}
        res['list'] = self.keys_list(accounts)
        res['default'] = account
        res['index'] = account['index']
        self.w_file(json.dumps(accounts), self.keys_path)
        return res
        
    def get_content_by_file(self, path):
        content = json.loads(self.read_file(path))
        return content

    def get_default_account(self):
        str = self.read_file(self.default)
        content = []
        if str:
            content = json.loads(str)
        return content

    def set_default_account(self, index):
        content = json.loads(self.read_file(self.keys_path))
        content[index]['index'] = index
        self.w_file(json.dumps(content[index]), self.default)
        return content[index]

    def set_default_setting(self, default):
        self.w_file(json.dumps(default), self.default_setting_path)
        return

    def get_default_setting(self):
        content = self.read_file(self.default_setting_path)
        if(content):
            content = json.loads(content)
        else:
            content = {
                'apikey': '',
                'rpc_url': '',
                'network' : 'BSC',
                'exchange' : 'Pancake',
                'slippage_tolerance' : 20,
                'gas_multiple' : 1,
                'trans_fail_num' : 1,
                'gas_limit' : 6000000
            }
            self.w_file(json.dumps(content), self.default_setting_path)
        return content

    #读取文件
    def read_file(self, filepath):
        content = ''
        if Path(filepath).exists():
            with open(filepath) as fp:
                content=fp.read();
        return content

    #写入文件
    def w_file(self, content = '', filepath = ''):
        with open(filepath,'w') as wf:
            wf.write(content)

    def get_dirs(self, path):
        list_dir = []
        for file in os.listdir(path):
            file_path = os.path.join(path, file)
            if os.path.isdir(file_path):
                is_hide = self.file_is_hidden(file)
                if is_hide != True:
                    list_dir.append(file)
        # print(list_dir)
        # print(path)
        return list_dir

    # def get_network(self, path, name):
    #     self.read_file()
    #     return list_dir

    def file_is_hidden(self, path):
        if os.name == 'nt':
            attribute = win32api.GetFileAttributes(path)
            return attribute & (win32con.FILE_ATTRIBUTE_HIDDEN | win32con.FILE_ATTRIBUTE_SYSTEM)
        else:
            return path.startswith('.') #linux-osx

    def is_number(self, s):
        try:  # 如果能运行float(s)语句，返回True（字符串s是浮点数）
            float(s)
            return True
        except ValueError:  # ValueError为Python的一种标准异常，表示"传入无效的参数"
            pass  # 如果引发了ValueError这种异常，不做任何事情（pass：不做任何事情，一般用做占位语句）
        # try:
        #     import unicodedata  # 处理ASCii码的包
        #     unicodedata.numeric(s)  # 把一个表示数字的字符串转换为浮点数返回的函数
        #     return True
        # except (TypeError, ValueError):
        #     pass
        return False
# if __name__ == "__main__":
#     t = LocalStorage()
#     t.get_network(os.getcwd() + '/network/', 'BSC')