import os
import shutil
from laganga_bot.publish.image_processor import process_deal_image

def test_image_processing():
    # 1. Setup paths
    # Assuming this script is in /tests and the image is also in /tests
    base_dir = os.path.dirname(os.path.abspath(__file__))
    source_image = os.path.join(base_dir, "imagen-test.jpg")
    
    # Output file in the current working directory (project root usually)
    output_image = "test_result.jpg" 

    if not os.path.exists(source_image):
        print(f"Error: Source image not found at {source_image}")
        return

    # 2. Copy source to output to avoid overwriting original
    print(f"Copying {source_image} -> {output_image}...")
    shutil.copy(source_image, output_image)

    # 3. Process it
    print("Processing image with 50% discount...")
    process_deal_image(output_image, 50)
    
    print(f"Done! Check the file '{output_image}' to see the result.")

if __name__ == "__main__":
    test_image_processing()
