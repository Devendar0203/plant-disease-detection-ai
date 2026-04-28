import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import matplotlib.pyplot as plt
import os
import numpy as np

# --- 1. Constants and Paths ---
# This path MUST match the folder you unzipped and moved
DATA_DIR = 'plantvillage dataset/color' 
IMAGE_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS = 10 # 10 is fast. You can increase this later for better accuracy.

# Check if data directory exists
if not os.path.exists(DATA_DIR):
    print(f"Error: Data directory not found at {DATA_DIR}")
    print("Please make sure you have the 'plantvillage dataset' folder in your project.")
else:
    NUM_CLASSES = len(os.listdir(DATA_DIR))
    print(f"Found {NUM_CLASSES} classes in {DATA_DIR}")

    # --- 2. Load Data and Apply Augmentation ---
    datagen = ImageDataGenerator(
        rescale=1./255,
        validation_split=0.2,       # Split 80% for training, 20% for validation
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        horizontal_flip=True,
        brightness_range=[0.8, 1.2],
        zoom_range=0.2
    )

    # --- 3. Create Data Generators ---
    print("Creating data generators...")
    train_generator = datagen.flow_from_directory(
        DATA_DIR,
        target_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        subset='training'
    )

    validation_generator = datagen.flow_from_directory(
        DATA_DIR,
        target_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        subset='validation',
        shuffle=False
    )

    # --- 4. Save the Class Names (This creates class_names.txt) ---
    class_names = list(train_generator.class_indices.keys())
    print("\nSaving class names...")
    with open('class_names.txt', 'w') as f:
        for item in class_names:
            f.write("%s\n" % item)
    print("Successfully saved 'class_names.txt'")

    # --- 5. Build the Model ---
    print("Building model...")
    base_model = MobileNetV2(
        input_shape=IMAGE_SIZE + (3,),
        include_top=False,
        weights='imagenet'
    )
    base_model.trainable = False # Freeze the base model

    model = models.Sequential([
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.Dropout(0.5),
        layers.Dense(NUM_CLASSES, activation='softmax')
    ])

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    model.summary()

    # --- 6. Train the Model ---
    print("\nStarting model training...")
    history = model.fit(
        train_generator,
        steps_per_epoch=train_generator.samples // BATCH_SIZE,
        validation_data=validation_generator,
        validation_steps=validation_generator.samples // BATCH_SIZE,
        epochs=EPOCHS
    )
    print("Training complete.")

    # --- 7. Save the Trained Model (This creates plant_disease_model.keras) ---
    model.save('plant_disease_model.keras')
    print("\nSuccessfully saved 'plant_disease_model.keras'")
    print("You can now run the Streamlit app!")