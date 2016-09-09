from packet_class import *  # Our initialization and checks
import os
import socket  # or sockets
import argparse

PTYPE_DATA = 0
PTYPE_ACK = 1

MAGICNO = 0x497E
MAX_READ_SIZE = 512  # bytes
TIMEOUT = 1  # 1 second
PATH = './file.txt'
IP = '127.0.0.1'


class Receiver:
    """Receiver Program"""

    def __init__(self, rin, rout, crin, file_name):
        self.rin = rin
        self.rout = rout
        self.crin = crin
        self.file_name = file_name
        self.socket_rin = self.create_sockets(self.rin)
        self.socket_rout = self.create_sockets(self.rout)

    def create_sockets(self, port):
        #  socket creation
        self.check_ports()
        try:
            #  accepts packets from channel
            new_socket = socket.socket(socket.AF_INET,
                                       socket.SOCK_DGRAM)
            new_socket.bind((IP, port))
            print("Socket Created")
            return new_socket
        except:
            #  ailed to create socket... quit
            exit(-1)

        # bind() both sockets

    def receive_socket(self):

        # connect() rout set default to port_num of crin
        self.socket_rout.connect((IP, self.crin))
        print("socket connected")
        self.check_file()
        open(self.file_name)
        expected = 0  # local int var

        # if initialization successful then loop
        success = True
        while success:
            print("in while")
            # wait on rin for incoming packet (use blocking call)
            received = self.received_packet()
            print("Packet Received")
            # once have received packet do checks
            # when different prepare ack packet
            if not Receiver.check_failure(received, expected):
                self.reply_to(received)
                continue  # return to beginning of loop

            if received.seqno == expected:
                self.reply_to(received)
                # send received_ack via rout to channel
                expected += 1

            if received.dataLen > 0:  # if received packet contains data then
                # append data to output file
                self.file_name.append(received.data)
                continue  # stop processing

            elif received.dataLen == 0:
                self.close_sockets()
                exit(0)  # exit program

            else:
                continue  # return to start of loop

    def received_packet(self):
        received_string = self.socket_rin.recv(MAX_READ_SIZE)
        received = Packet.deserialize(received_string)
        return received

    def reply_to(self, received):

        received_ack = received.serialize()
        # send packet via rout to channel
        self.socket_rout.send(received_ack)

    @staticmethod
    def check_failure(received_pack, expected):
            #  if packet is lost
            if received_pack.check_magicno() and received_pack.ptype == \
                    PTYPE_DATA or received_pack.seqno != expected:
                return False

    def check_ports(self):
        if not(1024 < self.rin < 64000 or 1024 < self.rout < 64000):
            print("the port numbers are not between 1024 and 64000")
            exit(-1)

    def check_file(self):
        open(self.file_name)
        if os.path.isfile(PATH) and os.access(PATH, os.R_OK):
            exit(-1)

    def close_sockets(self):
        self.file_name.close()  # close output file
        self.socket_rout.close()  # close all sockets
        self.socket_rin.close()


if __name__ == "__main__":

    args = argparse.ArgumentParser()

    args.add_argument("rin", help="Receiver in port", type=int)
    args.add_argument("rout", help="Receiver out port", type=int)
    args.add_argument("crin", help="Receiver Sender in port", type=int)
    args.add_argument("file_out", help="Filename of receiver", type=str)

    args = args.parse_args()

    receiver = Receiver(args.rin, args.rout, args.crin, args.file_out)
    receiver.receive_socket()


