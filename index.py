#!/user/bin/env python
# coding=utf-8
import threading
from tkinter import *
from tkinter import ttk
from unicodedata import *
from PIL import Image, ImageTk 
from LocalStorage import *
from WebThree import *
from tkinter.messagebox import showinfo
import webbrowser
from Logger import *
from urllib.request import urlopen
import io

class Application(Frame):
    def __init__(self,master):
        super(Application, self).__init__(master)#Set __init__ to the master class
        self.grid()
        self.default_account= ''
        self.create_main()#Creates function
        self.import_key = True
        self.setting = True
        self.swaping = False
        self.import_contract = True
        self.init_balance()
        threading.Thread(name='read_log', target=self.read_log).start()
        
    def read_log(self):
        time.sleep(2)
        with open(Logger.logname) as f:
            f.seek(0,2)
            while True:
                # data = f.readlines()
                # 可以添加日志量的监控，如果line列表越长说明单位时间产生的日志越多
                for line in f.readlines(): 
                    if line != '\n':    #空行不处理
                        self.frame_swap_log_text['state'] = NORMAL
                        self.frame_swap_log_text.insert(0.0, line + '\r')
                        self.frame_swap_log_text['state'] = DISABLED
                time.sleep(0.1)

    def create_main(self):
        self.frame_ad = Frame(self, width=400, height=20)
        self.frame_ad.grid(row=0, column=0)
        self.frame_ad.grid_propagate(0)
        
        self.frame_account = Frame(self,  width=400, height=60, padx=80)
        self.frame_account.grid(row=1, column=0)
        self.frame_account.grid_propagate(0)

        self.account_balance = Label(self.frame_account, text='余额：', justify=LEFT, relief=FLAT, width=3, fg='grey')
        self.account_balance.grid(row=1, column=0)
        self.account_balance.grid_propagate(0)

        self.account_balance2 = Label(self.frame_account, text='0', justify='left', anchor='w', relief=FLAT, width=12, fg='red')
        self.account_balance2.grid(row=1, column=1, sticky='w')
        # self.account_balance.grid_propagate(0)

        self.label_import = Button(self.frame_account, text='设置', width=5, justify=RIGHT, height=1, command=self.setting)
        self.label_import.grid(row=1, column=2)

        self.account_list = ttk.Combobox(self.frame_account, width=15, justify=LEFT, textvariable=StringVar(), height=5, state="readonly")
        keys = self.get_private_keys()
        if keys:
            self.account_list['values'] = self.get_private_keys()
            self.account_list.current(self.get_default_account())
            self.account_list.bind("<<ComboboxSelected>>", self.set_default_account)
        self.account_list.grid(row=0, column=0, columnspan=2)      # 设置其在界面中出现的位置  column代表列   row 代表行

        self.label_import = Button(self.frame_account, text='私钥导入', width=5, justify=RIGHT, height=1, command=self.input_private_key)
        self.label_import.grid(row=0, column=2)

        self.frame_ad2 = Frame(self, bg='blue', width=400, height=100)
        self.frame_ad2.grid(row=2, column=0)
        self.frame_ad2.grid_propagate(0)

        # logo1 = Image.open(ad['img'])
        self.logo2 = ImageTk.PhotoImage(banner)
        self.label_ad2 = Label(self.frame_ad2, image=self.logo2, anchor='center', justify=CENTER)
        self.label_ad2.grid()
        self.label_ad2.config(cursor='hand1')
        self.label_ad2.grid_propagate(0)
        self.label_ad2.bind("<ButtonPress-1>", self.openFilemanager) 

        self.frame_ad3 = Frame(self, width=400, height=10)
        self.frame_ad3.grid(row=3, column=0)
        self.frame_ad3.grid_propagate(0)

        ### 交易列表
        self.frame_swap = Frame(self, width=350, height=220)
        self.frame_swap.grid(row=4, column=0)
        self.frame_swap.grid_propagate(0)

        self.frame_swap_1 = Frame(self.frame_swap, width=300, height=80, padx=50)
        self.frame_swap_1.grid(row=0, column=1)
        self.frame_swap_1.grid_propagate(0)

        self.frame_swap_2 = Frame(self.frame_swap, width=300, height=100, padx=50)
        self.frame_swap_2.grid(row=1, column=1)
        self.frame_swap_2.grid_propagate(0)

        self.frame_swap_3 = Frame(self.frame_swap, width=300, height=30, padx=100)
        self.frame_swap_3.grid(row=2, column=1)
        self.frame_swap_3.grid_propagate(0)

        #合约列表
        contracts = self.get_contracts()
        self.swap_contracts_list1_index = 0
        self.swap_contracts_list2_index = 2
        
        self.swap_contracts_list1 = ttk.Combobox(self.frame_swap_1, width=11, justify=LEFT, textvariable=StringVar(), height=30, state='readonly')
        self.swap_contracts_list1['values'] = contracts
        self.swap_contracts_list1.current(self.swap_contracts_list1_index)
        self.swap_contracts_list1.bind("<<ComboboxSelected>>", self.init_price1)
        self.swap_contracts_list1.grid(row=0, column=1)      # 设置其在界面中出现的位置  column代表列   row 代表行
        self.swap_contracts_list1.grid_propagate(0)

        self.swap_contracts_btn1 = Button(self.frame_swap_1, text='导入合约', width=5, justify=RIGHT, height=1, command=self.import_contract1)
        self.swap_contracts_btn1.grid(row=0, column=2)

        self.validate1 = self.register(self.input1_key)
        self.swap_contracts_input1_value = StringVar()
        self.swap_contracts_input1 = Entry(self.frame_swap_1, textvariable = self.swap_contracts_input1_value, borderwidth=1, width=22, validate='key', validatecommand=(self.validate1, '%P'), highlightthickness=0)
        self.swap_contracts_input1.grid(row=1, column=1, columnspan=2)

        self.swap_contracts_balance1 = Label(self.frame_swap_1, text='余额', justify='right', anchor='e', relief=FLAT, width=6, fg='grey',font=('宋体',11))
        self.swap_contracts_balance1.grid(row=2, column=2)
        self.swap_contracts_balance1.grid_propagate(0)
        
        self.swap_contracts_balance1_label_value = StringVar()
        self.swap_contracts_balance1_label = Label(self.frame_swap_1, textvariable=self.swap_contracts_balance1_label_value, justify='right', anchor='w', relief=FLAT, width=15, fg='grey',font=('宋体',11))
        self.swap_contracts_balance1_label.grid(row=2, column=1, sticky='w')
        self.swap_contracts_balance1_label.bind("<ButtonPress-1>", self.set_input1_by_balance) 
        self.swap_contracts_balance1_label.grid_propagate(0)
        self.swap_contracts_balance1_label_value.set('0')
        self.swap_contracts_balance1_label.config(cursor='hand1')

        #合约列表2
        self.swap_contracts_list2 = ttk.Combobox(self.frame_swap_2, width=11, justify=LEFT, textvariable=StringVar(), height=30, state="readonly")
        self.swap_contracts_list2['values'] = contracts
        self.swap_contracts_list2.current(self.swap_contracts_list2_index)
        self.swap_contracts_list2.bind("<<ComboboxSelected>>", self.init_price2)
        self.swap_contracts_list2.grid(row=0, column=1)      # 设置其在界面中出现的位置  column代表列   row 代表行
        self.swap_contracts_list2.grid_propagate(0)

        self.swap_contracts_btn2 = Button(self.frame_swap_2, text='导入合约', width=5, justify=RIGHT, height=1, command=self.import_contract2)
        self.swap_contracts_btn2.grid(row=0, column=2)

        self.validate2 = self.register(self.input2_key)
        self.swap_contracts_input2_value = StringVar()
        self.swap_contracts_input2 = Entry(self.frame_swap_2, textvariable = self.swap_contracts_input2_value, borderwidth=1, width=22, validate='key', validatecommand=(self.validate2, '%P'), highlightthickness=0)
        self.swap_contracts_input2.grid(row=1, column=1, columnspan=2)

        self.swap_contracts_balance2 = Label(self.frame_swap_2, text='余额', justify='right', anchor='e', relief=FLAT, width=6, fg='grey',font=('宋体',11))
        self.swap_contracts_balance2.grid(row=2, column=2)
        self.swap_contracts_balance2.grid_propagate(0)
        self.swap_contracts_balance2_label_value = StringVar()
        self.swap_contracts_balance2_label = Label(self.frame_swap_2, textvariable=self.swap_contracts_balance2_label_value, justify='right', anchor='w', relief=FLAT, width=15, fg='grey',font=('宋体',11))
        self.swap_contracts_balance2_label.grid(row=2, column=1, sticky='w')
        self.swap_contracts_balance2_label.grid_propagate(0)
        self.swap_contracts_balance2_label_value.set('0')

        self.swap_contracts_received = Label(self.frame_swap_2, text='最少获得', justify='right', anchor='e', relief=FLAT, width=6, fg='grey',font=('宋体',11))
        self.swap_contracts_received.grid(row=3, column=2)
        self.swap_contracts_received.grid_propagate(0)
        self.swap_contracts_received_label = Label(self.frame_swap_2, text='0', justify='right', anchor='w', relief=FLAT, width=15, fg='grey',font=('',11))
        self.swap_contracts_received_label.grid(row=3, column=1, sticky='w')
        self.swap_contracts_received_label.grid_propagate(0)

        #开始
        self.swap_contracts_btn = Button(self.frame_swap_3, text='开始', width=5, justify=RIGHT, height=1, command=self.swap, padx=20)
        self.swap_contracts_btn.grid(row=0, column=0)
        # self.swap_contracts_btn.grid_propagate(0)

        self.frame_swap_log = Frame(self, width=350, height=150)
        self.frame_swap_log.grid(row=5, column=0)
        self.frame_swap_log.grid_propagate(0)

        # wrap属性是指 自动换行。WORD表示单词换行；CHAR(default)表示字符换行;NONE 表示不自动换行
        self.frame_swap_log_text = Text(self.frame_swap_log, width=46, height=10, bg='#ececec', fg='grey', relief=RIDGE,state=DISABLED, highlightthickness=0)
        self.frame_swap_log_text.grid(row=0, column=0)
        self.frame_swap_log_text.grid_propagate(0)

    def set_input1_by_balance(self, event):
        addr_index = self.swap_contracts_list1.current()
        b1 = self.swap_contracts_balance1_label_value.get()
        balance = 0.00
        if b1:
            balance = decimal.Decimal(b1)

        if addr_index == 0:
            gas_price = decimal.Decimal(w3.gas_price())
            balance = balance - gas_price / 10 ** w3.network['decimals']

        if balance < 0:
            balance = 0.00


        # self.swap_contracts_input1_value = str(w3.num_format(balance))
        self.swap_contracts_input1_value.set(w3.num_format(balance))

        self.init_price(1)
        return

    def init_balance1(self):
        if self.default_account:
            addr_index = self.swap_contracts_list1.current()
            if addr_index == 0:
                balance = self.set_default_balance()
            else:
                contract = ls.get_addr_by_index(addr_index)
                balance = w3.balance_of(contract, self.default_account)
            self.swap_contracts_balance1_label_value.set(str(balance))
        

    def init_balance2(self):
        if self.default_account:
            addr_index = self.swap_contracts_list2.current()
            if addr_index == 0:
                balance = self.set_default_balance()
            else:
                contract = ls.get_addr_by_index(addr_index)
                balance = w3.balance_of(contract, self.default_account)
            self.swap_contracts_balance2_label_value.set(str(balance))

    def init_balance(self):
        if self.default_account:
            self.init_balance1()
            self.init_balance2()

    def swapping(self):
        addr1_index = self.swap_contracts_list1.current()
        addr2_index = self.swap_contracts_list2.current()
        amount = self.swap_contracts_input1.get()
        addrs = ls.get_addr_by_indexs(addr1_index, addr2_index)
        threading.Thread(name='read_log', target=self.read_log).start()
        res = w3.swap(addrs[0], addrs[1], amount, default_setting_info['slippage_tolerance'], default_setting_info['trans_fail_num'])
        self.swaping = False
        self.swap_contracts_btn.config(text='开始')
        if res == 1:
            self.init_balance()
            showinfo(title='交易结果', message='交易成功')
        elif res == 3:
            showinfo(title='交易结果', message='授权失败')
        else:
            showinfo(title='交易结果', message='交易失败')
        return res

    def swap(self):
        amount_in = self.swap_contracts_input1.get()
        if amount_in == 0 or amount_in == '':
            return 
        if self.swaping == True:
            showinfo(title='交易', message='交易进行中，请稍等')
            return False
        self.swaping = True
        self.swap_contracts_btn.config(text='交易中')
        t = threading.Thread(name='swap', target=self.swapping).start()
        # print(t)
        return

    def openFilemanager(self, event):  
        webbrowser.open(ad['url'], new=0)

    def init_price1(self, t):
        self.init_balance1()
        if self.swap_contracts_list2_index == self.swap_contracts_list1.current():
            self.swap_contracts_list2.current(self.swap_contracts_list1_index)
            self.swap_contracts_list2_index = self.swap_contracts_list1_index
            self.swap_contracts_list1_index = self.swap_contracts_list1.current()
            self.init_balance2()
            c_amount = self.swap_contracts_input1.get()
            if c_amount != '0' and c_amount != '':
                self.swap_contracts_input1.delete(0, END)
                self.swap_contracts_input1.insert(0, self.swap_contracts_input2.get())
                self.swap_contracts_input2.delete(0, END)
                self.swap_contracts_input2.insert(0, c_amount)
            return
        self.swap_contracts_list1_index = self.swap_contracts_list1.current()
        self.init_price(1)
        return True

    def init_price2(self, t):
        self.init_balance2()
        if self.swap_contracts_list1_index == self.swap_contracts_list2.current():
            self.swap_contracts_list1.current(self.swap_contracts_list2_index)
            self.swap_contracts_list1_index = self.swap_contracts_list2_index
            self.swap_contracts_list2_index = self.swap_contracts_list2.current()
            self.init_balance1()
            c_amount = self.swap_contracts_input1.get()
            if c_amount != '0' and c_amount != '':
                self.swap_contracts_input1.delete(0, END)
                self.swap_contracts_input1.insert(0, self.swap_contracts_input2.get())
                self.swap_contracts_input2.delete(0, END)
                self.swap_contracts_input2.insert(0, c_amount)
            return
        self.swap_contracts_list2_index = self.swap_contracts_list2.current()
        self.init_price(1)
        return

    #购买 通过eth 获取价格
    def buy_price_by_eth(self, pair, input):
        return (pair[0]) / pair[1]

    #购买 通过token 获取价格
    def buy_price_by_token(self, pair, input):
        return (pair[0]) / (pair[1])

    #卖出 通过eth 获取价格
    def sell_price_by_eth(self, pair, input):
        return (pair[0]) / pair[1]

    #卖出 通过token 获取价格
    def sell_price_by_token(self, pair, input):
        return (pair[0]) / (pair[1])
    
    #获取价格
    def init_price(self, t):
        addr1_index = self.swap_contracts_list1.current()
        addr2_index = self.swap_contracts_list2.current()
        if t==1:
            input = self.swap_contracts_input1.get()
        else:
            input = self.swap_contracts_input2.get()

        if input == '' or input == '0' or input == 0:
            self.swap_contracts_input1.delete(0, END)
            self.swap_contracts_input2.delete(0, END)
            return 0

        amount = decimal.Decimal(input)
        if amount <= 0:
            return 0

        if addr1_index == 0 and addr2_index == 1: # bnb -> wbnb
            get_amount = amount
            if t == 1:
                self.swap_contracts_input2.delete(0, END)
                self.swap_contracts_input2.insert(0, w3.num_format(amount))
            else:
                self.swap_contracts_input1.delete(0, END)
                self.swap_contracts_input1.insert(0, w3.num_format(amount))
        elif addr1_index == 1 and addr2_index == 0: # wbnb -> bnb
            get_amount = amount
            if t == 1:
                self.swap_contracts_input2.delete(0, END)
                self.swap_contracts_input2.insert(0, w3.num_format(amount))
            else:
                self.swap_contracts_input1.delete(0, END)
                self.swap_contracts_input1.insert(0, w3.num_format(amount))
        elif addr1_index in [1, 0]: # 基础币购买 bnb -> token
            addr2 = ls.get_addr_by_index(addr2_index)
            contract_info = w3._contract_info(addr2)
            pair = w3.get_pair_num(contract_info)
            if t == 1:
                price = self.buy_price_by_eth(pair, amount)
                get_amount = amount / price
                self.swap_contracts_input2.delete(0, END)
                self.swap_contracts_input2.insert(0, w3.num_format(get_amount))
            else:
                price = self.buy_price_by_token(pair, amount)
                # print(price)
                need_eth = w3.num_format(amount * price)
                get_amount = amount
                self.swap_contracts_input1.delete(0, END)
                self.swap_contracts_input1.insert(0, need_eth)

        elif addr2_index in [1, 0]: # 卖出为基础币 token -> bnb
            addr1 = ls.get_addr_by_index(addr1_index)
            contract_info = w3._contract_info(addr1)
            pair = w3.get_pair_num(contract_info)
            if t== 1:
                price = self.sell_price_by_token(pair, amount)
                get_amount = (amount * price)
                self.swap_contracts_input2.delete(0, END)
                self.swap_contracts_input2.insert(0, w3.num_format(get_amount))
            else:
                price = self.sell_price_by_eth(pair, amount)
                need_eth = w3.num_format(amount / price)
                get_amount = (amount)
                self.swap_contracts_input1.delete(0, END)
                self.swap_contracts_input1.insert(0, str(need_eth))
        else: #兑换
            if t == 1:
                self.swap_contracts_input2.delete(0, END)
            else:
                self.swap_contracts_input1.delete(0, END)
            showinfo(title='提示', message='当前只支持使用 BNB 兑换')
            return

        slippage_tolerance = decimal.Decimal(default_setting_info['slippage_tolerance']) / 100
        min_amount = w3.num_format(get_amount - get_amount * (slippage_tolerance))
        self.swap_contracts_received_label.config(text=min_amount)
        return

    def calc_price_thread(self, name, task, arg1):
        return threading.Thread(name=name, target=task, args=(arg1,)).start()

    def input1_key(self, input):
        if self.swap_contracts_input1.focus_displayof() != self.swap_contracts_input1:
            return True
        if input == '' or input == '0':
            return True
        if ls.is_number(input):
            self.calc_price_thread(input, self.input1_handle, input)
            return True
        else:
            return False

    def input1_handle(self, input):
        self.init_price(1)

    def input2_key(self, input):
        if self.swap_contracts_input2.focus_displayof() != self.swap_contracts_input2:
            return True
        if input == '' or input == '0':
            return True
        if ls.is_number(input):
            self.calc_price_thread(input, self.input2_handle, input)
            return True
        else:
            return False

    def input2_handle(self, input):
        self.init_price(2)

    def import_contract1(self):
        if self.import_contract == True:
            self.import_contract = False
            input_diaglog = ImportContract()
            self.master.wait_window(input_diaglog)
            self.import_contract_finished(1, input_diaglog.contract_info['index'])
            self.calc_price_thread('init_price1', self.init_price1, 1)
        return

    def import_contract2(self):
        if self.import_contract == True:
            self.import_contract = False
            input_diaglog = ImportContract()
            self.master.wait_window(input_diaglog)

            self.import_contract_finished(2, input_diaglog.contract_info['index'])
            # self.init_price2(2)
            self.calc_price_thread('init_price2', self.init_price2, 2)
        return

    def import_contract_finished(self, t, index):
        contracts = self.get_contracts()
        self.swap_contracts_list1['values'] = contracts
        self.swap_contracts_list2['values'] = contracts
        self.swap_contracts_input1_value.set('0.0')
        self.swap_contracts_input2_value.set('0.0')
        
        if t == 1:
            self.swap_contracts_list1_index = index
            self.swap_contracts_list1.current(self.swap_contracts_list1_index)
            self.init_balance1()
        else:
            self.swap_contracts_list2_index = index
            self.swap_contracts_list2.current(self.swap_contracts_list2_index)
            self.init_balance2()        
        
        self.import_contract = True
        return

    def input_private_key(self):
        if self.import_key == True:
            self.import_key = False
            input_diaglog = ImportKey()
            self.master.wait_window(input_diaglog)
            self.keys_list = input_diaglog.keys_list
            Logger.info('导入钱包')
            threading.Thread(name='init_account_show', target=self.init_account_show).start()
        return

    #设置完 私钥 后需要初始化账户 及 余额
    def init_account_show(self):
        self.import_key = True
        Logger.info('初始化地址列表')
        if self.keys_list:
            self.account_list['values'] = self.keys_list['list']
            self.account_list.current(self.keys_list['index'])
            self.account_list.bind("<<ComboboxSelected>>", self.set_default_account)
        Logger.info('初始化余额')
        self.set_default_account('1')
        Logger.info('钱包导入成功')

    def setting(self):
        if self.setting == True:
            self.setting = False
            input_diaglog = Setting()
            self.master.wait_window(input_diaglog)
            Logger.info('开启设置')
            self.setting = True
            threading.Thread(name='setting_finished', target=self.setting_finished).start()
        return

    #设置完 参数 后需要初始化合约列表 及 余额
    def setting_finished(self):
        Logger.info('设置完成，重置合约')
        contracts = self.get_contracts()
        self.swap_contracts_list1_index = 0
        self.swap_contracts_list2_index = 2

        self.swap_contracts_list1['values'] = contracts
        self.swap_contracts_list1.current(self.swap_contracts_list1_index)
        self.swap_contracts_input1_value.set('0.0')
        self.swap_contracts_list2['values'] = contracts
        self.swap_contracts_list2.current(self.swap_contracts_list2_index)
        self.swap_contracts_input2_value.set('0.0')
        Logger.info('设置完成，重置余额')
        self.set_default_balance()
        self.init_balance()
        Logger.info('设置完成')

    def get_private_keys(self):
        return ls.get_private_keys()

    def get_default_account(self):
        default = ls.get_default_account()
        index = 0
        if default:
            index = default['index']
            w3._init_user(default['account'], default['private_key'])
            self.default_account = default['account']
            self.set_default_balance()
        return index
    
    def set_default_balance(self):
        if self.default_account:
            b = w3.balance(self.default_account)
            self.account_balance2.config(text=b)
            return b
        Logger.info('没有默认账户')
        return 0

    def get_contracts(self):
        return ls.get_contarct_list(w3.network_name)
        
    def set_default_account(self, evnent):
        current = self.account_list.current()
        default = ls.set_default_account(current)
        w3._init_user(default['account'], default['private_key'])
        self.default_account = default['account']
        self.set_default_balance()
        self.init_balance()
        return


class ImportKey(Toplevel):
    def __init__(self):
        Toplevel.__init__(self)
        self.title('私钥导入')
        
        #得到屏幕高度
        w = 450
        h = 150
        #窗口宽高为
        x = (sw-w) / 2
        y = (sh-h) / 2
        self.geometry("%dx%d+%d+%d" %(w,h,x,y))
        self.maxsize(w,h)
        self.minsize(w,h)
        
        # 弹窗界面
        self.setup_UI()
        self.is_ok = False
        self.keys_list = []

    def setup_UI(self):
        self.frame_empty = Frame(self,  width=50, height=100)
        self.frame_empty.grid(row=0, column=0)

        self.frame_label = Frame(self, width=50, height=100)
        self.frame_label.grid(row=0, column=1)
        self.label_key = Label(self.frame_label, text='秘钥', anchor=E)
        self.label_key.grid(row=0, column=1)

        self.frame_input = Frame(self,  width=300, height=100)
        self.frame_input.grid(row=0, column=2)
        self.text_key = Text(self.frame_input, width=40, height=5, highlightthickness=0)
        self.text_key.grid(row=0, column=0)

        self.frame_button = Frame(self,  width=300, height=50)
        self.frame_button.grid(row=1, column=2)
        self.button_ok = Button(self.frame_button, text='导入', width=5, justify=LEFT, height=1, command=self.ok)
        self.button_ok.grid(row=0, column=0)

    def ok(self):
        key = self.text_key.get(1.0,END).strip().replace("\n","").replace("\t","")  # 设置数据
        if key:
            account = w3.get_account_by_key(key)
            if account:
                self.keys_list = ls.set_account(account)
                self.destroy()
                return
        showinfo(title='导入私钥', message='导入失败，请检查私钥是否正确')

    def cancel(self):
        self.destroy()

class ImportContract(Toplevel):
    def __init__(self):
        Toplevel.__init__(self)
        self.title('合约导入')
        
        #得到屏幕高度
        w = 450
        h = 150
        #窗口宽高为
        x = (sw-w) / 2
        y = (sh-h) / 2
        self.geometry("%dx%d+%d+%d" %(w,h,x,y))
        self.maxsize(w,h)
        self.minsize(w,h)
        
        # 弹窗界面
        self.setup_UI()
        self.is_ok = False
        self.contract_info = []

    def setup_UI(self):
        self.frame_empty = Frame(self,  width=50, height=100)
        self.frame_empty.grid(row=0, column=0)

        self.frame_label = Frame(self, width=50, height=100)
        self.frame_label.grid(row=0, column=1)
        self.label_key = Label(self.frame_label, text='合约地址', anchor=E)
        self.label_key.grid(row=0, column=1)

        self.frame_input = Frame(self,  width=300, height=100)
        self.frame_input.grid(row=0, column=2)
        self.text_contract = Text(self.frame_input, width=40, height=5, highlightthickness=0)
        self.text_contract.grid(row=0, column=0)

        self.frame_button = Frame(self,  width=300, height=50)
        self.frame_button.grid(row=1, column=2)
        self.button_ok = Button(self.frame_button, text='导入', width=5, justify=LEFT, height=1, command=self.ok)
        self.button_ok.grid(row=0, column=0)

    def ok(self):
        address = self.text_contract.get(1.0,END).strip().replace("\n","").replace("\t","")  # 设置数据
        address = w3.w3.toChecksumAddress(address)
        if address:
            self.contract_info = w3.import_contract(address)
            if self.contract_info:
                self.destroy()
                return
        showinfo(title='导入合约', message='导入失败，请检查合约地址是否正确')

    def cancel(self):
        self.destroy()


class Setting(Toplevel):
    def __init__(self):
        Toplevel.__init__(self)
        self.title('设置')
        
        #得到屏幕高度
        w = 350
        h = 400
        #窗口宽高为
        x = (sw-w) / 2
        y = (sh-h) / 2
        self.geometry("%dx%d+%d+%d" %(w,h,x,y))
        self.maxsize(w,h)
        self.minsize(w,h)
        # 弹窗界面
        self.setup_UI()
        self.is_ok = False
        # print(w3.network)

    def setup_UI(self):
        self.frame_setting_left = Frame(self,  width=20, height=500)
        self.frame_setting_left.grid(row=0, column=0)
        self.frame_setting_left.grid_propagate(0)
        self.frame_setting_center = Frame(self, width=300, height=500)
        self.frame_setting_center.grid(row=0, column=1)
        self.frame_setting_center.grid_propagate(0)

        self.frame_setting_center_1 = Frame(self.frame_setting_center, width=300, height=70)
        self.frame_setting_center_1.grid(row=0, column=1)
        # self.frame_setting_center_1.grid_propagate(0)

        self.frame_setting_center_2 = Frame(self.frame_setting_center, width=300, height=50)
        self.frame_setting_center_2.grid(row=1, column=1)

        self.frame_setting_center_3 = Frame(self.frame_setting_center, width=300, height=50)
        self.frame_setting_center_3.grid(row=2, column=1)
        self.frame_setting_center_4 = Frame(self.frame_setting_center, width=300, height=50)
        self.frame_setting_center_4.grid(row=3, column=1)
        self.frame_setting_center_5 = Frame(self.frame_setting_center, width=300, height=50)
        self.frame_setting_center_5.grid(row=4, column=1)
        self.frame_setting_center_6 = Frame(self.frame_setting_center, width=300, height=50)
        self.frame_setting_center_6.grid(row=5, column=1)
        # self.frame_setting_center_2.grid_propagate(0)
        # self.frame_setting_center_3.grid_propagate(0)
        # self.frame_setting_center_4.grid_propagate(0)
        # self.frame_setting_center_5.grid_propagate(0)
        # self.frame_setting_center_6.grid_propagate(0)

        #网络选择
        self.setting_network = Label(self.frame_setting_center_1, text='切换网络', width=10, padx=10, pady=10)
        self.setting_network.grid(row=1, column=0)
        self.network_list = ttk.Combobox(self.frame_setting_center_1, width=10, justify=LEFT, textvariable=StringVar(), height=2, state="readonly")
        self.network_list['values'] = self.get_network_list()
        self.network_list.current(self.get_default_network())
        self.network_list.bind("<<ComboboxSelected>>", self.get_network)
        self.network_list.grid(row=1, column=1)      # 设置其在界面中出现的位置  column代表列   row 代表行

        # rpc
        self.setting_rpcurl = Label(self.frame_setting_center_1, text='节点', width=10, padx=10, pady=10)
        self.setting_rpcurl.grid(row=2, column=0)
        self.setting_rpcurl_entry = Entry(self.frame_setting_center_1, width=12, justify=LEFT, textvariable=StringVar(), highlightthickness=0)
        self.setting_rpcurl_entry.insert(2, w3.network['rpc_url'])
        self.setting_rpcurl_entry.grid(row=2, column=1)

        #APIKEY
        self.setting_apikey = Label(self.frame_setting_center_2, text='APIKey', width=10, padx=10, pady=10)
        self.setting_apikey.grid(row=1, column=0)
        self.setting_apikey_entry = Entry(self.frame_setting_center_2, width=12, justify=LEFT, textvariable=StringVar(), highlightthickness=0)
        self.setting_apikey_entry.insert(0, w3.network['apikey'])
        self.setting_apikey_entry.grid(row=1, column=1)

        #交易所选择
        self.setting_exchannge_label = Label(self.frame_setting_center_2, text='交易所', width=10, padx=10, pady=10)
        self.setting_exchannge_label.grid(row=2, column=0)
        self.setting_exchannge_list = ttk.Combobox(self.frame_setting_center_2, width=10, justify=LEFT, textvariable=StringVar(), height=10, state="readonly")
        self.setting_exchannge_list['values'] = ['Pancake']
        self.setting_exchannge_list.current(0)
        self.setting_exchannge_list.grid(row=2, column=1)      # 设置其在界面中出现的位置  column代表列   row 代表行

        #滑点
        self.setting_exchannge_slippage_tolerance_label = Label(self.frame_setting_center_3, text='滑点', width=10, padx=10, pady=10)
        self.setting_exchannge_slippage_tolerance_label.grid(row=0, column=0)

        self.setting_exchannge_slippage_tolerance_scale = Scale(self.frame_setting_center_3, variable = DoubleVar(), from_=1, to=100, orient=HORIZONTAL, borderwidth=0,sliderlength=15, sliderrelief=RIDGE, width=10)
        self.setting_exchannge_slippage_tolerance_scale.set(default_setting_info['slippage_tolerance'])
        self.setting_exchannge_slippage_tolerance_scale.grid(row=0, column=1)

        #gas倍数
        self.setting_exchannge_gas_price_label = Label(self.frame_setting_center_4, text='GAS倍数', width=10, justify=LEFT, anchor='w', padx=10, pady=10)
        self.setting_exchannge_gas_price_label.grid(row=0, column=0)

        self.setting_exchannge_gas_price_scale = Scale(self.frame_setting_center_4, variable = DoubleVar(), from_=1, to=10, orient=HORIZONTAL, borderwidth=1,sliderlength=15, sliderrelief=RIDGE, width=10)
        self.setting_exchannge_gas_price_scale.set(default_setting_info['gas_multiple'])
        self.setting_exchannge_gas_price_scale.grid(row=0, column=1)

        #gas上限
        self.setting_exchannge_gas_limit_label = Label(self.frame_setting_center_4, text='GAS上限', width=10, justify=LEFT, anchor='w', padx=10, pady=10)
        self.setting_exchannge_gas_limit_label.grid(row=1, column=0)
        self.setting_exchannge_gas_limit_entry = Entry(self.frame_setting_center_4, width=12, justify=LEFT, textvariable=StringVar(), highlightthickness=0)
        self.setting_exchannge_gas_limit_entry.insert(0, default_setting_info['gas_limit'])
        self.setting_exchannge_gas_limit_entry.grid(row=1, column=1)


        #重试次数
        self.setting_exchannge_trans_fail_num_label = Label(self.frame_setting_center_5, text='重试次数', width=10, justify=LEFT, anchor='w', padx=10, pady=10)
        self.setting_exchannge_trans_fail_num_label.grid(row=0, column=0)

        self.setting_exchannge_trans_fail_num_scale = Scale(self.frame_setting_center_5, variable = DoubleVar(), from_=1, to=10, orient=HORIZONTAL, borderwidth=1,sliderlength=15, sliderrelief=RIDGE, width=10)
        self.setting_exchannge_trans_fail_num_scale.set(default_setting_info['trans_fail_num'])
        self.setting_exchannge_trans_fail_num_scale.grid(row=0, column=1)

        #保存
        self.setting_exchannge_confirm_btn =  Button(self.frame_setting_center_6, text='保存', width=5, justify=RIGHT, height=1, command=self.confirm)
        self.setting_exchannge_confirm_btn.grid(row=0, column=1)

    def get_network(self, t):
        current = self.network_list.get()
        network = w3.get_network_info(current)
        self.setting_apikey_entry.delete(0, END)
        self.setting_apikey_entry.insert(0, network['apikey'])
        self.setting_rpcurl_entry.delete(0, END)
        self.setting_rpcurl_entry.insert(0, network['rpc_url'])
        return

    def confirm(self):
        global default_setting_info
        default = {
            'apikey': self.setting_apikey_entry.get(),
            'rpc_url': self.setting_rpcurl_entry.get(),
            'network' : self.network_list.get(),
            'gas_limit': self.setting_exchannge_gas_limit_entry.get(),
            'exchange' : self.setting_exchannge_list.get(),
            'slippage_tolerance' : self.setting_exchannge_slippage_tolerance_scale.get(),
            'gas_multiple' : self.setting_exchannge_gas_price_scale.get(),
            'trans_fail_num' : self.setting_exchannge_trans_fail_num_scale.get(),
        }
        ls.set_default_setting(default)
        w3._init_network(default['network'], default['apikey'], default['rpc_url'])
        w3._init_exchange(default['network'], default['exchange'])
        default_setting_info = default
        self.destroy()
        return
    
    def get_network_list(self):
        name = []
        self.network_default_index = 0
        for item in network_list:
            if item['name'] == default_setting_info['network']:
                self.network_default_index = item['index']
            name.append(item['name'])
        return name

    def get_default_network(self):
        return self.network_default_index

    def cancel(self):
        self.destroy()

if __name__ == '__main__':
    ls = LocalStorage()
    w3 = WebThree()
    network_list = ls.get_content_by_file(w3.network_file)
    default_setting_info = ls.get_default_setting()
    w3._init_network(default_setting_info['network'])
    default_setting_info['rpc_url'] = w3.network['rpc_url']
    default_setting_info['apikey'] = w3.network['apikey']
    version = '1.0.0'

    w3._init_exchange(default_setting_info['network'], default_setting_info['exchange'])
    
    res = w3.get_ad()

    if res:
        ad = res['result']
        image_bytes = urlopen(ad['banner']).read()
        data_stream = io.BytesIO(image_bytes)
        banner = Image.open(data_stream)
    else:
        ad = {
            'url' : 'https://t.me/PureLandRobot',
            'banner' : ls.base_path + '/imgs/ad.png',
            'name' : 'Pure Land 1.0.0',
            'version':'1.0.0',
            'icon':ls.base_path + 'favicon.ico',
            'upgrade':'1'
        }
        banner = Image.open(ad['banner'])
    
    if ad['upgrade'] == '1' and ad['version'] != version:
        exit()
        
    #Main
    root = Tk()
    root.title(ad['name'])
    
    sw = root.winfo_screenwidth()
    #得到屏幕宽度
    sh = root.winfo_screenheight()
    #得到屏幕高度
    ww = 400
    wh = 600
       
    #窗口宽高为
    x = (sw-ww) / 2
    y = (sh-wh) / 2
    root.geometry("%dx%d+%d+%d" %(ww,wh,x,y))
    
    root.maxsize(ww,wh)
    root.minsize(ww,wh)

    logo1 = ls.base_path + 'favicon.ico'
    root.iconbitmap(logo1)
    app = Application(root)#The frame is inside the widgit
    root.mainloop()#Keeps the window open/running