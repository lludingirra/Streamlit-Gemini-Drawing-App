import cv2 # Import the OpenCV library for image and video processing.
from cvzone.HandTrackingModule import HandDetector # Import HandDetector from cvzone for hand detection and tracking.
import numpy as np # Import numpy for numerical operations and array manipulation.
from google import genai # Import the Google Generative AI client library.
from PIL import Image # Import Pillow (PIL) for image manipulation, specifically for converting OpenCV to PIL image.
import streamlit as st # Import Streamlit for creating web applications/UIs.

# --- Streamlit UI Setup ---
st.set_page_config(layout="wide") # Set the Streamlit page layout to wide mode.
st.image("MathGestures.png") # Display an image at the top of the Streamlit app. (Make sure this image exists!)

col1, col2 = st.columns([2,1]) # Create two columns in the Streamlit layout: left (2 parts wide) and right (1 part wide).
with col1 :
    run = st.checkbox('Run', value=True) # Create a checkbox to control if the video processing loop runs. Default is True.
    FRAME_WINDOW = st.image([]) # Placeholder for the live video feed. This will be updated continuously.
    
with col2 :
    output_text_area = st.title("Answer") # Display a title "Answer" in the right column.
    output_text_area = st.subheader("") # Placeholder for displaying AI response text.

# --- Google Generative AI Client Initialization ---
# Initialize the Google Generative AI client with your API key.
# IMPORTANT: Replace "AIzaSyAb-tifXtvfy_AadPt36JaWHAWyJkko23o" with your actual API key.
# It's highly recommended not to hardcode API keys directly in public repositories.
# Consider using Streamlit secrets (st.secrets) or environment variables for production.
client = genai.Client(api_key="AIzaSyAb-tifXtvfy_AadPt36JaWHAWyJkko23o")

# --- Webcam Setup ---
cap = cv2.VideoCapture(0) # Initialize video capture from the default webcam (index 0).
cap.set(3, 1280) # Set the width of the captured video frame to 1280 pixels.
cap.set(4, 720) # Set the height of the captured video frame to 720 pixels.

# --- Hand Detector Initialization ---
detector = HandDetector(staticMode=False, # Continuous tracking, not static image mode.
                        maxHands=1,      # Detects a maximum of one hand.
                        modelComplexity=1, # Complexity of the hand landmark model.
                        detectionCon=0.7,  # Minimum confidence for hand detection.
                        minTrackCon=0.5)   # Minimum confidence for hand tracking.

def getHandInfo(img):
    """
    Detects hands in the image and extracts information about finger states and landmarks.

    Args:
        img (np.ndarray): The input image frame from the camera.

    Returns:
        tuple (list, list) or None:
            - fingers1 (list): List of 0s and 1s indicating which fingers are up.
            - lmList1 (list): List of landmark coordinates for the detected hand.
            Returns None if no hand is detected.
    """
    # Detect hands in the image. draw=True will draw landmarks on 'img'. flipType=True flips hand internally for detection.
    hands, img = detector.findHands(img, draw=True, flipType=True)

    if hands: # If a hand is detected:
        hand1 = hands[0] # Get the first detected hand.
        lmList1 = hand1["lmList"] # Get the list of landmark coordinates.
        fingers1 = detector.fingersUp(hand1) # Get the status of each finger (up or down).
        return fingers1, lmList1 # Return finger status and landmark list.
    else:
        return None # Return None if no hand is detected.

def draw(info, prev_pos, canvas):
    """
    Draws on the canvas based on hand gestures (index finger for drawing, thumb for clearing).

    Args:
        info (tuple): Tuple containing finger status and landmark list (from getHandInfo).
        prev_pos (tuple): Previous position of the drawing point (index finger tip).
        canvas (np.ndarray): The drawing canvas image.

    Returns:
        tuple (tuple, np.ndarray):
            - current_pos (tuple): Current position of the drawing point.
            - canvas (np.ndarray): The updated drawing canvas.
    """
    if info is None: # If no hand info, no drawing.
        return None, canvas

    fingers1, lmList1 = info # Unpack finger status and landmark list.
    current_pos = None # Initialize current position.

    # Drawing Mode: If only the index finger is up ([0, 1, 0, 0, 0] represents fingersUp status).
    if fingers1 == [0, 1, 0, 0, 0]:
        current_pos = lmList1[8][0:2] # Get the coordinates of the index finger tip (landmark 8).

        if prev_pos is None: # If this is the first point in a new stroke.
            prev_pos = current_pos # Set previous position to current position.
        cv2.line(canvas, prev_pos, current_pos, (255, 0, 255), 10) # Draw a line on the canvas (magenta, thickness 10).
        
    # Clear Canvas Mode: If only the thumb is up ([1, 0, 0, 0, 0]).
    elif fingers1 == [1, 0, 0, 0, 0]:
        canvas = np.zeros_like(img) # Create a new, black (empty) canvas of the same size as the image.
    
    return current_pos, canvas # Return current position and updated canvas.

def sendToAI(fingers, canvas_image):
    """
    Sends the drawn image to a Generative AI model for processing if a specific gesture is made.

    Args:
        fingers (list): List of finger states.
        canvas_image (np.ndarray): The image drawn on the canvas.

    Returns:
        str: The response text from the AI, or an error message.
    """
    # AI Send Gesture: If all fingers except the pinky are up ([1, 1, 1, 1, 0]).
    if fingers == [1, 1, 1, 1, 0]:
        rgb_canvas = cv2.cvtColor(canvas_image, cv2.COLOR_BGR2RGB) # Convert canvas from BGR to RGB (PIL likes RGB).
        pil_image = Image.fromarray(rgb_canvas) # Convert NumPy array (OpenCV image) to PIL Image.
        
        try:
            # --- CUSTOMIZE AI OPERATION HERE ---
            # The prompt to the AI determines what kind of operation it will perform on your drawing.
            # You can change "Analyze the drawing" to:
            # - "Solve this math problem" (if you draw math equations)
            # - "Describe the object" (if you draw an object)
            # - "Convert this sketch into a concept"
            # - "Identify elements in this diagram"
            # - Or any other instruction relevant to your drawing!
            # The AI model ("gemini-2.0-flash") can also be changed to other available models
            # like "gemini-pro-vision" for more detailed visual understanding tasks.
            
            response = client.models.generate_content(
                contents=[
                    "Analyze the drawing and provide a text response.", # Generic prompt
                    pil_image # This is the image input.
                ],
                model="gemini-2.0-flash" # Specify the AI model to use.
            )
            
            return response.text # Return the text response from the AI.
        
        except Exception as e: # Catch any errors during AI request.
            return f"Error occurred during AI request: {e}" # Return an error message.
    return None # Return None if the AI send gesture is not made.

prev_pos = None # Stores the previous drawing point, initialized to None.
canvas = None # The drawing canvas, initialized to None.
output_text = None # Stores the AI's response text, initialized to None.
ai_request_sent = False # Flag to prevent sending multiple AI requests for a single gesture.

# --- Main Application Loop ---
while run: # Loop continues as long as the 'Run' checkbox in Streamlit is checked.
    success, img = cap.read() # Read a frame from the webcam.
    if not success:
        print("Camera could not be read.") # Error message if camera fails.
        break # Exit the loop.
    img = cv2.flip(img, 1) # Flip the image horizontally for mirror effect.

    if canvas is None: # Initialize canvas if it's the first frame.
        canvas = np.zeros_like(img, dtype=np.uint8) # Create a black canvas of the same dimensions as the image.

    info = getHandInfo(img) # Get hand information (finger status, landmarks).

    if info: # If hand is detected:
        fingers, lmList = info # Unpack hand info.
        prev_pos, canvas = draw(info, prev_pos, canvas) # Perform drawing action on canvas.

        # Check for AI send gesture.
        if fingers == [1, 1, 1, 1, 0] and not ai_request_sent: # If AI gesture and request not already sent.
            output_text = sendToAI(fingers, canvas.copy()) # Send canvas image to AI. Use .copy() to send a snapshot.
            ai_request_sent = True # Set flag to prevent re-sending.
        elif fingers != [1, 1, 1, 1, 0]: # If AI gesture is not active, reset the flag.
            ai_request_sent = False
    else: # If no hand is detected:
        prev_pos = None # Reset previous position (stop drawing a line).
        ai_request_sent = False # Reset AI request flag.

    # Combine the live camera feed and the drawing canvas.
    # img is weighted 0.7, canvas 0.3 for a translucent effect.
    image_combined = cv2.addWeighted(img, 0.7, canvas, 0.3, 0)
    
    # Update the Streamlit image widget with the combined image.
    FRAME_WINDOW.image(image_combined, channels="BGR")
    
    # If there's AI output, update the Streamlit text area.
    if output_text:
        output_text_area.subheader(output_text) # Use subheader to display AI text.

    # Check for 'q' key press to break the loop (useful for local running, less for Streamlit).
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# --- Resource Release ---
cap.release() # Release the webcam object.
cv2.destroyAllWindows() # Close all OpenCV windows.
