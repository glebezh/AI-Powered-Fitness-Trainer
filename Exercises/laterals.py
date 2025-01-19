from Utilities.calculate_angle import calculate_angle
import streamlit as st

# Function to process angle of lateral raises
def process_laterals_angle(hip, shoulder, wrist, stage, reps, reps_goal, feedback):
    
    lateral_angle = calculate_angle(hip, shoulder, wrist)
    if lateral_angle > 90:
        stage = "up"
        feedback = ""
    elif 60 <= lateral_angle <= 100 and stage == "up":
        feedback = "RAISE YOUR ARMS HIGHER"
    elif lateral_angle < 20 and stage == "up":
        feedback = ""
        stage = "Down"
        reps += 1
        if reps == reps_goal:
            st.balloons()

    return stage, reps, feedback