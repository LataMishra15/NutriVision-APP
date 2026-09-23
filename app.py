import gradio as gr
from PIL import Image
import torch
from transformers import CLIPProcessor, CLIPModel
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

# Load model
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

# Food labels
food_labels = ["pizza", "burger", "pasta", "salad", "rice", "dal", "paneer"]

# Dataset
data = {
    "name": ["pizza", "burger", "pasta", "salad", "rice", "dal", "paneer"],
    "calories": [266, 295, 220, 150, 200, 180, 265],
    "protein": [11, 17, 8, 5, 4, 9, 14],
    "carbs": [33, 30, 43, 10, 45, 25, 6]
}

df = pd.DataFrame(data)

def analyze(image):
    image = Image.open(image)

    inputs = processor(text=food_labels, images=image, return_tensors="pt", padding=True)
    outputs = model(**inputs)
    probs = outputs.logits_per_image.softmax(dim=1)

    food = food_labels[probs.argmax().item()]

    item = df[df["name"] == food].iloc[0]

    nutrition = f"""
Calories: {item['calories']}
Protein: {item['protein']}g
Carbs: {item['carbs']}g
"""

    # Recommendation
    vec = df[["calories", "protein", "carbs"]]
    sim = cosine_similarity([item[["calories", "protein", "carbs"]]], vec)[0]
    df["sim"] = sim
    recs = df.sort_values("sim", ascending=False)["name"].iloc[1:4].tolist()

    return food, nutrition, ", ".join(recs)

gr.Interface(
    fn=analyze,
    inputs=gr.Image(type="filepath"),
    outputs=["text", "text", "text"],
    title="🍽️ Free Food AI App"
).launch()