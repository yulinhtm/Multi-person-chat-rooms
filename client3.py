# -*- coding: utf-8 -*-
import wx
from socket import socket, AF_INET, SOCK_STREAM
import threading


class ClientFrame(wx.Frame):
    def __init__(self, client_name):
        super().__init__(None, id=1001, title=client_name + ' client page',
                         pos=wx.DefaultPosition, size=(400, 450))

        pl = wx.Panel(self)  # 创建面板
        box = wx.BoxSizer(wx.VERTICAL)  # 创建垂直布局管理器

        # 创建按钮
        conn_btn = wx.Button(pl, label='connect', size=(200, 40))
        dis_conn_btn = wx.Button(pl, label='stop', size=(200, 40))

        # 按钮布局
        fgz1 = wx.BoxSizer(wx.HORIZONTAL)
        fgz1.Add(conn_btn, 0, wx.ALL, 5)
        fgz1.Add(dis_conn_btn, 0, wx.ALL, 5)
        box.Add(fgz1, 0, wx.ALIGN_CENTER)

        # 显示信息的文本框
        self.show_text = wx.TextCtrl(pl, size=(400, 210),
                                     style=wx.TE_MULTILINE | wx.TE_READONLY)
        box.Add(self.show_text, 0, wx.ALL, 5)

        # 输入信息的文本框
        self.chat_text = wx.TextCtrl(pl, size=(400, 120),
                                     style=wx.TE_MULTILINE)
        box.Add(self.chat_text, 0, wx.ALL, 5)

        # 发送和重置按钮
        fgz2 = wx.BoxSizer(wx.HORIZONTAL)
        reset_btn = wx.Button(pl, label='reset', size=(200, 40))
        send_btn = wx.Button(pl, label='send', size=(200, 40))
        fgz2.Add(reset_btn, 0, wx.ALL, 5)
        fgz2.Add(send_btn, 0, wx.ALL, 5)
        box.Add(fgz2, 0, wx.ALIGN_CENTER)

        pl.SetSizer(box)  # 设置布局管理器

        '''绑定事件'''
        self.Bind(wx.EVT_BUTTON, self.on_connect, conn_btn)
        
        # 设置属性的设置   
        self.client_name=client_name
        self.is_connected = False # 存储连接状态，默认为未连接
        self.client_socket = None # 存储客户端 socket 对象
        # 给“发送”按钮绑定一个事件
        self.Bind(wx.EVT_BUTTON, self.send_to_serve, send_btn)

        #给“断开”按钮绑定一个事件

        self.Bind(wx.EVT_BUTTON, self.dis_conn_serve, dis_conn_btn)

        # ”重置“按钮
        self.Bind(wx.EVT_BUTTON, self.reset, reset_btn)

    def reset(self,event):
        self.chat_text.Clear() # 文本框内容没有

    def dis_conn_serve(self, event):
        if self.is_connected and self.client_socket:
            try:
                # 发送退出信号
                self.client_socket.send("__exit__".encode("utf-8"))
            except Exception as e:
                print(f"断开时出错: {e}")
            finally:
                # 本地也标记为断开，避免 recv_data 继续跑
                self.is_connected = False
                self.client_socket.close()
                self.client_socket = None
                wx.CallAfter(self.show_text.AppendText, "你已主动断开连接\n")

        


    
    
    
    
    
    
    
    def send_to_serve(self,event):
        # 判断连接状态
        if self.is_connected:
            # 从可写文本中获取
            input_data=self.chat_text.GetValue()
            if input_data != '':
                self.client_socket.send(input_data.encode('utf-8'))
                #发送数据后，清空文本框
                self.chat_text.SetValue('')

        
        



    def on_connect(self, event):   
        print(f'{self.client_name} try to connect to server...')
        # 这里可以添加实际的连接逻辑，例如创建 socket 并连接到服务器
        if not self.is_connected:
            self_host_port = ('localhost', 8888)
            self.client_socket = socket(AF_INET, SOCK_STREAM)
            # 连接服务器
            self.show_text.AppendText("已连接到服务器\n")
            # 更新连接状态
            self.client_socket.connect(self_host_port)
            self.client_socket.send(self.client_name.encode('utf-8'))
            
            # 启动一个线程,客户端的线程进行会话
            client_thread=threading.Thread(target=self.recv_data)
            # 设置为守护线程 # 主线程退出，子线程也退出
            client_thread.daemon = True
            # 更新连接状态
            self.is_connected = True
            # 启动线程
            client_thread.start()

    def recv_data(self):
        while self.is_connected:
            try:
                # 从服务器接收数据
                data = self.client_socket.recv(1024).decode('utf-8')
                if not data:  # 没有数据，服务器断开
                    self.is_connected = False
                    break

                # 如果收到退出信号，说明服务器确认断开
                if data.strip() == "__exit__":
                    wx.CallAfter(self.show_text.AppendText, "已断开服务器连接\n")
                    self.is_connected = False
                    break

                # 安全更新 GUI
                wx.CallAfter(
                    self.show_text.AppendText,
                    '-'*40 + '\n' + data + '\n'
                )
            except (ConnectionResetError, OSError):
                wx.CallAfter(self.show_text.AppendText, "连接已关闭\n")
                self.is_connected = False
                break
            
        

        
if __name__ == '__main__':
    app = wx.App()
    # 创建客户端名字
    name = input('Please input you user name:')
    # frame = ClientFrame('') # 这里可以填任何名字
    frame = ClientFrame(name)
    frame.Show()
    app.MainLoop()


    
    # lsof -i :8888  