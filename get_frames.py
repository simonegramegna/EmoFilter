import cv2
import time
import requests
import threading
from os import _exit
from threading import Thread
from keyboard import is_pressed
from filters_folder import filters

# load the face and eye recognizer
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_eye.xml')

# global variables used by threads
emotion = None
intensity = None
cap = cv2.VideoCapture(0)

frame_filtered = None
frame_not_filtered = None

# lock used to ensure that no global variables are corrupted
lock = threading.Lock()

# used to load the stream video and apply filter on it
def video_stream_filtered():
    offset = []
    global cap, intensity, emotion, frame_filtered, frame_not_filtered
    emotions = filters.Filters()
    emotion_local = None
    ret, frame = cap.read()
    img_h, img_w = frame.shape[:2]
    lock.acquire()
    frame_not_filtered = frame
    lock.release()
    while cap.isOpened() and ret:
        lock.acquire()
        ret, frame = cap.read()
        frame_not_filtered = frame.copy()
        emotion_local = emotion
        intensity_local = intensity
        lock.release()
        if emotion_local != "no_face" and emotion_local != None:
            mask_s_temp, offset = select_emotion(
                emotion_local, emotions, intensity)
            frame = apply_filter(frame, mask_s_temp, offset, img_w, img_h)
        lock.acquire()
        frame_filtered = frame
        lock.release()
        # cv2.imshow('img',frame)
        # cv2.waitKey(1)
    cap.release()
    cv2.destroyAllWindows()

# used to send frame to analize to the server and read the emotion
def load_camera_server():
    global cap, emotion, intensity
    i = 0
    frame = []
    while(True):  # cap.isOpened()
        lock.acquire()
        ret, frame = cap.read()
        lock.release()
        if ret:
            url = 'https://www.intintlab.uniba.it/face-analyzer'
            # encode il numpy array nel formato specificato (jpg), secondo valore e' array monodimensionale numpy dell'immagine
            is_success, im_buf_arr = cv2.imencode(".jpg", frame)
            # converte l'array in byte reali
            byte_frame = im_buf_arr.tobytes()
            # image to send
            my_img = {'image': byte_frame}
            # data to send to server
            my_data = {"emotion": "yes", "gender": "no",
                       "age": "no", "detect_face": "yes"}
            try:
                r = requests.post(url, data=my_data,
                                  files=my_img, verify=False)
            except requests.exception.RequestsJSONDecodeError:
                print("timeout")
                time.sleep(10)
            response_json = r.json()
            if "error" in response_json.keys():
                lock.acquire()
                emotion = "no_face"
                intensity = 0
                lock.release()
                print("no face")
            else:
                lock.acquire()
                emotion = response_json['emotion']
                intensity = response_json["probabilities"][emotion]
                lock.release()
                print(emotion)
            i += 1
            frame = []
        time.sleep(0.2)

# used to apply the filter on the frame
# input: the frame, the mask that rapresent the filter, offset array used to move the filter on the frame, img width and img height
def apply_filter(frame, mask_c_temp, offset, img_w, img_h):
    mask_c = mask_c_temp
    # dimension of the filter
    original_mask_c_h, original_mask_c_w, mask_c_channels = mask_c.shape
    # grey of the filter
    mask_c_grey = cv2.cvtColor(mask_c, cv2.COLOR_BGR2GRAY)
    # mask of the filter
    ret, original_mask_c = cv2.threshold(
        mask_c_grey, 10, 255, cv2.THRESH_BINARY_INV)
    # inverted mask of the filter
    original_mask_inv = cv2.bitwise_not(original_mask_c)
    # gray version of fram
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # faces recognized from the face_cascade
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    if len(faces) != 0:
        # coordinates of face region
        face_w = faces[0][2]  # w
        face_h = faces[0][3]  # h
        face_x1 = faces[0][0]  # x
        face_x2 = face_x1 + face_w
        face_y1 = faces[0][1]  # y
        face_y2 = face_y1 + face_h

        # filter size in relation to face by scaling
        mask_c_width = int(offset[0] * face_w)
        mask_c_height = int(
            mask_c_width * original_mask_c_h / original_mask_c_w)

        # setting location of coordinates of witch
        mask_c_x1 = face_x2 - int(face_w/2) - int(mask_c_width/2) + offset[1]
        mask_c_x2 = mask_c_x1 + mask_c_width
        mask_c_y1 = face_y1 + offset[2]
        mask_c_y2 = mask_c_y1 + mask_c_height

        # check to see if out of frame
        if mask_c_x1 < 0:
            mask_c_x1 = 0
        if mask_c_y1 < 0:
            mask_c_y1 = 0
        if mask_c_x2 > img_w:
            mask_c_x2 = img_w
        if mask_c_y2 > img_h:
            mask_c_y2 = img_h

        # account for any out of frame changes
        mask_c_width = mask_c_x2 - mask_c_x1
        mask_c_height = mask_c_y2 - mask_c_y1
        # resize witch to fit on face
        try:
            mask_c = cv2.resize(
                mask_c, (mask_c_width, mask_c_height), interpolation=cv2.INTER_AREA)
            mask = cv2.resize(original_mask_c, (mask_c_width,
                              mask_c_height), interpolation=cv2.INTER_AREA)
            mask_inv = cv2.resize(
                original_mask_inv, (mask_c_width, mask_c_height), interpolation=cv2.INTER_AREA)
            #entered = True

            # take roi(region of interest) for filter from background
            roi = frame[mask_c_y1:mask_c_y2, mask_c_x1:mask_c_x2]

            # changing color pixel in the frame and in the filter and adding the filter on the frame
            roi_bg = cv2.bitwise_and(roi, roi, mask=mask)
            roi_fg = cv2.bitwise_and(mask_c, mask_c, mask=mask_inv)
            dst = cv2.add(roi_bg, roi_fg)

            # put back in original frame
            frame[mask_c_y1:mask_c_y2, mask_c_x1:mask_c_x2] = dst
        except cv2.error as e:
            pass

    return frame

# used to select current emotion
# input: emotion_local is the current emotion read, emotions is the Filters objects with all the filters, intensity is the intensity of the emotion
def select_emotion(emotion_local,emotions,intensity):
    dim = []
    if emotion_local == "Anger":
        if intensity > 5:
            mask_s_temp = emotions.veryAnger[0]
            dim.append(emotions.veryAnger[1])
            dim.append(emotions.veryAnger[2])
            dim.append(emotions.veryAnger[3])
        else:
            mask_s_temp = emotions.anger[0]
            dim.append(emotions.anger[1])
            dim.append(emotions.anger[2])
            dim.append(emotions.anger[3])
    elif emotion_local == "Disgust":
        if intensity > 5:
            mask_s_temp = emotions.veryDisgust[0]
            dim.append(emotions.veryDisgust[1])
            dim.append(emotions.veryDisgust[2])
            dim.append(emotions.veryDisgust[3])
        else:
            mask_s_temp = emotions.disgust[0]
            dim.append(emotions.disgust[1])
            dim.append(emotions.disgust[2])
            dim.append(emotions.disgust[3])
    elif emotion_local == "Fear":
        if intensity > 5:
            mask_s_temp = emotions.veryFear[0]
            dim.append(emotions.veryFear[1])
            dim.append(emotions.veryFear[2])
            dim.append(emotions.veryFear[3])
        else:
            mask_s_temp = emotions.fear[0]
            dim.append(emotions.fear[1])
            dim.append(emotions.fear[2])
            dim.append(emotions.fear[3])
    elif emotion_local == "Happiness":
        if intensity > 5:
            mask_s_temp = emotions.veryHappiness[0]
            dim.append(emotions.veryHappiness[1])
            dim.append(emotions.veryHappiness[2])
            dim.append(emotions.veryHappiness[3])
        else:
            mask_s_temp = emotions.happiness[0]
            dim.append(emotions.happiness[1])
            dim.append(emotions.happiness[2])
            dim.append(emotions.happiness[3])
    elif emotion_local == "Neutral":
        if intensity > 5:
            mask_s_temp = emotions.veryNeutral[0]
            dim.append(emotions.veryNeutral[1])
            dim.append(emotions.veryNeutral[2])
            dim.append(emotions.veryNeutral[3])
        else:
            mask_s_temp = emotions.neutral[0]
            dim.append(emotions.neutral[1])
            dim.append(emotions.neutral[2])
            dim.append(emotions.neutral[3])
    elif emotion_local == "Sadness":
        if intensity > 5:
            mask_s_temp = emotions.verySadness[0]
            dim.append(emotions.verySadness[1])
            dim.append(emotions.verySadness[2])
            dim.append(emotions.verySadness[3])
        else:
            mask_s_temp = emotions.sadness[0]
            dim.append(emotions.sadness[1])
            dim.append(emotions.sadness[2])
            dim.append(emotions.sadness[3])
    elif emotion_local == "Surprise":
        if intensity > 5:
            mask_s_temp = emotions.verySurprise[0]
            dim.append(emotions.verySurprise[1])
            dim.append(emotions.verySurprise[2])
            dim.append(emotions.verySurprise[3])
        else:
            mask_s_temp = emotions.surprise[0]
            dim.append(emotions.surprise[1])
            dim.append(emotions.surprise[2])
            dim.append(emotions.surprise[3])
    return mask_s_temp, dim

# used to kill the application
def kill_process():
    while True:  # making a loop
        time.sleep(1)
        try:  # this way if another button is pressed no errors are printed in consolle
            if is_pressed('s'):  # if 's' is pressed
                _exit(1)
        except:
            pass

# main
def main():
    server_video = Thread(target=load_camera_server)
    server_video.daemon = True
    server_video.start()
    video_filter = Thread(target=video_stream_filtered)
    video_filter.daemon = True
    video_filter.start()
    kill_process_thread = Thread(target=kill_process)
    kill_process_thread.start()


# chiamo il main
main()
