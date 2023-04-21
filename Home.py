import sys
import tempfile
from streamlit_extras.switch_page_button import switch_page
import av
from streamlit_webrtc import webrtc_streamer
import streamlit as st
import numpy as np
from PIL import Image
import math
import json
import requests


from streamlit_lottie import st_lottie
import cv2
import mediapipe as mp
from score_calc_func import pose_estimation
from score_calc_func import angle_calc
import mimetypes
from tkinter import filedialog
import math as m

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
def image_pose_estimation(name):

    score,image=pose_estimation(name)
    print(score)
    return score,image
    #if rula and reba:
     ##       pgi.alert("Posture not proper in upper body","Warning")
     #   elif int(reba)>4:
    #        pgi.alert("Posture not proper in your body","Warning")
    #variable1.set("Rapid Upper Limb Assessment Score : "+rula)
    #variable2.set("Rapid Entire Body Score : "+reba)
    #root.update()
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def video_pose_estimation(cap):
    # For webcam input replace file name with 0.
    # file_name = 'input.mp4'
    # cap = cv2.VideoCapture(name)
    good_frames = 0
    bad_frames = 0
    if cap=='a':
        return

    # Meta.
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_size = (width, height)
    fourcc = cv2.VideoWriter_fourcc(*'H264')

    # Video writer.
    video_output = cv2.VideoWriter('output.mp4', fourcc, fps, frame_size)

    while cap.isOpened():
        # Capture frames.
        success, image = cap.read()
        if not success:
            print("Null.Frames")
            break
        # Get fps.
        fps = cap.get(cv2.CAP_PROP_FPS)
        # Get height and width.
        h, w = image.shape[:2]

        # Convert the BGR image to RGB.
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
                cx, cy = int(l.x * w), int(l.y * h)
                if id % 2 == 0:
                    cv2.circle(image, (cx, cy), 5, (255, 0, 0), cv2.FILLED)
                else:
                    cv2.circle(image, (cx, cy), 5, (255, 0, 255), cv2.FILLED)

        if(cap==0):
            Nose = pose1[0]
            L_Neck = pose1[11]
            R_Neck = pose1[12]
            R_Hip = pose1[24]
            L_Hip = pose1[23]
            R_Eye = pose1[5]
            L_Eye = pose1[2]
            offset = findDistance(L_Neck[0], L_Neck[1], R_Neck[0], R_Neck[1])
            neckx, necky = findmid(L_Neck[0], L_Neck[1], R_Neck[0], R_Neck[1])
            eyex,eyey=findmid(L_Eye[0],L_Eye[1],R_Eye[0],R_Eye[1])
            if int(offset*100)<10:
                neck_inclination = find_angle(neckx, necky, eyex, eyey)
            else:
                neck_inclination = find_angle(neckx,necky,Nose[0],Nose[1])
            torso_inclination= find_angle(L_Neck[0],L_Neck[1],R_Neck[0],R_Neck[1])
            score = {}
            score['neck'] = neck_inclination
            score['trunk'] = torso_inclination
            if (score['neck'] in range(70,74) and int(offset*100)<10) or (score['neck'] in range(87,90)) or score['trunk'] in range(0,3):
                pass
        else:
            try:
                score= angle_calc(pose1)
            except:
                continue
        print(score)
        font=cv2.FONT_HERSHEY_SIMPLEX

        string_reba = str(score)
        cv2.putText(image, string_reba, (0, h - 20), font, 0.5, (0,255,0), 2)

        video_output.write(image)

        # Display.
        #cv2.imshow('MediaPipe Pose', image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            return video_output

    cap.release()
    cv2.destroyAllWindows()
    return video_output


def main_loop():
    st.set_page_config(
        page_title="Posture Risk Assessment",
        page_icon="🧊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    url = requests.get(
        "https://assets2.lottiefiles.com/packages/lf20_cmaqoazd.json")
    # Creating a blank dictionary to store JSON file,
    # as their structure is similar to Python Dictionary
    url_json = dict()

    if url.status_code == 200:
        url_json = url.json()
    else:
        print("Error in the URL")

    col1, col2 = st.columns([40,26])

    with col1:
        st.title("Posture risk assessment Tool")
        st.subheader("Get instant results on how risky your posture is!!!")
        st.text("Upload an image or video to get your results.")
        st.text("To record and get results for a live video, navigate to Live Monitoring.")
        live = st.button("Go to Live")
        if live:
            switch_page("record live")

    with col2:
        st_lottie(url_json, height=300)




    image_file = st.file_uploader("Upload Your Image", type=['jpg', 'png', 'jpeg'])
    video_file = st.file_uploader("Upload Your Video", type=['mp4', 'mov', 'mpeg'])

    if image_file:
        filebytes=np.asarray(bytearray(image_file.read()),dtype=np.uint8)
        img = cv2.imdecode(filebytes, 1)
        score,image = image_pose_estimation(img)
        st.image(image, channels='BGR')
        st.write(score)
        # with open(image_file.name,'wb') as f:
        #     filebytes=np.asarray(bytearray(image_file.read()),dtype=np.uint8)
        #     img=cv2.imdecode(filebytes,1)
        #     score = image_pose_estimation(img)
        #     # img = Image.open(image_file)
        #     st.image(img,channels="BGR")
        #     # img_array=np.array(img)
        #     # score = image_pose_estimation(img_array)
        #     st.write(score)
    elif video_file:
        tfile=tempfile.NamedTemporaryFile(delete=False)
        tfile.write(video_file.read())
        analyse=st.button(label="Analyse")
        if analyse:
           video_pose_estimation(cv2.VideoCapture(tfile.name))
           vf=open('output.mp4','rb')
           st.video(vf,format='video/mp4')
           with open('output.mp4','rb') as vf:
               btn= st.download_button(label='download',data=vf,file_name='output.mp4',mime='video/mp4')


if __name__ == '__main__':
    main_loop()