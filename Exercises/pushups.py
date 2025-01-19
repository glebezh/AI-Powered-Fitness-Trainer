from Utilities.calculate_angle import calculate_angle
import streamlit as st

# Function to process the pushup angle
def process_pushup_angle(hip, shoulder, wrist, stage, reps, reps_goal, feedback):

    pushup_angle = calculate_angle(hip, shoulder, wrist)
    if pushup_angle > 160:
        stage = "up"
        feedback = ""
    elif 40 <= pushup_angle <= 50 and stage == "up":
        feedback = "LOWER YOUR CHEST"
    elif pushup_angle < 40 and stage == "up":
        stage = "Down"
        feedback = ""
        reps += 1
        if reps == reps_goal:
            st.balloons() 
            
    return stage, reps, feedback