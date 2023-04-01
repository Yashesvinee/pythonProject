import math
import math as m
import threading
from pathlib import Path
from sys import prefix

import av
import mediapipe as mp
import cv2
import streamlit as st
from aiortc.contrib.media import MediaRecorder
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase,WebRtcMode
from streamlit_extras.switch_page_button import switch_page

lock=threading.Lock()
st.markdown("# Live monitoring")
mpPose = mp.solutions.pose
pose = mpPose.Pose()
mpDraw = mp.solutions.drawing_utils

def findDistance(x1, y1, x2, y2):
    dist = m.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return dist

def findmid(x1, y1, x2, y2):
    x=(x1+x2)/2
    y=(y1+y2)/2
    return x,y

def find_angle(x1,y1,x2,y2):
    m=(y2-y1)/(x2-x1)
    deg=abs(math.degrees(math.atan(m)))
    return int(deg)


RECORD_DIR = Path("../records")
RECORD_DIR.mkdir(exist_ok=True)
out_file = RECORD_DIR / f"output.mp4"
def out_recorder_factory() -> MediaRecorder:
    return MediaRecorder(str(out_file), format="mp4")

class VideoTransformer(VideoTransformerBase):

    def transform(self, frame):
        image = frame.to_ndarray(format="bgr24")
        global timer,playing

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
            # mpDraw.draw_landmarks(img, keypoints.pose_landmarks, mpPose.POSE_CONNECTIONS)
            for id, l in enumerate(keypoints.pose_landmarks.landmark):
                x_y_z = []
                h, w, c = image.shape
                x_y_z.append(l.x)
                x_y_z.append(l.y)
                x_y_z.append(l.z)
                x_y_z.append(l.visibility)
                pose1.append(x_y_z)
                # cx, cy = int(l.x*w), int(l.y*h)

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

        if not (score['neck'] in range(70, 74) and int(offset * 100) < 10) or  not (score['neck'] in range(87, 90)) or score['trunk'] in range(0, 3):
            pass
        else:
            timer=0

        print(score)
        font = cv2.FONT_HERSHEY_SIMPLEX

        string_reba = str(score)
        cv2.putText(image, string_reba, (0, h - 20), font, 0.5, (0, 255, 0), 2)

        #video_output.write(image)
        return image

timer=0

ctx=webrtc_streamer(key="live", video_transformer_factory=VideoTransformer,out_recorder_factory=out_recorder_factory,
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})
if out_file.exists():
        with out_file.open("rb") as f:
            st.download_button(
                "Download the recorded video with results", f, "output.mp4"
            )

# st.warning("alert")