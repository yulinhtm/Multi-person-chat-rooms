# -*- coding: utf-8 -*-
import wx
from socket import socket, AF_INET, SOCK_STREAM
import threading
import time

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

        # 保存聊天记录按钮
        self.Bind(wx.EVT_BUTTON, self.save_record, record_btn )

        # ‘断开’按钮
        self.Bind(wx.EVT_BUTTON, self.stop_server, stop_btn)


    def stop_server(self,event):
        print('The server is out of service')
        self.isOn = False



    def save_record(self,event):
        # 获取文本框内容
        record_data = self.show_text.GetValue()
        with open('record.log','w',encoding='utf-8') as file:
            file.write(record_data)
        
        




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

            self.show_info_and_send_client('system message', f'{user_name} is now online!',
                                           time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))

        #当self.isOn为False时，关闭服务器
        self.server_socket.close()
        self.show_text.AppendText("服务器已关闭...\n")
        print('server stop...')

    
    def show_info_and_send_client(self, data_source, data, datetime):
        # 字符串操作
        send_data = f'[{datetime}] {data_source} : {data}\n'
        # 在文本框显示
        self.show_text.AppendText(''*40 + '\n'+ send_data+ '\n')

        # 发送给所有在线用户
        for client in self.session_thread_dict.values():
            # 开始发送？
            if client.is_On:
                client.client_socket.send(send_data.encode('utf-8'))





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
            try:
                # 接收客户端消息 存储data中
                data = self.client_socket.recv(1024).decode('utf-8')
                # 如果客户端断开连接，data为空

                if not data or data == 'stop': # 客户端关闭或发送断开消息
                    print(f'{self.user_name} disconnected...')
                    self.is_On = False
                    self.server_frame.show_info_and_send_client('Notifications:',f'{self.user_name} leave the chat room',
                                                                time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
                
                else:
                    self.server_frame.show_info_and_send_client(self.user_name, data,
                                                                time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
            
            # 客户端异常断开
            except ConnectionResetError: 
                print(f'{self.user_name} disconnected abruptly')
                self.is_On = False
                break       
        
        # 关闭客户端 socket
        self.client_socket.close()
                



if __name__ == '__main__':
    app = wx.App()
    server = ServerFrame()
    server.Show()
    app.MainLoop()
