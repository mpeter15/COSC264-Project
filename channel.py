import argparse
import socket  # for sockets
import select  # for listening nicely on sockets
from random import random  # for uniform
from packet_class import *

PTYPE_DATA = 0
PTYPE_ACK = 1

MAGICNO = 0x497E
MAX_READ_SIZE = 512  # bytes
TIMEOUT = 1  # 1 second
PATH = './file.txt'
IP = '127.0.0.1'



class Channel:
    """Channel Program"""
    def __init__(self, c_sin, c_sout, c_rout, c_rin, sin, rin, p_rate):
        self.c_sin = c_sin
        self.c_sout = c_sout
        self.c_rout = c_rout
        self.c_rin = c_rin
        self.sin = sin
        self.rin = rin
        self.p_rate = p_rate
        self.socket_sin = self.create_socket(self.c_sin)
        self.socket_sout = self.create_socket(self.c_sout)
        self.socket_rin = self.create_socket(self.c_rin)
        self.socket_rout = self.create_socket(self.c_rout)
        self.check_port()

    def create_socket(self, port):
        #  socket creation
        new_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        new_socket.bind((IP, port))
        if port == self.c_rin or port == self.c_sin:
            new_socket.settimeout(.5)
        print("Socket Created")
        return new_socket

    def connect_socket(self):
        self.socket_sout.connect((IP, self.sin))
        self.socket_rout.connect((IP, self.rin))
        print("Sockets Connected")

    def send_to(self):
        self.connect_socket()
        while True:
            print("select")
            socket_read, _, _ = select.select([self.socket_sin,
                                               self.socket_rin], [], [])
            print("Socket read")
            for sock in socket_read:
                if not sock.check_magicno():
                    #  if the socket does not have MAGICNO correct get next
                    continue
                received = Channel.rec_packet(sock)
                #  random_var = random()
                #  if random_var < self.p_rate:
                #  continue
                if sock is self.socket_sin:
                    Channel.send_packet(self.socket_sin, received)
                elif sock is self.socket_rin:
                    Channel.send_packet(self.socket_rin, received)

    @staticmethod
    def send_packet(socket1, received):
        try:
            # packet is sent on crout to rin
            received = received.serialize()
            socket1.send(received)
        except:
            print("Connection Failed")

    @staticmethod
    def rec_packet(socket1):
        try:
            received_bytes = socket1.recv(MAX_READ_SIZE)
            received = Packet.deserialize(received_bytes)
            print("Successfully Received")
            return received
        except:
            print("Failed to Receive")

    def check_p_rate(self):
        #  check p rate
        if not (0 <= self.p_rate < 1):
            exit(-1)

    def check_port(self):
        #  check port numbers
        if not all(1024 <= x <= 64000 and isinstance(x, int) is True
                   for x in (self.c_sin, self.c_sout, self.c_rin, self.c_rout)):
            exit(-1)

    def socket_close(self):
        self.socket_rin.close()
        self.socket_rout.close()
        self.socket_sin.close()
        self.socket_sout.close()


if __name__ == "__main__":

    args = argparse.ArgumentParser()
    args.add_argument("csout", help="Channel Sender out port", type=int)
    args.add_argument("csin", help="Channel Sender in port", type=int)
    args.add_argument("crout", help="Channel Receiver out port", type=int)
    args.add_argument("crin", help="Channel Receiver in port", type=int)
    args.add_argument("sin", help="Sender in port", type=int)
    args.add_argument("rin", help="Receiver in port", type=int)
    args.add_argument("prate", help="P rate", type=float)
    args = args.parse_args()

    channel = Channel(args.csin, args.csout, args.crout, args.crin,
                      args.sin, args.rin, args.prate)
    channel.send_to()