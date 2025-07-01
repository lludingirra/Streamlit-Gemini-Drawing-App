# AI-Powered Hand Drawing Tool

This project is an interactive application that allows users to draw on a virtual canvas using hand gestures and then process these drawings with a Generative AI model (Google Gemini). It combines real-time hand tracking with a Streamlit web interface for a seamless user experience. This tool enables the AI to perform operations and generate text responses based on anything you draw (e.g., math problems, shapes, diagrams, etc.).

## Features

* **Hand Gesture Drawing:** Draw freehand on a virtual canvas using your index finger.
* **Canvas Clearing:** Clear the entire drawing canvas with a specific hand gesture (thumb up).
* **AI Integration:** Send your drawing to a Google Generative AI model (e.g., Gemini-2.0-Flash) with a distinct hand gesture (all fingers up except pinky). This allows the AI to analyze, explain, or process **anything you draw**.
* **Real-time Interaction:** Live webcam feed overlaid with your drawings.
* **Streamlit Web Interface:** A user-friendly web application built with Streamlit for easy control and display.
* **Configurable API Key:** Integrates with Google Generative AI via an API key (security considerations are important).

## Prerequisites

To run this project, you need:

* Python (3.8 or higher recommended).
* A webcam connected to your computer.
* **A Google Generative AI API Key:** You'll need an API key to use Google's AI models. Obtain one from [Google AI Studio](https://aistudio.google.com/app/apikey).
* `MathGestures.png` image in the project root directory.

## Installation

1.  **Clone or Download the Repository:**
    Get the project files to your local machine.

2.  **Install Required Libraries:**
    Open your terminal or command prompt, navigate to the project directory, and run the following command:
    ```bash
    pip install opencv-python cvzone numpy google-generativeai pillow streamlit
    ```

## Usage

1.  **Set Your Google Generative AI API Key:**
    * **Crucial Step:** Open `main.py`.
    * Locate the line `client = genai.Client(api_key="YOUR_API_KEY_HERE")`.
    * Replace `"YOUR_API_KEY_HERE"` with your actual Google Generative AI API key.
    * **Security Note:** For production applications or public repositories, it is **highly recommended** to use Streamlit's secrets management (`st.secrets`) or environment variables to store your API key instead of hardcoding it directly in the script.

2.  **Run the Streamlit Application:**
    Open your terminal or command prompt, navigate to the project directory, and execute:
    ```bash
    streamlit run main.py
    ```

3.  **Interact in Your Browser:**
    * A web browser tab will automatically open, displaying the Streamlit application.
    * **Ensure Webcam Access:** Your browser might ask for permission to access your webcam. Grant permission.
    * **Drawing Mode:** Extend only your **index finger** to draw on the virtual canvas. A magenta line will follow your finger's movement.
    * **Clear Canvas:** Extend only your **thumb** to clear the entire drawing canvas. The canvas will turn black.
    * **Send to AI:** Extend **all fingers except your pinky** (i.e., thumb, index, middle, ring fingers up, pinky down). This gesture will capture the current drawing on the canvas and send it to the Google Generative AI model.
    * **AI Response:** The AI's text response will appear in the "Answer" section on the right side of the Streamlit interface.

## How It Works

1.  **Streamlit UI:** The application is built using Streamlit, providing a web-based interface with a live video feed, a "Run" checkbox, and an area for AI responses.
2.  **Webcam & Hand Tracking:**
    * The webcam continuously captures video frames.
    * `cvzone.HandDetector` tracks a single hand, providing landmark positions and identifying which fingers are up.
3.  **Drawing Logic (`draw` function):**
    * If only the index finger is extended, the script draws a line on a transparent `canvas` (a `numpy` array initialized with zeros) from the `prev_pos` to the `current_pos` (index finger tip).
    * If only the thumb is extended, the `canvas` is reset to a completely black image, effectively clearing the drawing.
4.  **AI Integration (`sendToAI` function):**
    * When the "send to AI" gesture (all fingers up except pinky) is detected, a snapshot of the current `canvas` is taken.
    * This `numpy` image is converted to a PIL (Pillow) image and sent to the specified Google Generative AI model (`gemini-2.0-flash`) along with a text prompt. **Here, you can customize the prompt to specify what kind of operation you want the AI to perform on your drawing.** For example, you could use a prompt like `contents=["Solve this math equation", pil_image]` instead of `contents=["Analyze the drawing and provide a text response.", pil_image]`, or `contents=["Describe this object", pil_image]`, `contents=["Identify elements in this diagram", pil_image]`, or any other instruction relevant to your drawing.
    * The AI's text response is then retrieved and displayed in the Streamlit UI. A flag (`ai_request_sent`) prevents continuous re-sending during the gesture.
5.  **Image Composition:** The live webcam feed (`img`) and the drawing `canvas` are blended together using `cv2.addWeighted` to create a composite image, which is then displayed in the Streamlit interface.

## Customization

* **API Key:** Remember to secure your API key.
* **AI Model & Prompt:** You can change the `model` (e.g., to `gemini-pro-vision` or other available models) and the `contents` prompt in the `sendToAI` function to alter the AI's behavior and what you ask it to do with your drawings. For example, you could set `contents=["Solve this math equation", pil_image]` for math problems, or `contents=["Describe the object in the drawing", pil_image]` for object descriptions.
* **Drawing Color/Thickness:** Modify the color `(255, 0, 255)` and thickness `10` in `cv2.line` within the `draw` function.
* **Gesture Definitions:** Adjust the `fingers == [...]` conditions in `draw` and `sendToAI` to change the gestures for drawing, clearing, or sending to AI.
* **UI Layout:** Modify `st.columns` and image/text positions in Streamlit to customize the app's appearance.
* **`MathGestures.png`:** Replace this with your own branding or a relevant image.

## Troubleshooting

* **"Error occurred during AI request":**
    * Check your internet connection.
    * Verify your Google Generative AI API key is correct and active.
    * Ensure you have enabled the `gemini-2.0-flash` model (or whichever model you choose) in your Google Cloud Project.
    * The AI might refuse to generate content based on the prompt or image. Try simpler prompts.
* **Webcam not detected/working:**
    * Ensure your webcam is connected and not in use by another application, and its drivers are installed correctly.
    * Check browser permissions for webcam access.
    * Try changing `cv2.VideoCapture(0)` to `1` or higher.
* **No hand detection:** Adjust `detectionCon` and `minTrackCon` in `HandDetector` if hand detection is inconsistent. Ensure good lighting.
* **Streamlit not displaying:** Check your terminal for errors. Ensure you ran `streamlit run main.py`.
