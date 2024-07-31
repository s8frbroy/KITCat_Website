
from typing import Any, Dict, Optional, cast, List
import threading
import queue

import pyaudio
from pythonrecordingclient.inputStreamAdapter import BaseAdapter


def read_audio(stream, chunk_size, queue):
    while True:
        chunk = stream.read(chunk_size, exception_on_overflow=False)
        queue.put(chunk)

class WebsiteStream(BaseAdapter):

    def __init__(self, audio_data) -> None:
        self.audio_data = audio_data
        self._stream: bytes = b''
        self.queue = queue.Queue()
        self.chunk_size = 1024
    
    def set_audio_data(self, audio_data: bytes) ->None:
        self.audio_data = audio_data

    def read_audio(self):
        # Simulate reading audio data asynchronously
        # Set the initial position of the BytesIO object
        self.audio_data.seek(0)
        # Iterate over the audio data and split it into chunks
        while True:
            # Read a chunk of data from self.audio_data
            chunk = self.audio_data.read(self.chunk_size)
            # If chunk is empty, break the loop
            
            # Print information about the current chunk
            # print(f"Chunk has length {len(chunk)}, expected: {self.chunk_size}")
            # Put the chunk into the queue
            self.queue.put(chunk)
            if len(chunk) < self.chunk_size:
                # print("break")
                break
        # print("Out of loop")
        '''    
        print(f"\nIn read_audio --> ")
        #print(f"audio_data has length: {len(self.audio_data)}")
        while True:
            for i in range(0, len(self.audio_data.getbuffer()), self.chunk_size):
                chunk = self.audio_data[i:i + self.chunk_size]
                print(f"{i}th chunk has length {len(chunk)}, expected: {len(self.chunk_size)}")
                self.queue.put(chunk)
            print(f"Queue after read_audio: {self.queue}")
            break
        '''


    def get_stream(self) -> bytes:
        # If stream is not initialized
        if not self._stream:
            # Start a thread to simulate reading audio data asynchronously
            thread = threading.Thread(target=self.read_audio)
            thread.daemon = True
            thread.start()

        return self._stream

    def read(self) -> bytes:
        # self.get_stream()
        print("Start read_audio")
        self.read_audio()
        size = max(self.queue.qsize(), 1)
        chunks = [self.queue.get() for _ in range(size)]
        
        if len(chunks) > 75:
            print("WARNING: Network is too slow. Having at least 5 seconds of delay!")

        return b''.join(chunks)

    def chunk_modify(self, chunk: bytes) -> bytes:
        # Modify audio chunk if needed
        return chunk


    def cleanup(self) -> None:
        if self._stream is not None:
            self._stream.stop_stream()
            self._stream.close()

        if self._pyaudio is not None:
            self._pyaudio.terminate()

    def set_input(self, id: int) -> None:
        devices = self.get_audio_devices()
        try:
            devName = devices[id]
            self.input_id = id
        except (ValueError, KeyError) as e:
            self.print_all_devices()
            sys.exit(1)

    def get_audio_devices(self) -> Dict[int, str]:
        devices = {}

        p = self.pyaudio
        info = p.get_host_api_info_by_index(0)
        deviceCount = info.get('deviceCount')

        for i in range(0, deviceCount):
                if p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels') > 0:
                        devices[i] = p.get_device_info_by_host_api_device_index(0, i).get('name')
        return devices

    def print_all_devices(self) -> None:
        """
        Special command, prints all audio devices available
        """
        print('-- AUDIO devices:')
        devices = self.get_audio_devices()
        for key in devices:
            dev = devices[key]
            if isinstance(dev, bytes):
                dev = dev.decode("ascii", "replace")
            print('    id=%i - %s' % (key, dev))

    @property
    def pyaudio(self) -> pyaudio.PyAudio:
        if self._pyaudio == None:
            self._pyaudio = pyaudio.PyAudio()
        return self._pyaudio

    def set_audio_channel_filter(self, channel: int) -> None:
        # actually chosing a specific channel is apparently impossible with portaudio,
        # so we record all channels instead and then filter out the wanted channel with numpy
        if self.input_id is None:
            raise BugException()
        channelCount = self.pyaudio.get_device_info_by_host_api_device_index(0, self.input_id).get('maxInputChannels')
        self.channel_count = channelCount
        self.chosen_channel = channel

