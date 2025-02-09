import streamlit as st
from PIL import Image
import requests
import sys
import subprocess
import pkg_resources
import google.generativeai as genai
import os

try:
    if 'GEMINI_API_KEY' in st.secrets:
        genai.configure(api_key=st.secrets['GEMINI_API_KEY'])
except:
    if 'GEMINI_API_KEY' in os.environ:
        genai.configure(api_key=os.environ['GEMINI_API_KEY'])



generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

gemini_model = genai.GenerativeModel(
  model_name="gemini-1.5-flash-8b",
  generation_config=generation_config,
  system_instruction="You are an AI assistant for an image generation model. Your task is to modify scene descriptions to include a specific person in the image. Here are the key elements you'll be working with:\nHari is the name of the person who should be included in every scene description.\nYour goal is to modify the user's input to create a new scene description that includes Hari as an active participant in the scene. Follow these guidelines:\n\n1. Analyze the original input to understand the scene.\n2. If Hari is not already mentioned, add them to the scene.\n3. Choose an appropriate action or position for Hari that fits naturally within the described setting.\n4. Ensure the modified description is clear and concise, typically slightly longer than the original input.\n5. Maintain the essence of the original scene while integrating Hari.\n6. Make sure the scene doesn't involve covering Hari's face or is facing away from the perspective\n Limit the output to 50 words",
)


def check_install_packages():
    required_packages = ['replicate']
    installed_packages = [pkg.key for pkg in pkg_resources.working_set]
    
    for package in required_packages:
        if package not in installed_packages:
            st.error(f"Package '{package}' is not installed. Installing now...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                st.success(f"Successfully installed {package}")
                st.info("Please restart the Streamlit app")
                st.stop()
            except Exception as e:
                st.error(f"Failed to install {package}: {str(e)}")
                st.stop()

check_install_packages()

try:
    import replicate
except ImportError as e:
    st.error(f"Error importing replicate: {str(e)}")
    st.info("Please try installing replicate manually in your terminal:")
    st.code("pip install replicate")
    st.stop()

# Configure Replicate client
try:
    if 'REPLICATE_API_TOKEN' in st.secrets:
        replicate_client = replicate.Client(api_token=st.secrets['REPLICATE_API_TOKEN'])
except:
    if 'REPLICATE_API_TOKEN' in os.environ:
        replicate_client = replicate.Client(api_token=os.environ['REPLICATE_API_TOKEN'])
    else:
        st.error("REPLICATE_API_TOKEN not found in environment variables or secrets")
        st.stop()

def get_image_from_url(url):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        image = Image.open(response.raw)
        return image
    except Exception as e:
        st.error(f"Error loading image from URL: {str(e)}")
        return None

def generate_images(prompt, num_steps=28, guidance_scale=7.5, model="dev", num_outputs=4):
    try:
        output = replicate.run(
            "harikrishnad1997/flux-1-hari-ft:37b22168a51d814b49bc8629cca6caaa6789a8a7b65cdd5123310fe5a5c5fecc",
            input={
                "prompt": prompt,
                "num_inference_steps": num_steps,
                "guidance_scale": guidance_scale,
                "model": model,
                "num_outputs": num_outputs,
            }
        )
        return output
    except Exception as e:
        st.error(f"Error generating images: {str(e)}")
        return None

def main():
    st.title("Hari's Image Generation App")
    st.write("This app will output AI Images created with Hari in them")
    
    # Input prompt
    prompt = st.text_input("Enter your prompt:", 
                          "Winning the Italian GP as a Ferrari Driver")
    # Advanced settings in an expander
    with st.expander("Advanced Settings"):
        num_steps = st.slider("Number of Inference Steps", 1, 50, 28)
        guidance_scale = st.slider("Guidance Scale", 1.0, 20.0, 7.5)
        num_outputs = st.slider("Number of Outputs", 1, 4, 2)
        model = st.selectbox("Model", ["dev","schnell"])

    # Generate button
    if st.button("Generate Images"):
        if prompt:
            with st.spinner("Generating images..."):
                chat_session = gemini_model.start_chat(
                    history=[
                    ]
                    )

                final_prompt = chat_session.send_message(prompt)
                
                st.markdown(f"Final prompt: {final_prompt.text}")

                outputs = generate_images(
                    final_prompt.text,
                    num_steps,
                    guidance_scale,
                    model,
                    num_outputs
                )
                
                if outputs:
                    cols = st.columns(2)
                    for idx, image_url in enumerate(outputs):
                        with cols[idx % 2]:
                            image = get_image_from_url(image_url)
                            if image:
                                st.image(image, caption=f"Generated Image {idx+1}")
                                st.markdown(f"[Download Image]({image_url})")
        else:
            st.warning("Please enter a prompt first!")

if __name__ == "__main__":
    main()
