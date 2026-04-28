import streamlit as st
import numpy as np
import cv2
from PIL import Image
import io
import os

# --- 1. Page Configuration ---
st.set_page_config(
    page_title="Plant Disease Detector",
    page_icon="🌿",
    layout="wide"
)

# --- 2. NEW UI/UX: Simplified CSS for Animation and Readability ---
def inject_custom_css():
    """Injects all custom CSS for animations and text styling."""
    st.markdown(
         f"""
         <style>
         /* Style headers */
         h1, h2, h3 {{
             color: #115E3A; /* Dark green for headers */
         }}
         
         /* --- Animation CSS --- */
         @keyframes fadeInZoom {{
             0% {{ opacity: 0; transform: scale(0.8); filter: blur(3px); }}
             100% {{ opacity: 1; transform: scale(1); filter: blur(0px); }}
         }}
         
         .animated-welcome {{
             text-align: center;
             animation: fadeInZoom 1.5s ease-out;
             padding-top: 5rem;
             padding-bottom: 5rem;
         }}
         
         .animated-welcome h1 {{
             font-size: 3.5rem !important;
             color: #115E3A;
         }}
         .welcome-text {{
             text-align: center;
             font-size: 1.1rem;
             color: #333;
         }}
         </style>
         """,
         unsafe_allow_html=True
     )

inject_custom_css()

# --- 3. Actionable Advice Dictionary ---
TREATMENT_SUGGESTIONS = {
    "Apple___Apple_scab": {
        "description": "A fungal disease causing olive-green to black, velvety spots on leaves, fruit, and twigs. Leaves may twist and fall off early.",
        "treatment": (
            "1. **Sanitation:** Rake up and destroy all fallen leaves in the autumn to reduce fungal overwintering.\n"
            "2. **Pruning:** Prune trees to improve air circulation, which helps leaves dry faster.\n"
            "3. **Resistant Varieties:** If planting new trees, choose varieties resistant to apple scab.\n"
            "4. **Fungicides:** Apply fungicides (like myclobutanil or captan) from bud break until dry weather returns."
        )
    },
    "Apple___Black_rot": {
        "description": "A fungal disease. On leaves, it creates 'frog-eye' spots (purple border, tan center). It can also create black, sunken cankers on branches and a firm, black rot on the fruit.",
        "treatment": (
            "1. **Pruning:** Prune out any dead or cankered branches. Remove mummified fruit.\n"
            "2. **Sanitation:** Clean up all fallen fruit and leaves from around the tree.\n"
            "3. **Fungicides:** Apply fungicides during the growing season, especially during wet periods."
        )
    },
    "Apple___Cedar_apple_rust": {
        "description": "A fungal disease that requires both an apple tree and a juniper/cedar tree to survive. It causes bright orange-yellow spots on apple leaves.",
        "treatment": (
            "1. **Remove Host:** Remove any nearby juniper or Eastern red cedar trees (the alternate host).\n"
            "2. **Fungicides:** Apply a preventative fungicide (like myclobutanil) starting at bud break.\n"
            "3. **Resistant Varieties:** Plant apple varieties that are resistant to rust."
        )
    },
    "Apple___healthy": {
        "description": "The leaf appears healthy and free from common diseases.",
        "treatment": (
            "1. **Monitoring:** Continue to monitor for signs of pests or disease.\n"
            "2. **Care:** Ensure proper watering, fertilization, and pruning for good air circulation."
        )
    },
    "Blueberry___healthy": {
        "description": "The leaf appears healthy.",
        "treatment": (
            "1. **Care:** Maintain acidic soil (pH 4.5-5.5).\n"
            "2. **Monitoring:** Mulch to retain moisture and control weeds. Watch for common pests."
        )
    },
    "Cherry_(including_sour)___Powdery_mildew": {
        "description": "A fungal disease that appears as white, powdery patches on the surface of leaves. Leaves may distort and curl.",
        "treatment": (
            "1. **Air Circulation:** Prune trees to improve airflow and reduce humidity.\n"
            "2. **Fungicides:** Apply fungicides (like sulfur, potassium bicarbonate, or myclobutanil) as soon as symptoms appear.\n"
            "3. **Sanitation:** Rake and destroy fallen leaves in the fall."
        )
    },
    "Cherry_(including_sour)___healthy": {
        "description": "The leaf appears healthy.",
        "treatment": (
            "1. **Monitoring:** Watch for common cherry pests like aphids and birds.\n"
            "2. **Care:** Ensure proper watering and fertilization. Prune annually."
        )
    },
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": {
        "description": "A fungal disease. Appears as long, narrow, rectangular, tan-to-gray lesions that run parallel to the leaf veins.",
        "treatment": (
            "1. **Resistant Hybrids:** This is the most effective management. Plant corn hybrids with good resistance ratings.\n"
            "2. **Crop Rotation:** Rotate with non-host crops (like soybeans) to reduce fungal residue in the soil.\n"
            "3. **Tillage:** Burying the crop residue (tillage) can help, but balance this with soil conservation goals."
        )
    },
    "Corn_(maize)___Common_rust_": {
        "description": "A fungal disease. Appears as powdery, brick-red, oval-shaped pustules on both upper and lower leaf surfaces.",
        "treatment": (
            "1. **Resistant Hybrids:** Most sweet corn and field corn hybrids have good resistance.\n"
            "2. **Monitoring:** This disease rarely causes significant yield loss in most hybrids. Treatment is often not economical."
        )
    },
    "Corn_(maize)___Northern_Leaf_Blight": {
        "description": "A fungal disease. Appears as large, elliptical, 'cigar-shaped', grayish-green to tan lesions on the leaves.",
        "treatment": (
            "1. **Resistant Hybrids:** The best method is to plant resistant corn hybrids.\n"
            "2. **Crop Rotation:** Rotate with non-host crops.\n"
            "3. **Tillage:** Burying infected residue can reduce the fungus."
        )
    },
    "Corn_(maize)___healthy": {
        "description": "The leaf appears healthy.",
        "treatment": (
            "1. **Monitoring:** Scout fields regularly for pests (like corn borer) and early signs of disease.\n"
            "2. **Care:** Ensure proper nitrogen fertilization and watering."
        )
    },
    "Grape___Black_rot": {
        "description": "A fungal disease. On leaves, it creates small, reddish-brown, circular spots. On fruit, it creates black, mummified berries.",
        "treatment": (
            "1. **Sanitation:** Remove and destroy all mummified fruit and infected canes during dormant pruning.\n"
            "2. **Fungicides:** Apply preventative fungicides (like mancozeb or captan) from bud break until fruit begins to ripen.\n"
            "3. **Airflow:** Prune vines and manage canopy for good air circulation."
        )
    },
    "Grape___Esca_(Black_Measles)": {
        "description": "A complex fungal disease. Symptoms include 'tiger-stripe' patterns on leaves (interveinal yellowing or reddening) and small, dark spots on berries.",
        "treatment": (
            "1. **Pruning:** Prune late (in spring) during dry weather. Remove and destroy all dead wood.\n"
            "2. **Wound Protection:** Protect large pruning wounds with a sealant or fungicide paint.\n"
            "3. **No Cure:** There is no cure; management focuses on slowing the disease's spread."
        )
    },
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": {
        "description": "A fungal disease. Appears as irregular, dark brown spots on leaves, often with a yellow halo. Can cause leaves to fall off early.",
        "treatment": (
            "1. **Sanitation:** Rake and destroy fallen leaves in the fall.\n"
            "2. **Fungicides:** Standard fungicide programs for Black Rot will also control Leaf Blight."
        )
    },
    "Grape___healthy": {
        "description": "The vine leaf appears healthy.",
        "treatment": (
            "1. **Care:** Requires full sun, good air circulation, and well-drained soil.\n"
            "2. **Pruning:** Prune annually during dormancy to manage canopy and fruit production."
        )
    },
    "Orange___Haunglongbing_(Citrus_greening)": {
        "description": "One of the most serious citrus diseases. Caused by a bacterium and spread by an insect (Asian citrus psyllid). Symptoms include blotchy, mottled, and yellowing leaves.",
        "treatment": (
            "1. **NO CURE:** There is no cure for this disease. Management is about prevention.\n"
            "2. **Remove Infected Trees:** Immediately remove and destroy infected trees to prevent spread.\n"
            "3. **Insect Control:** Control the Asian citrus psyllid insect with insecticides.\n"
            "4. **Use Certified Trees:** Plant only certified, disease-free nursery trees."
        )
    },
    "Peach___Bacterial_spot": {
        "description": "A bacterial disease. Causes small, water-soaked spots on leaves that turn purple-black, then fall out, leaving a 'shot-hole' appearance. Also causes spots on fruit.",
        "treatment": (
            "1. **Resistant Varieties:** Plant varieties with resistance to bacterial spot.\n"
            "2. **Dormant Sprays:** Apply copper-based bactericides during the dormant season.\n"
            "3. **Pruning:** Prune for good airflow to help leaves dry quickly."
        )
    },
    "Peach___healthy": {
        "description": "The leaf appears healthy.",
        "treatment": (
            "1. **Monitoring:** Watch for common pests like peach tree borer and plum curculio.\n"
            "2. **Pruning:** Prune annually to maintain an open, V-shape (open center) for best sun and airflow."
        )
    },
    "Pepper,_bell___Bacterial_spot": {
        "description": "A bacterial disease. Appears as small, dark, water-soaked spots on leaves that may turn brown with a light center. Fruit can also develop raised, scab-like spots.",
        "treatment": (
            "1. **Use Clean Seed:** Use certified, disease-free seed and transplants.\n"
            "2. **Crop Rotation:** Do not plant peppers or tomatoes in the same soil for at least one year.\n"
            "3. **Copper Sprays:** Apply copper-based bactericides as a preventative measure."
        )
    },
    "Pepper,_bell___healthy": {
        "description": "The leaf appears healthy.",
        "treatment": (
            "1. **Care:** Requires full sun and well-drained soil. Avoid over-watering.\n"
            "2. **Monitoring:** Watch for pests like aphids and hornworms."
        )
    },
    "Potato___Early_blight": {
        "description": "A fungal disease. Appears as dark, circular spots with a 'target' or 'bulls-eye' pattern, usually on older leaves first.",
        "treatment": (
            "1. **Crop Rotation:** Do not plant potatoes or tomatoes in the same spot for at least two years.\n"
            "2. **Sanitation:** Remove and destroy infected plant debris at the end of the season.\n"
            "3. **Fungicides:** Apply fungicides (like chlorothalonil or mancozeb) preventatively."
        )
    },
    "Potato___Late_blight": {
        "description": "A highly destructive fungal disease. Appears as large, dark, water-soaked blotches on leaves that can quickly kill the plant. A white, fuzzy mold may appear on the underside.",
        "treatment": (
            "1. **Certified Seed:** Plant only certified, disease-free potato seed.\n"
            "2. **Airflow:** Ensure good spacing between plants for air circulation.\n"
            "3. **Fungicides:** Apply preventative fungicides, especially during cool, moist weather. This disease spreads very fast."
        )
    },
    "Potato___healthy": {
        "description": "The leaf appears healthy.",
        "treatment": (
            "1. **Monitoring:** Regularly check for common pests like the Colorado potato beetle.\n"
            "2. **Hilling:** Ensure plants are 'hilled' (soil piled up around the stem) to protect tubers from sunlight."
        )
    },
    "Raspberry___healthy": {
        "description": "The leaf appears healthy.",
        "treatment": (
            "1. **Pruning:** Prune annually to remove old canes that have fruited.\n"
            "2. **Support:** Provide a trellis or support system for the canes.\n"
            "3. **Care:** Requires well-drained soil and good air circulation."
        )
    },
    "Soybean___healthy": {
        "description": "The leaf appears healthy.",
        "treatment": (
            "1. **Monitoring:** Scout for common pests like soybean aphids and bean leaf beetles.\n"
            "2. **Crop Rotation:** Rotate with non-host crops (like corn) to maintain soil health and reduce disease pressure."
        )
    },
    "Squash___Powdery_mildew": {
        "description": "A fungal disease. Appears as white, powdery spots on the upper surfaces of leaves. Can eventually cover the entire leaf.",
        "treatment": (
            "1. **Air Circulation:** Provide ample spacing between plants.\n"
            "2. **Fungicides:** Apply fungicides (like neem oil, sulfur, or potassium bicarbonate) at the first sign of disease.\n"
            "3. **Watering:** Water at the base of the plant, not on the leaves."
        )
    },
    "Strawberry___Leaf_scorch": {
        "description": "A fungal disease. Appears as small, irregular, purplish-to-brown blotches on leaves. As they grow, the centers turn brown, and the leaf looks 'scorched'.",
        "treatment": (
            "1. **Sanitation:** Remove and destroy old, infected leaves after harvest and in the fall.\n"
            "2. **Resistant Varieties:** Plant varieties that are resistant to leaf scorch.\n"
            "3. **Fungicides:** Apply fungicides if the disease is severe."
        )
    },
    "Strawberry___healthy": {
        "description": "The leaf appears healthy.",
        "treatment": (
            "1. **Care:** Plant in full sun in well-drained soil. Refresh plants every few years.\n"
            "2. **Mulch:** Use straw mulch to keep fruit clean and retain soil moisture."
        )
    },
    "Tomato___Bacterial_spot": {
        "description": "This disease is caused by bacteria. It appears as small, dark, water-soaked spots on leaves.",
        "treatment": (
            "1. **Remove Infected Plants:** Immediately remove and destroy infected leaves.\n"
            "2. **Apply Copper Fungicide:** Spray with a copper-based bactericide.\n"
            "3. **Improve Airflow:** Prune plants to improve air circulation.\n"
            "4. **Avoid Overhead Watering:** Water at the base of the plant."
        )
    },
    "Tomato___Early_blight": {
        "description": "A fungal disease (same family as Potato Early Blight). Causes dark 'target' spots on older leaves, leading to yellowing and leaf drop.",
        "treatment": (
            "1. **Sanitation:** Remove and destroy lower, infected leaves. Clean up garden debris in the fall.\n"
            "2. **Mulch:** Apply mulch to prevent fungal spores from splashing from the soil onto the leaves.\n"
            "3. **Fungicides:** Apply fungicides (like chlorothalonil or copper) preventatively."
        )
    },
    "Tomato___Late_blight": {
        "description": "A highly destructive fungal disease (same as Potato Late Blight). Appears as large, dark, water-soaked blotches on leaves that can quickly kill the plant.",
        "treatment": (
            "1. **Immediate Action:** Remove and destroy all infected plants (do not compost).\n"
            "2. **Airflow:** Ensure good spacing and pruning for air circulation.\n"
            "3. **Fungicides:** Apply preventative fungicides, especially during cool, moist weather."
        )
    },
    "Tomato___Leaf_Mold": {
        "description": "A fungal disease common in high humidity. Appears as pale green or yellow spots on the upper leaf, with a gray or purplish mold on the underside.",
        "treatment": (
            "1. **Lower Humidity:** This is key. Improve air circulation via pruning and spacing. Water in the morning.\n"
            "2. **Sanitation:** Remove and destroy infected leaves.\n"
            "3. **Fungicides:** Apply a fungicide if necessary."
        )
    },
    "Tomato___Septoria_leaf_spot": {
        "description": "A fungal disease. Appears as many small, circular spots with dark borders and tan or gray centers. Black dots (pycnidia) are visible in the center.",
        "treatment": (
            "1. **Sanitation:** Remove and destroy infected leaves (this is very important).\n"
            "2. **Crop Rotation:** Rotate tomatoes to a different garden spot each year.\n"
            "3. **Fungicides:** Apply fungicides (like chlorothalonil or copper) to protect new leaves."
        )
    },
    "Tomato___Spider_mites Two-spotted_spider_mite": {
        "description": "A pest, not a disease. Tiny (not insects) spider mites suck plant juices, causing tiny yellow or white speckles (stippling) on leaves. Fine webbing may be visible.",
        "treatment": (
            "1. **Water Spray:** A strong blast of water from a hose can knock many mites off.\n"
            "2. **Insecticidal Soap/Neem Oil:** Spray plants thoroughly, especially the undersides of leaves.\n"
            "3. **Miticides:** If infestation is severe, use a specific miticide."
        )
    },
    "Tomato___Target_Spot": {
        "description": "A fungal disease. Causes small, dark spots with concentric rings (like Early Blight, but spots are smaller and have a dark center).",
        "treatment": (
            "1. **Airflow:** Prune and stake plants to improve air circulation.\n"
            "2. **Sanitation:** Remove infected leaves and garden debris.\n"
            "3. **Fungicides:** Apply preventative fungicides."
        )
    },
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": {
        "description": "A virus spread by whiteflies. Symptoms include severe stunting of the plant, and new leaves that are small, curled upward, and yellow at the margins.",
        "treatment": (
            "1. **NO CURE:** There is no cure for this virus.\n"
            "2. **Remove Infected Plants:** Immediately remove and destroy infected plants to stop the source.\n"
            "3. **Insect Control:** Control whiteflies with insecticidal soap or neem oil.\n"
            "4. **Use Resistant Varieties:** Plant tomato varieties labeled as 'TYLCV-resistant'."
        )
    },
    "Tomato___Tomato_mosaic_virus": {
        "description": "A virus that is easily spread by touch (hands, tools). Causes a light and dark green mosaic or mottle pattern on leaves. Leaves may be stunted or fern-like.",
        "treatment": (
            "1. **NO CURE:** There is no cure for this virus.\n"
            "2. **Remove Infected Plants:** Immediately remove and destroy infected plants.\n"
            "3. **Sanitation:** Wash hands and tools thoroughly with soap and water after handling any tomato plant.\n"
            "4. **Use Resistant Varieties:** Plant varieties labeled as 'ToMV-resistant'."
        )
    },
    "Tomato___healthy": {
        "description": "The leaf appears healthy and free of common diseases.",
        "treatment": (
            "1. **Keep Monitoring:** Continue to check plants regularly for pests and diseases.\n"
            "2. **Proper Care:** Ensure consistent watering, full sun, and balanced fertilizer."
        )
    }
}

# --- 5. Model and Class Loading Function ---
@st.cache_resource
def load_model_and_classes():
    """Builds the model structure and loads the saved weights."""
    try:
        IMAGE_SIZE = (224, 224)
        
        if not os.path.exists('class_names.txt'):
             st.error("Error: class_names.txt not found in the directory.")
             return None, None
             
        with open('class_names.txt', 'r') as f:
            class_names = [line.strip() for line in f.readlines()]
        NUM_CLASSES = len(class_names)

        base_model = tf.keras.applications.MobileNetV2(
            input_shape=IMAGE_SIZE + (3,),
            include_top=False,
            weights='imagenet'
        )
        base_model.trainable = False 

        model = tf.keras.models.Sequential([
            base_model,
            tf.keras.layers.GlobalAveragePooling2D(),
            tf.keras.layers.Dropout(0.5),
            tf.keras.layers.Dense(NUM_CLASSES, activation='softmax')
        ], name="plant_disease_model") 

        weights_path = 'plant_disease_model_weights.weights.h5'
        if not os.path.exists(weights_path):
             st.error(f"Error: Weights file not found: {weights_path}")
             return None, class_names 

        model.load_weights(weights_path)
        return model, class_names

    except Exception as e:
        st.error(f"Error building model or loading weights: {e}")
        return None, None


# --- Load the model and classes ---
model, class_names = load_model_and_classes()


# --- 6. Image Preprocessing Function ---
def preprocess_image(image_bytes):
    """Preprocesses the uploaded image for the model."""
    try:
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        image_np = np.array(image)
        resized_image = cv2.resize(image_np, (224, 224))
        # Important: Verify if your model was trained with 0-1 scaling (MobileNetV2 usually expects this if you didn't use tf.keras.applications.mobilenet_v2.preprocess_input)
        normalized_image = resized_image / 255.0
        batched_image = np.expand_dims(normalized_image, axis=0)
        return batched_image
    except Exception as e:
        st.error(f"Error preprocessing image: {e}")
        return None

# --- 7. Sidebar: Upload or Capture ---
with st.sidebar:
    st.header("📸 Image Source")

    upload_choice = st.radio(
        "Select Input Method:",
        ("Upload from File", "Capture from Camera"),
        label_visibility="collapsed"
    )

    if upload_choice == "Upload from File":
        uploaded_file = st.file_uploader("Choose a plant leaf image...", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
        captured_image = None
    else:
        captured_image = st.camera_input("Take a photo of the plant leaf", label_visibility="collapsed")
        uploaded_file = None
    
    st.markdown("---")
    st.header("ℹ️ About This Project")
    st.info(
        """
        This application is an end-to-end AI project that uses a **Deep Learning model (MobileNetV2)**, 
        trained on the public PlantVillage dataset, to identify 38 plant diseases.

        **How to use:**
        1️⃣ **Upload or Capture:** Use the options above to provide a clear image of a plant leaf.
        2️⃣ **Analyze:** The AI model will analyze the image to find patterns.
        3️⃣ **Diagnose:** View the predicted disease, confidence score, and detailed treatment advice.

        **Developed by:**
        B. Devendar Naidu
        """
    )

# --- 8. Process Selected Image ---
image_source = uploaded_file or captured_image

if image_source is not None:
    # --- This is the RESULTS page ---
    st.title("🌿 Plant Disease Detection AI")
    st.write("Here is the analysis of your plant leaf.")
    
    # Read bytes once to avoid stream cursor issues
    image_bytes = image_source.getvalue()
    image = Image.open(io.BytesIO(image_bytes))
    
    # Corrected Columns: 20% left, 60% center, 20% right
    col1, col2, col3 = st.columns([0.2, 0.6, 0.2]) 
    with col2:
        st.image(image, caption="🖼️ Uploaded Image", use_container_width=True) 

    # Only attempt prediction if the model actually loaded
    if model is None or class_names is None:
         st.error("⚠️ The AI model or class definitions are missing. Please make sure `plant_disease_model_weights.weights.h5` and `class_names.txt` are in the folder.")
    else:
        with st.spinner('🔍 Analyzing the image... Please wait.'):
            processed_image = preprocess_image(image_bytes)

            if processed_image is not None:
                try:
                    # --- 9. Prediction ---
                    prediction = model.predict(processed_image)
                    predicted_index = int(np.argmax(prediction[0]))
                    confidence = float(np.max(prediction[0]))
                    predicted_class_name = class_names[predicted_index]
                    display_name = predicted_class_name.replace('___', ' ').replace('_', ' ')

                    # --- 10. Confidence Guardrail ---
                    CONFIDENCE_THRESHOLD = 0.5  # 50%

                    if confidence < CONFIDENCE_THRESHOLD:
                        st.error(f"**I'm not confident in this prediction (Confidence: {confidence*100:.2f}%)**")
                        st.warning("This may not be a plant leaf. Please upload a clear, close-up image.")
                    else:
                        # --- 11. Organized Results Display ---
                        st.header("✅ Analysis Results")
                        # Smaller columns for metrics
                        res_col1, res_col2 = st.columns([2, 1])
                        with res_col1:
                            st.success(f"**Prediction:** {display_name}")
                        with res_col2:
                            st.metric("Confidence", f"{confidence*100:.2f}%")

                        # Show Description & Treatment
                        advice = TREATMENT_SUGGESTIONS.get(predicted_class_name)
                        if advice:
                            tab1, tab2 = st.tabs(["📝 Description", "💊 Suggested Treatment"])
                            with tab1:
                                st.write(advice["description"])
                            with tab2:
                                st.info(advice["treatment"]) 
                        else:
                            st.info(f"No specific treatment data found for **{display_name}**. Please ensure your class_names.txt matches the dictionary keys exactly.")

                except Exception as e:
                    st.error(f"An error occurred during prediction: {e}")

else:
    # --- 12. This is the WELCOME page ---
    st.markdown(
        """
        <div class="animated-welcome">
            <h1>🌿 Welcome to the <br> Plant Disease Detection AI</h1>
            <p class="welcome-text">
                Use the sidebar on the left to upload an image or take a photo of a plant leaf to begin.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
