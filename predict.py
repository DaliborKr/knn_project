from ultralytics import YOLO

model = YOLO("runs\\detect\\train7\\weights\\last.pt")
#model = YOLO("yolo11m.pt")

model.predict(source = "d1_02_209.jpg", save=True, show_labels = False)
#model.predict(source = "F:\\datasets\\dataset2\\train\\images\\d1_01_550.jpg", save=True, show_labels = False)