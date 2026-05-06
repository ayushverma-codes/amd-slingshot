import streamlit as st
from PIL import Image
import io
import vertexai
from vertexai.generative_models import GenerativeModel, Part

# Initialize Vertex AI 
# Note: On GCP Cloud Run, this automatically picks up your Project ID and region 
# from the attached service account. 
# Initialize Vertex AI with explicit project and location
try:
    # Hardcoding the exact project ID ensures Vertex AI doesn't get lost
    vertexai.init(
        project="nice-theater-495508-q0", 
        location="us-central1"
    )
    # Using the fully qualified, stable model version name
    model = GenerativeModel("gemini-1.5-flash-001") 
except Exception as e:
    st.error(f"Failed to initialize Vertex AI. Error: {e}")

# Streamlit UI Configuration
st.set_page_config(page_title="NutriLens", page_icon="🥗", layout="centered")

st.title("🥗 NutriLens: AI Dietician")
st.write("Upload a menu or meal photo, tell me your goal, and get an instant nutritional breakdown.")

# User Inputs
uploaded_file = st.file_uploader("Upload Image (Restaurant Menu or Plate of Food)", type=["jpg", "jpeg", "png"])
dietary_goal = st.text_input("Dietary Goal or Restrictions", placeholder="e.g., High protein, under 600 calories, vegetarian")

# Processing Block
# Processing Block
if st.button("Analyze Meal"):
    if uploaded_file is not None and dietary_goal:
        with st.spinner("Analyzing with Gemini 1.5 Flash..."):
            try:
                # 1. Display the uploaded image directly (No PIL needed!)
                st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
                
                # 2. Extract raw bytes directly for Vertex AI
                image_part = Part.from_data(
                    uploaded_file.getvalue(), 
                    mime_type=uploaded_file.type  # Automatically grabs 'image/jpeg', 'image/png', etc.
                )

                # 3. Construct the System Prompt
                system_prompt = f"""
                You are an expert, highly analytical dietician. Analyze the attached image of a food item or restaurant menu. 
                Based on the user's stated goal: "{dietary_goal}", complete the following:
                1. Identify the best option(s) for them.
                2. Estimate the macronutrients (Protein, Carbs, Fats) and total calories.
                3. Briefly explain why this fits their goal.
                If it is a menu, pick the best dish. If it is a plate of food, analyze what is on the plate. Format your response cleanly using Markdown.
                """

                # 4. Generate the response from Vertex AI
                response = model.generate_content([image_part, system_prompt])
                
                # 5. Output the results
                st.success("Analysis Complete!")
                st.markdown("### 📋 Nutritional Breakdown & Recommendation")
                st.markdown(response.text)

            except Exception as e:
                st.error(f"An error occurred during analysis: {e}")
    else:
        st.warning("Please upload an image and enter a dietary goal before analyzing.")