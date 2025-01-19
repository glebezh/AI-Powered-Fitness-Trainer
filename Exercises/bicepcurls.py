from Utilities.calculate_angle import calculate_angle
import streamlit as st

# Function to process angle of bicep curls
def process_bicepcurls_angle(hip, shoulder, wrist, stage, reps, reps_goal, feedback):

    bicepcurl_angle = calculate_angle(hip, shoulder, wrist)
    if bicepcurl_angle > 150:
        stage = "up"
        feedback = ""
    elif 20 <= bicepcurl_angle <= 60 and stage == "up":
        feedback = "CURL ALL THE WAY UP"
    elif bicepcurl_angle < 20 and stage == "up":
        stage = "Down"
        feedback = ""
        reps += 1
        if reps == reps_goal:
            st.balloons()

    return stage, reps, feedback