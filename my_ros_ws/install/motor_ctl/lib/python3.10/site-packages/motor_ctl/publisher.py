import rclpy
from rclpy.node import Node
import time
import socket
import json
import random
import select
import struct
from std_msgs.msg import String

class PicoListener:
    
    def __init__(self, HOST='0.0.0.0', PORT=8001):
        self.setup_socket_server(HOST, PORT)
        
        
    def setup_socket_server(self, host, port, max_waiting=5):
        self.listening_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listening_socket.bind((host, port))
        self.inputs= [self.listening_socket]
        self.outputs=[]
        self.listening_socket.listen(max_waiting)
        
        
    def listen_for_pico(self):
        while len(self.inputs) > 0 or len(self.outputs) > 0:
            readable, writable, exceptions= select.select(self.inputs, self.outputs, self.inputs)
            self.handle_input(readable)
            self.handle_output(writable)
            time.sleep(0.5)

    def handle_input(self, readable):
        for s in readable:
            try:
                if s==self.listening_socket:
                    pico_connection, pico_addr= s.accept()
                    self.inputs.append(pico_connection)
                    print("new connection")
                    self.outputs.append(pico_connection)
                else:
                    length_prefix = self.recv_all(s, 4)
                    msg_length = struct.unpack('>I', length_prefix)[0]
                    data= json.loads(self.recv_all(s, msg_length).decode())
                    # print(f"recieved data from {s.getpeername()[0]}:{data}")
                    pub.send_detected(value=data['us'])
                    pub.send_loading(value= data['button'])
            except BlockingIOError as e:
                print(f"socket {s.getpeername()} data unavailable. skipping")
            except OSError as e:
                self.shut_socket(s, readable=readable)

    def handle_output(self, writable):
        for s in writable:
            n=random.random()
            if n<0.75:
                try:
                    encoded_msg= 'LED'.encode()
                    message_length=len(encoded_msg)
                    length_prefix= struct.pack('>I', message_length)
                    s.sendall(length_prefix + encoded_msg)
                except BlockingIOError as e:
                    print(f"socket {s.getpeername()} data unavailable. skipping")
                except OSError as e:
                    self.shut_socket(s, writable=writable)
                    
                    
    def recv_all(self, sock, length):
        data=b''
        while len(data) < length:
            more=sock.recv(length-len(data))
            if not more:
                print("connection hung up")
                raise OSError("read is too short")
            data+=more
        return data
    
    def shutdown_sockets(self):
        print(f"shutting sockets")
        for s in self.inputs:
            s.close()
        for s in self.outputs:
            s.close()
            
    def shut_socket(self, s, readable=None, writable=None):
        s.close()
        if s in self.inputs:
            self.inputs.remove(s)
        if s in self.outputs:
            self.outputs.remove(s)
        if readable and s in readable:
            readable.remove(s)
        if writable and s in writable:
            writable.remove(s)






class MyPublisher(Node):
    '''
    An example publisher node
    '''
    def __init__(self):
        # call the Node constructor, pass it a name for your node
        super().__init__('motor_ctl_publisher')
        # create a publisher on a topic called 'chatter'
        self.detected_publisher = self.create_publisher(String, 'detected', 1)
        self.loading_publisher = self.create_publisher(String, 'loading', 1)
        self.message_counter = 0

    def send_detected(self, value):
        '''
        Generate a String message and publish it on the /chatter topic
        '''
        # create a string message
        msg = String()
        # set the data field
        #msg.data = f'This is message number {self.message_counter}'
        msg.data=f'{value}'
        # publish the message
        self.detected_publisher.publish(msg)
        # write a message to the logger describing what we sent
        self.get_logger().info(f"Publishing message {self.message_counter}")
        self.message_counter += 1
        
        
    def send_loading(self, value):
        '''
        Generate a String message and publish it on the /chatter topic
        '''
        # create a string message
        msg = String()
        # set the data field
        #msg.data = f'This is message number {self.message_counter}'
        msg.data=f'{value}'
        # publish the message
        self.loading_publisher.publish(msg)
        # write a message to the logger describing what we sent
        self.get_logger().info(f"Publishing message {self.message_counter}")
        self.message_counter += 1





def main():
        try:
            rclpy.init()
            pico=PicoListener()
            global pub
            pub = MyPublisher()
            while True:
                pico.listen_for_pico()
                #pub.send_detected()
                time.sleep(2)
        except KeyboardInterrupt:
            pub.destroy_node()
            rclpy.shutdown()
