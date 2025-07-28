import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
from PIL import Image
from google.api_core.exceptions import ResourceExhausted

# Load environment variables
load_dotenv()
genai.configure(api_key="Your API key here")

# Compress image before sending to reduce input size
def compress_image(image, max_size=(512, 512)):
    image = image.convert("RGB")
    image.thumbnail(max_size)
    return image

# Handle Gemini API interaction
def get_gemini_response(input_prompt, uploaded_file):
    for model_name in ['gemini-1.5-pro', 'gemini-1.5-flash']:
        try:
            model = genai.GenerativeModel(model_name)
            image = compress_image(Image.open(uploaded_file))
            response = model.generate_content([input_prompt, image])
            return f"🧠 Model used: {model_name}\n\n" + response.text

        except ResourceExhausted as e:
            continue  # Try next model if quota exceeded
        except Exception as e:
            return "❌ Unexpected error:\n" + str(e)

    return "⚠️ Gemini API quota exceeded for all available models. Please wait and try again later."

# Streamlit UI
st.set_page_config(page_title="Calories Advisor App")
st.header("🍱 Calories Advisor App")

uploaded_file = st.file_uploader("📷 Upload a food image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_container_width=True)  # updated from deprecated `use_column_width`

submit = st.button("🍽️ Analyze My Meal")

# Optimized prompt
input_prompt = """
You are a nutritionist. Analyze the food in the image and list:
- Food items with estimated calories.
- Whether the meal is healthy or not.
- Nutrient % split: carbs, fats, fiber, sugar, protein.
- Suggest healthy alternatives if needed.
"""

# Handle submit
if submit and uploaded_file:
    with st.spinner("🔍 Analyzing image..."):
        result = get_gemini_response(input_prompt, uploaded_file)
        st.success("✅ Analysis Complete!")
        st.subheader("📋 Nutrition Report")
        st.write(result)

