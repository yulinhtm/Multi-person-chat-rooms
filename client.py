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
      pass
            
        
            

if __name__ == '__main__':
    app = wx.App()
    frame = ClientFrame('Python')
    frame.Show()
    app.MainLoop()
