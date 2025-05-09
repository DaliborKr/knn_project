from ultralytics import YOLO

# Load a model
model = YOLO("runs\\detect\\train19\\weights\\best.pt")  # load a custom model

# Validate the model
metrics = model.val(data = "F:\\datasets\\datasetTest\\dataset_beetle.yaml", imgsz = 1920, 
                    batch = 8, epochs = 100, workers = 0, device = 0, plots = True, max_det = 1000)
metrics.box.map  # map50-95
metrics.box.map50  # map50
metrics.box.map75  # map75
metrics.box.maps  # a list contains map50-95 of each category