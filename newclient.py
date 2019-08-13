from socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST, SO_REUSEPORT, gethostname, gethostbyname
from threading import Thread
import pyaudio


class Client:

    def __init__(self, host='', port=37020, buffer_size=4096, format=pyaudio.paInt16, channels=2, rate=44100, chunk=1024):
        self._host = host
        self._port = port
        self._buffer_size = buffer_size
        self._format = format
        self._channels = channels
        self._rate = rate
        self._chunk = chunk
        self._sock = socket(AF_INET, SOCK_DGRAM)  # UDP
        self._sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        self._sock.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)

        audio = pyaudio.PyAudio()
        self._stream = audio.open(format=format, channels=channels, rate=rate, input=True, output=True,
                                  frames_per_buffer=chunk)

    def start(self):
        self._sock.bind((self._host, self._port))
        Thread(target=self._handle_audio_in).start()
        Thread(target=self._handle_audio_out).start()

    def _handle_audio_in(self):
        while True:
            data, addr = self._sock.recvfrom(self._buffer_size)
            if addr[0] != gethostbyname(gethostname()):
                self._stream.write(data)

    def _handle_audio_out(self):
        while True:
            data = self._stream.read(self._chunk, exception_on_overflow=False)
            self._sock.sendto(data, ('<broadcast>', self._port))

client = Client()
client.start()