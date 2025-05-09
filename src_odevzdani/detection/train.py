from ultralytics import YOLO

model = YOLO("yolo11m.pt")

model.train(data = "F:\\datasets\\dataset\\dataset_beetle.yaml", imgsz = 640, 
            batch = 8, epochs = 100, workers = 0, device = 0, max_det = 2000)
