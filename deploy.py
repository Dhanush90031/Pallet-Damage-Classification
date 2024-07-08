import streamlit as st
import numpy as np
import cv2
from keras.models import load_model
from datetime import datetime
import mysql.connector

# Create 'history' table if it doesn't exist
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Dhanush2000",
    database="pallet"
)
cursor = connection.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS history (
        id INT AUTO_INCREMENT PRIMARY KEY,
        TIMESTAMP DATETIME,
        IMAGE_PATH TEXT,
        CLASS_LABEL TEXT
    )
''')

connection.commit()
cursor.close()
connection.close()

# Load the trained model
model = load_model(r"C:\Users\Asus\Downloads\cnnmodel.h5")

# Define categories
CATEGORIES = ['dismantle', 'good', 'repair']

# Function to preprocess and classify the uploaded image
def classify_image(image):
    image = cv2.resize(image, (244, 244))
    image = image.reshape(-1, 244, 244, 3) / 255.0
    prediction = model.predict(image)
    class_index = np.argmax(prediction)
    CLASS_LABEL = CATEGORIES[class_index]
    confidence = prediction[0][class_index]
    return CLASS_LABEL, confidence

# Function to save browsing history to the MySQL database
def save_to_database(images, CLASS_LABEL):
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Dhanush2000",
        database="pallet"
    )
    cursor = connection.cursor()

    TIMESTAMP = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    for image in images:
        insert_query = "INSERT INTO history (TIMESTAMP, IMAGE_PATH, CLASS_LABEL) VALUES (%s, %s, %s)"
        insert_values = (TIMESTAMP, 'uploaded_image.jpg', CLASS_LABEL)
        cursor.execute(insert_query, insert_values)
        connection.commit()
    
    cursor.close()
    connection.close()


# Streamlit app
def main():
    st.title("Image Classification App")  # Set the title at the top
    st.write("Upload one or more images and let the model classify them!")

    uploaded_files = st.file_uploader("Choose image(s)...", type=["jpg", "png", "jpeg"], accept_multiple_files=True)

    if uploaded_files:
        for i, uploaded_file in enumerate(uploaded_files):
            image = cv2.imdecode(np.fromstring(uploaded_file.read(), np.uint8), 1)
            st.image(image, caption='Uploaded Image', use_column_width=True)

            if st.button(f"Classify {i}"):  # Add a unique identifier to the button label
                CLASS_LABEL, confidence = classify_image(image)
                st.write(f"Prediction: {CLASS_LABEL}")
                st.write(f"Confidence: {confidence:.2f}")

                # Save to MySQL database
                save_to_database([image], CLASS_LABEL)

        # Display browsing history
        st.header("Browsing History")
        
    
    # Retrieve history from MySQL and format it
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Dhanush2000",
        database="pallet"
    )
    cursor = connection.cursor()
    cursor.execute("SELECT TIMESTAMP, IMAGE_PATH, CLASS_LABEL FROM history")
    history_data = cursor.fetchall()
    connection.close()
    
    # Convert the timestamp to a more readable format
    formatted_history_data = []
    for row in history_data:
        # Modify this line to handle datetime objects correctly
        formatted_time = row[0].strftime('%Y-%m-%d %I:%M %p')
        formatted_history_data.append((formatted_time, row[1], row[2]))

    st.table(formatted_history_data)

if __name__ == '__main__':
    main()


