from Utilities.calculate_angle import calculate_angle
import streamlit as st

# Function to process squat angle
def process_squat_angle(hip, knee, ankle, stage, reps, reps_goal, feedback):

    squat_angle = calculate_angle(hip, knee, ankle)
    if squat_angle > 170:
        stage = "up"
        feedback = ""
    elif 95 <= squat_angle <= 140 and stage == "up":
        feedback = "LOWER YOUR HIPS" 
    elif squat_angle < 95 and (stage == "up"):
        stage = "Down"
        feedback = ""
        reps += 1
        if reps == reps_goal:
            st.balloons()

    return stage, reps, feedback