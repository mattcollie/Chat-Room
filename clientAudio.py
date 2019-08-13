from array import array
from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST, SO_REUSEPORT, gethostname, gethostbyname
from threading import Thread

import pyaudio

HOST = '127.0.0.1'
PORT = 4000
BufferSize = 4096

FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
CHUNK = 256


class Client:

    def __init__(self, host='', port=37020, buffer_size=4096):
        self._host = host
        self._port = port
        self._buffer_size = buffer_size
        self._sock = socket(AF_INET, SOCK_DGRAM)  # UDP
        self._sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        self._sock.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)

        audio = pyaudio.PyAudio()
        self._stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, output=True,
                                  frames_per_buffer=CHUNK)

    def start(self):
        self._sock.bind((self._host, self._port))
        Thread(target=self._handle_audio_in).start()
        Thread(target=self._handle_audio_out).start()

    def _handle_audio_in(self):
        while True:
            # data = self._recvall(self._buffer_size)
            data, addr = self._sock.recvfrom(self._buffer_size)
            if addr[0] != gethostbyname(gethostname()):
                self._stream.write(data)

    def _recvall(self, size):
        databytes = b''
        while len(databytes) != size:
            to_read = size - len(databytes)
            if to_read > (4 * CHUNK):
                databytes += self._sock.recvfrom(4 * CHUNK)
            else:
                databytes += self._sock.recvfrom(to_read)
        return databytes

    def _handle_audio_out(self):
        while True:
            data = self._stream.read(CHUNK, exception_on_overflow=False)
            data_chunk = array('h', data)
            volume = max(data_chunk)
            self._sock.sendto(data, ('<broadcast>', self._port))

def tcp_server():
    def SendAudio():
        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)
            data_chunk = array('h', data)
            volume = max(data_chunk)
            client.sendall(data)

    def RecieveAudio():
        while True:
            data = recvall(BufferSize)
            stream.write(data)

    def recvall(size):
        databytes = b''
        while len(databytes) != size:
            to_read = size - len(databytes)
            if to_read > (4 * CHUNK):
                databytes += client.recv(4 * CHUNK)
            else:
                databytes += client.recv(to_read)
        return databytes

    client = socket(family=AF_INET, type=SOCK_STREAM)
    client.connect((HOST, PORT))

    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, output=True, frames_per_buffer=CHUNK)

    RecieveAudioThread = Thread(target=RecieveAudio).start()
    SendAudioThread = Thread(target=SendAudio).start()


def voice_server():
    _socket = socket(AF_INET, SOCK_DGRAM)

    while 1:
        message = input("> ")

        # encode the message
        message = message.encode()

        # send the message
        _socket.sendto(message, ("127.0.0.1", 6666))

        # output the response (if any)
        data, ip = _socket.recvfrom(1024)

        print("{}: {}".format(ip, data.decode()))


def broadcast_receive():
    import socket

    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
    client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    client.bind(("", 37020))
    while True:
        data, addr = client.recvfrom(1024)
        print("received message: %s" % data)


if __name__ == '__main__':
    client = Client()
    client.start()
