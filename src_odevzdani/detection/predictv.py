import cv2
from ultralytics import YOLO

# Load model
model = YOLO("runs\\detect\\train19\\weights\\best.pt")

# Read image with OpenCV
img = cv2.imread("d1_02_209.jpg")

# Convert to RGB (YOLO expects RGB format)
img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

# Run prediction
results = model.predict(img_rgb, conf=0.5, iou=0.4, max_det=1000, imgsz=1920)

# Extract results
for result in results:
    for box in result.boxes:
        # Get box coordinates (xyxy format)
        x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
        
        # Get confidence score and class ID
        confidence = box.conf.item()
        class_id = int(box.cls.item())
        
        # Draw bounding box
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        # Optional: Add label and confidence
        label = f"{model.model.names[class_id]}: {confidence:.2f}"
        cv2.putText(img, label, (x1, y1 - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

# Show results with OpenCV
cv2.imshow('YOLO Detection', img)
cv2.waitKey(0)
cv2.destroyAllWindows()