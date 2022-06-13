import os
import time
from numpy import ndarray
from cv2 import imencode, imwrite
from flask import Flask, render_template, Response, request


if os.environ.get('WERKZEUG_RUN_MAIN') or Flask.debug is False:
    import get_frames

app = Flask(__name__)

frame = None
frame_not_filtered = None
IMG_FOLDER = 'images'

# generate frame by frame from camera


def gen_frames():
    global frame, frame_not_filtered
    while True:
        # Capture frame-by-frame
        get_frames.lock.acquire()
        frame = get_frames.frame_filtered
        frame_not_filtered = get_frames.frame_not_filtered
        get_frames.lock.release()  # read the camera frame
        if isinstance(frame, ndarray):
            ret, buffer = imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result


def save_frame():
    global frame_not_filtered
    file_name = IMG_FOLDER + '/' + str(time.time()) + ".jpg"
    imwrite(file_name, frame_not_filtered)


@app.route('/video_feed')
def video_feed():
    # Video streaming route. Put this in the src attribute of an img tag
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/save_frame', methods=['POST', 'GET'])
def index_save():
    if request.method == 'POST':
        save_frame()
    return render_template('index.html')


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


def main():
    if not os.path.exists(IMG_FOLDER):
        os.mkdir(IMG_FOLDER)

    app.run(debug=True)


main()
