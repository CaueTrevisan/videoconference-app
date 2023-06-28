import cv2
import zmq
import threading
import numpy as np


class VideoStreaming:
    __context = zmq.Context()
    __video_publisher_socket = __context.socket(zmq.PUB)
    __video_server_threads = []
    __video_client_threads = []
    def __init__(self, id):
        self.id=id
        print(f'[{self.id}] Conectado à videotransmissao!')        
        self.video_streaming_server()
        self.video_streaming_client()

    def __format_print(self, sender, message):
        print(f'[id={self.id}] [sender={sender}]: {message}')

    def video_streaming_server(self):
        self.__video_publisher_socket.bind(f"tcp://*:55{self.id}2")
        thread = threading.Thread(target=self.__video_streaming_server_thread, args=())
        self.__video_server_threads.append(thread)
        thread.start()

    def __video_streaming_server_thread(self):
        video_capture = cv2.VideoCapture(0)
        while True:
            ret, frame = video_capture.read()
            encoded_frame = cv2.imencode('.jpg', frame)[1].tobytes()
            self.__video_publisher_socket.send(encoded_frame)
        video_capture.release()

    def video_streaming_client(self):
        for newSocket in range(8):
            context = zmq.Context()
            socket = context.socket(zmq.SUB)
            socket.connect(f"tcp://localhost:55{newSocket}2")
            socket.setsockopt(zmq.SUBSCRIBE, b"")
            thread = threading.Thread(target=self.__video_streaming_client_thread, args=(socket,newSocket))
            self.__video_client_threads.append(thread)
            thread.start()

    def __video_streaming_client_thread(self, socket, sender):
        windowName = f'Video [id={self.id}] [sender={sender}]'
        while True:
            encoded_frame = socket.recv()
            frame = cv2.imdecode(np.frombuffer(encoded_frame, dtype=np.uint8), cv2.IMREAD_COLOR)
            cv2.imshow(windowName, frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cv2.destroyWindow(windowName)
            
    def video_streaming_join(self):
        windowName=f'Video [id={self.id}]'
        while True:
            #frame0 = cv2.resize( data_deque_dict[0].popleft(), (640,480))
            #frame1 = cv2.resize( data_deque_dict[1].popleft(), (640,480))
            #frame2 = cv2.resize( data_deque_dict[2].popleft(), (640,480))            

            '''combined_frame= cv2.hconcat([frame0,frame1, frame2])
            cv2.imshow(windowName,combined_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break'''
        cv2.destroyWindow(windowName)
            
        