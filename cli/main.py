import os
import sys
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from langgraph_pipeline import graph

def get_receipt_images(directory="images_test/"):
    """Fetch all image files from the given directory."""
    return [
        os.path.join(directory, f) for f in os.listdir(directory)
        if f.endswith((".jpg", ".png"))
    ]

if __name__ == "__main__":
    # Fetch receipt images
    receipt_images = get_receipt_images()

    if not receipt_images:
        print("No images found in the 'images/' folder.")
    else:
        # Run LangGraph pipeline with receipts
        state = {"receipt_paths": receipt_images}
        result = graph.invoke(state)

        # Print structured OCR output
        print(json.dumps(result["extracted_receipts"], indent=4))

