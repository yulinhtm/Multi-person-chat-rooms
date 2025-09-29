# -*- coding: utf-8 -*-
import wx
from socket import socket, AF_INET, SOCK_STREAM
import threading

class ServerFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, id=1002, title='server page',
                         pos=wx.DefaultPosition, size=(400, 450))

        pl = wx.Panel(self)
        box = wx.BoxSizer(wx.VERTICAL)

        # 水平按钮布局
        fgz1 = wx.BoxSizer(wx.HORIZONTAL)

        start_server_btn = wx.Button(pl, label='start server', size=(133, 40))
        record_btn = wx.Button(pl, label='save chat history', size=(133, 40))
        stop_btn = wx.Button(pl, label='stop server', size=(133, 40))

        fgz1.Add(start_server_btn, 0, wx.ALL, 5)
        fgz1.Add(record_btn, 0, wx.ALL, 5)
        fgz1.Add(stop_btn, 0, wx.ALL, 5)

        box.Add(fgz1, 0, wx.ALIGN_CENTER)

        self.show_text = wx.TextCtrl(pl, size=(400, 410),
                                     style=wx.TE_MULTILINE | wx.TE_READONLY)
        box.Add(self.show_text, 1, wx.ALL, 5)

        pl.SetSizer(box)

        # 服务器属性
        self.isOn = False
        self.host_port = ('', 8888)
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.server_socket.bind(self.host_port)
        self.server_socket.listen(5)
        self.session_thread_dict = {}

        # 绑定事件
        self.Bind(wx.EVT_BUTTON, self.start_server, start_server_btn)

    # 事件处理函数必须在类里
    def start_server(self, event):
        self.show_text.AppendText("服务器已启动...\n")
        print('server start...')

        # 可以用线程去接受客户端连接，防止阻塞 GUI
        if not self.isOn:
            self.isOn = True
            main_thread=threading.Thread(target=self.do_work)
            
            #daemon=True  # 主线程退出，子线程也退出
            main_thread.daemon = True

            # 启动线程
            main_thread.start()

    def do_work(self):
        # 服务器主循环，接受客户端连接
        while self.isOn:
            # 接受客户端连接
            session_sock, client_addr = self.server_socket.accept()
            
            # 接受客户端用户名
            user_name = session_sock.recv(1024).decode('utf-8')
            #创建一个会话线程对象
            session_thread = SessionThread(session_sock, user_name, self)
            # 保存会话线程对象到字典
            self.session_thread_dict[user_name] = session_thread
            # 启动线程
            session_thread.start()

        #当self.isOn为False时，关闭服务器
        self.server_socket.close()
        self.show_text.AppendText("服务器已关闭...\n")
        print('server stop...')



class SessionThread(threading.Thread):
    def __init__(self, client_socket, user_name, server):
        # 调用父类的初始化方法
        threading.Thread.__init__(self)
        self.client_socket = client_socket
        self.user_name = user_name
        self.server_frame = server
        self.is_On = True # 控制线程运行的标志

        

    def run(self) -> None:
        print(f' {self.user_name} connected...')
        while self.is_On:
            # 接收客户端消息 存储data中
            data = self.client_socket.recv(1024).decode('utf-8')
            # 如果客户端断开连接，data为空
            if not data:  # 客户端断开或发送空消息
                print(f'{self.user_name} disconnected...')
                self.is_On = False
                self.client_socket.close()
                break



if __name__ == '__main__':
    app = wx.App()
    server = ServerFrame()
    server.Show()
    app.MainLoop()
