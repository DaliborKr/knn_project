from ultralytics import YOLO

model = YOLO("yolo11m.pt")

model.train(data = "dataset_beetle.yaml", imgsz = 640, 
            batch = 8, epochs = 100, workers = 1, device = 0)