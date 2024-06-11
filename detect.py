from ultralytics import YOLO
import cv2
import os
import sys
import logging

logging.basicConfig(level=logging.DEBUG)

def main():
    print("in main")
    model_path = 'models/train-yolov8-n-100/weights/best.pt'
    model = YOLO(model_path)
    logging.info(f'Loaded model from {model_path}')

    if len(sys.argv) < 5:
        logging.error("Insufficient arguments")
        sys.exit(1)

    source = sys.argv[2]
    output_path = sys.argv[4]

    logging.info(f'Source: {source}')
    logging.info(f'Output Path: {output_path}')

    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        logging.error(f"Error opening video stream or file: {source}")
        sys.exit(1)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, 20.0, (int(cap.get(3)), int(cap.get(4))))
    if not out.isOpened():
        logging.error(f"Error opening video writer for {output_path}")
        sys.exit(1)

    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            results = model.predict(frame)
            annotated_frame = results[0].plot()
            out.write(annotated_frame)
        else:
            break

    cap.release()
    out.release()
    # cv2.destroyAllWindows()
    logging.info(f'Processed video saved to {output_path}')

if __name__ == "__main__":
    main()
