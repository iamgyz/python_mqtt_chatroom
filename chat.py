import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
import curses #for drawing

class mqtt_chat:
    def __init__(self,host,port,topic,nick_name,curse):
        self.host = host
        self.port = int(port)
        self.topic = topic
        self.nick_name = nick_name
        self.curse = curse
        '''loop_start()/loop_stop'''
        #print("init..")
        self.subscribe_msg()
    def subscribe_msg(self):
        self.subscriber = mqtt.Client()
        self.subscriber.on_connect = self.on_connect
        self.subscriber.on_message = self.on_message
        self.is_connect = False #using this variable to wait for connect ready
        self.subscriber.connect(self.host,self.port);#keep_alive=60 
        self.subscriber.loop_start()
        while self.is_connect == False:
            pass#donothig...
    def send_msg(self,msg):
        msg = "["+self.nick_name + "] : "+msg
        publish.single(self.topic,msg, hostname=self.host, port=self.port)
    def on_connect(self,client, userdata, flags, rc):
        #print("Connected with result code "+str(rc))
        self.is_connect = True
        client.subscribe(self.topic);
        self.send_msg(self.nick_name+" is join the discussion\n")
    def on_message(self,client,user_data,msg):        
        self.curse.draw_received_msg(msg.payload.decode('utf-8'))
        #pass#print(msg.topic+" "+str(msg.payload))

class my_curses:
    def __init__(self):
        self.stdscr = curses.initscr()
        self.show_row = self.show_col = 0 #紀錄目前的row col
        self.input_col = 0 #紀錄目前user打的字到第幾個cursor
        (self.max_row,self.max_col) = self.stdscr.getmaxyx()#取得目前terminal的mac col/row
        #curses.noecho()
        curses.cbreak()
    def draw_text(self,row,col,msg):
        #clear first
        self.stdscr.addstr(row,col,' '*(self.max_col-1))
        self.stdscr.addstr(row,col,msg)
        self.stdscr.refresh()
    def get_input(self):
        user_input = ''
        while True:
            c = self.stdscr.get_wch()#從python3後 用這個解決編碼問題
            if c == '\n':#Enter Key
                self.input_col=2 #>>
                break
            elif c == curses.KEY_BACKSPACE:
                print('!')
                pass
            else:
                user_input+=str(c)
            self.input_col+=1
        return user_input
    def draw_start_window(self):
        self.stdscr.clear()
        self.draw_text(1,0,"#"*(self.max_col-1))
        self.draw_text(2,0,"A simple Chat Room using MQTT protocol")
        self.draw_text(3,0,"Author : Gyzheng, guanggyz@gmail.com")
        self.draw_text(4,0,"#"*(self.max_col-1))
    def draw_main_window(self):
        self.stdscr.clear()
        self.draw_text(1,0,"A simple Chat System using MQTT Protocol");
        self.draw_text(3,0,"#"*(self.max_col-1))
        row = self.max_row-2;
        self.draw_text(row,0,"-"*(self.max_col-1))
        self.draw_user_input_area()
        #init show_row/show_col
        self.show_row = 3
    def draw_user_input_area(self):
        self.draw_text(self.max_row-1,0,' '*(self.max_col-1))
        self.draw_text(self.max_row-1,0,">>")
    def draw_received_msg(self,msg):
        self.show_row+=1
        if self.show_row == self.max_row-2:
            #全部往上
            '''
            for y in range(5,self.max_row-2):
                for x in range(0,self.max_col-1):
                    tmp=''
                    tmp+=self.stdscr.getkey(y,x)
                #self.draw_text(y-1,0,tmp)
            self.show_row = self.max_row-3 
            '''
            self.show_row = 4   
        self.draw_text(self.show_row,0,msg)
        #將curse跳回user input
        self.stdscr.move(self.max_row-1,self.input_col)
        self.stdscr.refresh()

if __name__ == "__main__":
    #initilize mt_curses
    curse = my_curses()
    curse.draw_start_window()
    #get nick name & topic
    curse.draw_text(5, 0, 'Enter your nick name:\n')#y,x
    nick_name = curse.get_input()
    curse.draw_text(7, 0, 'Enter the topic, the people with sample topic will discuss together!\n')
    topic = curse.get_input()
    #initilize mqtt_chat
    chat = mqtt_chat("iot.eclipse.org","1883",str(topic),str(nick_name),curse);
    curse.draw_main_window()
    #entering while loop
    while True:
        msg = curse.get_input()
        curse.draw_user_input_area()
        chat.send_msg(msg)
