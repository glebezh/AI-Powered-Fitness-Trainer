import cv2
import streamlit as st
import mediapipe as mp
import numpy as np

# Importing necessary functions
from streamlit_webrtc import webrtc_streamer
from Utilities.tracking_overlay import tracking_overlay
from Utilities.available_cameras import get_available_cameras
from Exercises.squats import process_squat_angle
from Exercises.laterals import process_laterals_angle
from Exercises.pushups import process_pushup_angle
from Exercises.bicepcurls import process_bicepcurls_angle


# Creating variables
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# UI and setting wide page layout
st.set_page_config(layout="wide")
st.title("AI-Powered Fitness Trainer")
st.sidebar.title("Workout Options", )

# Sidebar content for selecting workout and other options
workout = st.sidebar.selectbox("Choose an Exercise", ["Lateral Raises", "Pushups", "Bicep Curls", "Squats"])
reps_goal = st.sidebar.slider("Set Reps Goal", 1, 50, 10)
sets_goal = st.sidebar.slider("Set Sets Goal", 1, 5, 3)

if workout == "Squats":
    st.sidebar.markdown("**Squats:** A great lower body exercise to build strength.")
elif workout == "Pushups":
    st.sidebar.markdown("**Pushups:** A great upper body exercise to build chest and arm strength.")
elif workout == "Bicep Curls":
    st.sidebar.markdown("**Bicep Curls:** A great isolation exercise for your arms.")
elif workout == "Lateral Raises":
    st.sidebar.markdown("**Lateral Raises:** A great exercises to target your lateral deltoids.")

# Get available camera sources
available_cameras = get_available_cameras()

# Initialize camera selection in session state
if "camera_index" not in st.session_state:
    st.session_state.camera_index = 0 

# Select camera in the sidebar and set session state to variable
camera_index = st.sidebar.selectbox("Select Camera Source", available_cameras, index=st.session_state.camera_index, help="Select the camera source")
st.session_state.camera_index = camera_index

# Create container for the sidebar
sidebar_container = st.sidebar.container()
sidebar_container.write("")

col1, col2, col3 = sidebar_container.columns([1, 2, 1]) 
with col2:
    run_camera = st.button("I'm ready to go!")

container = st.empty()

if not run_camera:
    st.session_state.run_camera = False 

# Button to toggle the camera
if run_camera:
    st.session_state.run_camera = True

# If application not started, then show instructions
if not st.session_state.run_camera:
    container.markdown("""
    Welcome to the AI-Powered Fitness Trainer! Let's get started.
    - Firstly, select your exercise.
    - Next, select reps and sets.
    - Finally, click on the confirm button to start the workout.
    - The AI will evaluate your exercise performance!
    """)


# If button pressed, start video capture and initialise the model
if st.session_state.run_camera:
    
    # Initialize necessary variables and selected camera
    reps = 0
    sets = 0
    stage = None
    active_side = "right"
    feedback = ""
    cap = cv2.VideoCapture(st.session_state.camera_index)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    FRAME_WINDOW = st.image([])
    REQUIRED_VISIBILITY = 0.75

    # Create progress bar and progress text once webcam is initialised
    col1, col2 = st.columns([1, 5])
    with col1:
        st.markdown("My Progress")
    with col2:
        progress = st.progress(reps/reps_goal)

    
    # Initialise the model with complexity 1
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5, model_complexity=1) as pose:
        while run_camera:
            ret, frame = cap.read()
            if not ret:
                st.error("Failed to capture video, please refresh the window")
                break

            # Process frame
            frame = cv2.flip(frame, 1)
            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(image_rgb)

            # Extract landmarks and calculate angles
            if results.pose_landmarks:
                
                # Adjust reps
                if reps == reps_goal:
                    sets += 1
                    reps = 0

                # Extract landmarks
                landmarks = results.pose_landmarks.landmark

                # Biceps/Pushups Calculations
                left_shoulder_landmark = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
                left_elbow_landmark = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value]
                left_wrist_landmark = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value]

                right_shoulder_landmark = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
                right_elbow_landmark = landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value]
                right_wrist_landmark = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value]

                # Squats Calculations
                left_hip_landmark = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
                left_knee_landmark = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value]
                left_ankle_landmark = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]

                right_hip_landmark = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]
                right_knee_landmark = landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value]
                right_ankle_landmark = landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value]

                # Examine appropriate landmarks based on exercise
                if workout == "Pushups":
                    # Logic to process left or right side depending on what is most visible
                    if (left_shoulder_landmark.visibility > REQUIRED_VISIBILITY and
                        left_elbow_landmark.visibility > REQUIRED_VISIBILITY and 
                        left_wrist_landmark.visibility > REQUIRED_VISIBILITY
                    ):
                        left_shoulder = [left_shoulder_landmark.x, left_shoulder_landmark.y]
                        left_elbow = [left_elbow_landmark.x, left_elbow_landmark.y]
                        left_wrist = [left_wrist_landmark.x, left_wrist_landmark.y]
                        active_side = "left"
                        stage, reps, feedback = process_pushup_angle(left_shoulder, left_elbow, left_wrist, stage, reps, reps_goal, feedback)

                    elif (right_shoulder_landmark.visibility > REQUIRED_VISIBILITY and
                        right_elbow_landmark.visibility > REQUIRED_VISIBILITY and 
                        right_wrist_landmark.visibility > REQUIRED_VISIBILITY
                    ):
                        right_shoulder = [right_shoulder_landmark.x, right_shoulder_landmark.y]
                        right_elbow = [right_elbow_landmark.x, right_elbow_landmark.y]
                        right_wrist = [right_wrist_landmark.x, right_wrist_landmark.y]
                        active_side = "right"
                        stage, reps, feedback = process_pushup_angle(right_shoulder, right_elbow, right_wrist, stage, reps, reps_goal, feedback)
                    else:
                        # If missing landmarks show overlay
                        tracking_overlay(frame)

                elif workout == "Bicep Curls":
                    # Logic to process left, right or both, depending on what is visible
                    if (left_shoulder_landmark.visibility > REQUIRED_VISIBILITY and
                        left_elbow_landmark.visibility > REQUIRED_VISIBILITY and 
                        left_wrist_landmark.visibility > REQUIRED_VISIBILITY
                    ):
                        left_shoulder = [left_shoulder_landmark.x, left_shoulder_landmark.y]
                        left_elbow = [left_elbow_landmark.x, left_elbow_landmark.y]
                        left_wrist = [left_wrist_landmark.x, left_wrist_landmark.y]
                        active_side = "left"
                        stage, reps, feedback = process_bicepcurls_angle(left_shoulder, left_elbow, left_wrist, stage, reps, reps_goal, feedback)

                    if (right_shoulder_landmark.visibility > REQUIRED_VISIBILITY and
                        right_elbow_landmark.visibility > REQUIRED_VISIBILITY and 
                        right_wrist_landmark.visibility > REQUIRED_VISIBILITY
                    ):
                        right_shoulder = [right_shoulder_landmark.x, right_shoulder_landmark.y]
                        right_elbow = [right_elbow_landmark.x, right_elbow_landmark.y]
                        right_wrist = [right_wrist_landmark.x, right_wrist_landmark.y]
                        active_side = "both"
                        stage, reps, feedback = process_bicepcurls_angle(right_shoulder, right_elbow, right_wrist, stage, reps, reps_goal, feedback)
                    else:
                        # If missing landmarks show overlay
                        tracking_overlay(frame)

                elif workout == "Squats":
                    # Logic to process left or right side depending on what is most visible
                    if (
                        left_hip_landmark.visibility > REQUIRED_VISIBILITY and
                        left_knee_landmark.visibility > REQUIRED_VISIBILITY and
                        left_ankle_landmark.visibility > REQUIRED_VISIBILITY
                    ):
                        hip = [left_hip_landmark.x, left_hip_landmark.y]
                        knee = [left_knee_landmark.x,left_knee_landmark.y] 
                        ankle = [left_ankle_landmark.x,left_ankle_landmark.y]
                        active_side = "left"
                        stage, reps, feedback = process_squat_angle(hip, knee, ankle, stage, reps, reps_goal, feedback)
                     
                    elif(
                        right_hip_landmark.visibility > REQUIRED_VISIBILITY and
                        right_knee_landmark.visibility > REQUIRED_VISIBILITY and
                        right_ankle_landmark.visibility > REQUIRED_VISIBILITY
                    ):
                        hip = [right_hip_landmark.x, right_hip_landmark.y]
                        knee = [right_knee_landmark.x, right_knee_landmark.y]
                        ankle = [right_ankle_landmark.x, right_ankle_landmark.y]    
                        active_side = "right"
                        stage, reps, feedback = process_squat_angle(hip, knee, ankle, stage, reps, reps_goal, feedback)
                    
                    else:
                       # If missing landmarks show overlay
                       tracking_overlay(frame)
                    

                elif workout == "Lateral Raises":
                    # Logic to process left, right or both sides depending on what is most visible
                    if (
                        left_hip_landmark.visibility > REQUIRED_VISIBILITY and
                        left_shoulder_landmark.visibility > REQUIRED_VISIBILITY and
                        left_wrist_landmark.visibility > REQUIRED_VISIBILITY
                    ):
                        hip = [left_hip_landmark.x,left_hip_landmark.y]
                        shoulder = [left_shoulder_landmark.x, left_shoulder_landmark.y]
                        wrist = [left_wrist_landmark.x, left_wrist_landmark.y]
                        active_side = "left"
                        stage, reps, feedback = process_laterals_angle(hip, shoulder, wrist, stage, reps, reps_goal, feedback)
                        
                    if (
                        right_hip_landmark.visibility > REQUIRED_VISIBILITY and
                        right_shoulder_landmark.visibility > REQUIRED_VISIBILITY and
                        right_wrist_landmark.visibility > REQUIRED_VISIBILITY
                    ):
                        hip = [right_hip_landmark.x, right_hip_landmark.y]
                        shoulder = [right_shoulder_landmark.x, right_shoulder_landmark.y]
                        wrist = [right_wrist_landmark.x, right_wrist_landmark.y]
                        active_side = "both"
                        stage, reps, feedback = process_laterals_angle(hip, shoulder, wrist, stage, reps, reps_goal, feedback)

                    else:
                       # Feedback for missing landmarks
                       tracking_overlay(frame)
                
                # Update Progress Bar
                progress.progress(min(reps / reps_goal, 1.0))

                # Get frame dimensions
                frame_height, frame_width, _ = frame.shape
                rect_width, rect_height = 300, 150
                rect_x = frame_width - rect_width
                rect_y = frame_height - rect_height

                # Draw the rectangle + reps_count and sets_count
                cv2.rectangle(frame, (rect_x, rect_y), (rect_x + rect_width, rect_y + rect_height), (245, 117, 16), -1)
                cv2.putText(frame, f"REPS: {reps}", (rect_x + 20, rect_y + 60), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2, cv2.LINE_AA)
                cv2.putText(frame, f"SETS: {sets}", (rect_x + 20, rect_y + 120), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2, cv2.LINE_AA)

                # Recalculate rectangle x to create new rectangle
                rect_x = (frame_width - rect_width) // 2
                rect_y = 10 

                # If there is feedback, create a red rectangle
                if feedback:
                    rect_color = (0, 0, 255)  # RED
                    cv2.rectangle(frame, (rect_x, rect_y), (rect_x + rect_width, rect_y + rect_height), rect_color, -1)
                
                    (text_width, text_height), baseline = cv2.getTextSize(f" {feedback}", cv2.FONT_HERSHEY_SIMPLEX, 1, 3)
                    text_x = rect_x + (rect_width - text_width) // 2
                    text_y = rect_y + (rect_height + text_height) // 2
                    cv2.putText(frame, f" {feedback}", (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 3, cv2.LINE_AA)
            else:
                tracking_overlay(frame)
            # Draw landmarks on frame
            mp_drawing.draw_landmarks_custom(
                frame, 
                results.pose_landmarks, 
                mp_pose.POSE_CONNECTIONS,  
                mp_drawing.DrawingSpec(color=(39, 21, 234), thickness=20, circle_radius=10),  # Connection lines
                mp_drawing.DrawingSpec(color=(234, 145, 21), thickness=10, circle_radius=3), active_side, workout) # 

            # Create a thin black border using cv2
            frame_with_border = cv2.copyMakeBorder(frame, 5, 5, 5, 5, cv2.BORDER_CONSTANT, value=(0,0,0))

            # Image = generated frame with border
            FRAME_WINDOW.image(frame_with_border, channels="BGR")

    cap.release()
    