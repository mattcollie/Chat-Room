from socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST, SO_REUSEPORT, gethostname, gethostbyname
from threading import Thread
import pyaudio


class Client:

    def __init__(self, host='', port=37020, buffer_size=4096, format=pyaudio.paInt16, channels=2, rate=44100, chunk=256):
        self._host = host
        self._port = port
        self._buffer_size = buffer_size
        self._format = format
        self._channels = channels
        self._rate = rate
        self._chunk = chunk
        self._sock = socket(AF_INET, SOCK_DGRAM)  # UDP
        self._sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 2)
        self._sock.setsockopt(SOL_SOCKET, SO_REUSEPORT, 2)

        audio = pyaudio.PyAudio()
        self._stream_in = audio.open(format=format, channels=channels, rate=rate, input=True, frames_per_buffer=chunk)
        self._stream_out = audio.open(format=format, channels=channels, rate=rate, output=True, frames_per_buffer=chunk)

    def start(self):
        self._sock.bind((self._host, self._port))
        Thread(target=self._handle_audio_in).start()
        Thread(target=self._handle_audio_out).start()

    def _handle_audio_in(self):
        while True:
            data, addr = self._sock.recvfrom(self._chunk * self._channels * 2)
            if addr[0] != gethostbyname(gethostname()):
                self._stream_out.write(data, self._chunk)

    def _handle_audio_out(self):
        while True:
            data = self._stream_in.read(self._chunk, exception_on_overflow=False)
            self._sock.sendto(data, ('<broadcast>', self._port))


client = Client()
client.start()
