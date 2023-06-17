import tkinter
import cv2
import PIL.Image, PIL.ImageTk
import time
import imutils
from datetime import date

import configparser
from ultralytics import YOLO
import numpy as np
import codecs
import PIL.Image, PIL.ImageTk
import logging


logging.getLogger("utils.general").setLevel(logging.WARNING)

config = configparser.ConfigParser()
config.read_file(codecs.open("config.ini", 'r', 'utf8'))

fps_formula = {'Option 1': '1', 'Option 3': 'self.frame_id % 10 == 5 or self.frame_id % 10 == 0', 'Option 2': 'self.frame_id % 2 == 0'}
stuff = {'backpack': 'Рюкзак', 'handbag': 'Сумка', 'suitcase': 'Кейс', 'knife': 'Нож'}


class AppSeg:
    def __init__(self, window, window_title, video_source=0):
        self.window = window
        self.window.title(window_title)		
        self.video_source = video_source


        # open video source (by default this will try to open the computer webcam)
        self.vid = VideoSide(self.video_source)
        self.win_w = 800
        self.win_h = 600

        self.frame_id = 0

        self.video_path_out = f'out-{date.today()}.avi'
        if config['Stream']['save_state'] == 'Yes':
            self.out = cv2.VideoWriter(self.video_path_out, 
                    cv2.VideoWriter_fourcc(*'MJPG'),
                    int(self.vid.vid.get(cv2.CAP_PROP_FPS)), 
                    (int(self.vid.vid.get(3)), int(self.vid.vid.get(4)))
                    )
        else:
            self.out = False

        window.geometry(f'1024x602')

        # Create a canvas that can fit the above video source size
        self.canvas = tkinter.Canvas(window, width=self.win_w, height=self.win_h, bg='black') # self.vid.height
        self.canvas.grid(column=0, row=0)
        self.canvas2 = tkinter.Canvas(window, bg='black', width=220, height=600)
        self.canvas2.grid(column=1, row=0)

        self.lab = tkinter.Text(self.canvas2, height=35, width=27,wrap="word", bg='black', fg='white')
        self.lab.config(state='disabled')
        self.lab.grid()

        # After it is called once, the update method will be automatically called every delay milliseconds
        self.delay = 15
        self.update()
        self.window.protocol('WM_DELETE_WINDOW', self.close_window)
        self.window.mainloop()
        

    def update(self):
        # Get a frame from the video source
        ret, frame = self.vid.get_frame()

        font = cv2.FONT_HERSHEY_COMPLEX

        ys = YOLOSegmentation("yolov8x-seg.pt")

        if ret:
            self.frame_id += 1
            if eval(fps_formula[config['Stream']['fps_f']]):
                result = ys.detect(frame)
                if result:
                    bboxes, classes, segmentations, scores, names = result
                    for bbox, class_id, seg, score in zip(bboxes, classes, segmentations, scores):
                        # print(f"Вероятность: {score * 100}%")
                        (x, y, x2, y2) = bbox
                        cv2.polylines(frame, [seg], True, (255, 0, 0), 4)
                        self.lab.config(state='normal')
                        self.lab.insert(1.0, f"\n{time.ctime()}\nОбнаружение: {stuff[names.get(int(class_id))]}\n")
                        self.lab.config(state='disable')
                if config['Stream']['save_state'] == 'Yes':
                    self.out.write(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  )

            img = imutils.resize(frame, width=800, height=600)
            self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(img))
            self.canvas.create_image(self.win_w / 2, self.win_h / 2, image = self.photo, anchor = tkinter.CENTER)
  
            self.window.after(self.delay, self.update)

    def close_window(self):
        if config['Stream']['save_state'] == 'Yes':
            self.out.release()
        self.window.destroy()


class VideoSide:
    def __init__(self, video_source=0):
        # Open the video source
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)

        # Get video source width and height
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)


    def get_frame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                # Return a boolean success flag and the current frame converted to BGR
                return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            else:
                return (ret, None)
        else:
            return (ret, None)

    # Release the video source when the object is destroyed
    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()



class YOLOSegmentation:
    def __init__(self, model_path):
        self.model = YOLO(model_path)    

    def detect(self, img):
        try:
            height, width, channels = img.shape
            results = self.model.predict(source=img.copy(), save=False, save_txt=False, classes=[24, 26, 28, 43], verbose=False)
            result = results[0]
            segmentation_contours_idx = []
            for seg in result.masks.segments:
                seg[:, 0] *= width
                seg[:, 1] *= height
                segment = np.array(seg, dtype=np.int32)
                segmentation_contours_idx.append(segment)
        except Exception as e:
            return False
        bboxes = np.array(result.boxes.xyxy.cpu(), dtype="int")
        class_ids = np.array(result.boxes.cls.cpu(), dtype="int")
        scores = np.array(result.boxes.conf.cpu(), dtype="float").round(2)
        return bboxes, class_ids, segmentation_contours_idx, scores, self.model.model.names


def detect(source):
    app = tkinter.Tk()
    AppSeg(app, "Segmentator", video_source=source)


