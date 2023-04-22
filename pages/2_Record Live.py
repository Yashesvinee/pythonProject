import math
import math as m
import threading
from pathlib import Path

import av
import cv2
import mediapipe as mp
import requests
import streamlit as st
from aiortc.contrib.media import MediaRecorder
from streamlit_lottie import st_lottie
from streamlit_webrtc import webrtc_streamer

lock = threading.Lock()

mpPose = mp.solutions.pose
pose = mpPose.Pose()
mpDraw = mp.solutions.drawing_utils


def findDistance(x1, y1, x2, y2):
    dist = m.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return dist


def findmid(x1, y1, x2, y2):
    x = (x1 + x2) / 2
    y = (y1 + y2) / 2
    return x, y


def find_angle(x1, y1, x2, y2):
    m = (y2 - y1) / (x2 - x1)
    deg = abs(math.degrees(math.atan(m)))
    return int(deg)


out_file = Path("output.mp4")


def out_recorder_factory() -> MediaRecorder:
    return MediaRecorder(str(out_file), format="mp4")


class VideoTransformer:

    def recv(self, frame):
        image = frame.to_ndarray(format="bgr24")
        global timer, playing

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Process the image.
        keypoints = pose.process(image)

        # Convert the image back to BGR.
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # Use lm and lmPose as representative of the following methods.
        lm = keypoints.pose_landmarks
        lmPose = mpPose.PoseLandmark

        pose1 = []
        if keypoints.pose_landmarks:
            mpDraw.draw_landmarks(image, keypoints.pose_landmarks, mpPose.POSE_CONNECTIONS)
            for id, l in enumerate(keypoints.pose_landmarks.landmark):
                x_y_z = []
                h, w, c = image.shape
                x_y_z.append(l.x)
                x_y_z.append(l.y)
                x_y_z.append(l.z)
                x_y_z.append(l.visibility)
                pose1.append(x_y_z)

        Nose = pose1[0]
        L_Neck = pose1[11]
        R_Neck = pose1[12]
        R_Hip = pose1[24]
        L_Hip = pose1[23]
        R_Eye = pose1[5]
        L_Eye = pose1[2]
        offset = findDistance(L_Neck[0], L_Neck[1], R_Neck[0], R_Neck[1])
        neckx, necky = findmid(L_Neck[0], L_Neck[1], R_Neck[0], R_Neck[1])
        eyex, eyey = findmid(L_Eye[0], L_Eye[1], R_Eye[0], R_Eye[1])
        if int(offset * 100) < 10:
            neck_inclination = find_angle(neckx, necky, eyex, eyey)
        else:
            neck_inclination = find_angle(neckx, necky, Nose[0], Nose[1])
        torso_inclination = find_angle(L_Neck[0], L_Neck[1], R_Neck[0], R_Neck[1])
        score = {}
        score['neck'] = neck_inclination
        score['trunk'] = torso_inclination

        print(score)
        font = cv2.FONT_HERSHEY_SIMPLEX

        if not (score['neck'] in range(85, 90)) or not(score['trunk'] in range(0, 5)):
            string = "WARNING!!!!\nBAD POSTURE"
            cv2.putText(image, string, (0, h - 50), font, 0.5, (0, 255, 0), 2)

        elif not score['neck'] in range(70, 74) and int(offset * 100) < 10:
            string = "WARNING!!!!\nBAD POSTURE"
            cv2.putText(image, string, (0, h - 20), font, 0.5, (0, 255, 0), 2)
        else:
            timer = 0

        return av.VideoFrame.from_ndarray(image, format="bgr24")


timer = 0

url = requests.get(
    "https://assets4.lottiefiles.com/packages/lf20_wEt2nn.json")

url_json = dict()

if url.status_code == 200:
    url_json = url.json()
else:
    print("Error in the URL")

col1, col2 = st.columns([14, 2])

with col1:
    st.markdown("# Live monitoring")

with col2:
    st_lottie(url_json, height=100)

ctx = webrtc_streamer(key="live", video_processor_factory=VideoTransformer, out_recorder_factory=out_recorder_factory,
                      rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})
if out_file.exists():
    with out_file.open("rb") as f:
        st.download_button(
            "Download the recorded video with results", f, "output.mp4"
        )

# st.warning("alert")
