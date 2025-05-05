import os
import json

# Set the frame dimensions according to your video resolution
FRAME_WIDTH = 1920   # Replace with actual frame width
FRAME_HEIGHT = 1304   # Replace with actual frame height

def load_data(folder_path):
    data = {}
    for filename in os.listdir(folder_path):
        if filename.endswith('.txt'):
            # Extract frame number from the filename
            parts = filename.split('_')
            frame_part = parts[-1].split('.')[0]
            if not frame_part.isdigit():
                continue  # Skip files with non-numeric frame parts
            frame_number = int(frame_part) - 1 
            
            # Read the file content
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r') as file:
                lines = file.readlines()
            
            # Initialize frame entry if not exists
            if frame_number not in data:
                data[frame_number] = {}
            
            for line in lines:
                parts = line.strip().split()
                if len(parts) != 6:
                    continue  # Skip invalid lines
                try:
                    # Parse the bounding box data
                    _, x_center, z_center, width, height, box_id = parts
                    x_center = float(x_center)
                    z_center = float(z_center)
                    width = float(width)
                    height = float(height)
                    box_id = box_id  # Keep as string to match JSON keys in example
                except ValueError:
                    continue  # Skip lines with invalid numbers
                
                # Convert normalized coordinates to pixel values
                left = (x_center - width / 2) * FRAME_WIDTH
                right = (x_center + width / 2) * FRAME_WIDTH
                top = (z_center - height / 2) * FRAME_HEIGHT
                bottom = (z_center + height / 2) * FRAME_HEIGHT
                
                # Prepare the bounding box coordinates
                bbox = [
                    float(left),
                    float(top),
                    float(right),
                    float(bottom)
                ]
                
                # Add to the data structure
                if box_id not in data[frame_number]:
                    data[frame_number][box_id] = []
                data[frame_number][box_id].append(bbox)
    
    return data

# Example usage
folder_path = 'F:\\boxmot\\runs\\track\\exp19\\labels'  # Replace with your folder path
output_json = load_data(folder_path)

# Convert to JSON string
json_output = json.dumps(output_json, indent=4)

# Save to a file or print
#print(json_output)
# To save to a file:
with open('tracking_results\\boxmot-boosttrack.json', 'w') as f:
    f.write(json_output)