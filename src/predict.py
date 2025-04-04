from ultralytics import YOLO

model = YOLO("runs/detect/train17/weights/best.pt")
#model = YOLO("yolo11m.pt")

model.predict(source = "images/d1_02_208.jpg", save=True, show_labels = False, max_det=1000, conf=0.50, iou=0.4, imgsz = 1920,augment=False)
#model.predict(source = "F:\\datasets\\dataset2\\train\\images\\d1_01_550.jpg", save=True, show_labels = False)