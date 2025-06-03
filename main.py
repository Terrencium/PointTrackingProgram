import cv2
import numpy as np
import matplotlib.pyplot as plt
import csv
import os

# Global state
clicked_points = []
frame_index = 0
positions = []
current_frame = None
start_frame = 0
end_frame = None

CSV_EXPORT_PATH = "C:/Users/TZYan/OneDrive/Desktop/PhysicsCProjectVideos"

def click_event(event, x, y, flags, param):
    global clicked_points, current_frame, frame_index
    if event == cv2.EVENT_LBUTTONDOWN:
        clicked_points.append((x, y))
        print(f"Point on frame {frame_index}: ({x}, {y})")
        # Draw circle on clicked point
        cv2.circle(current_frame, (x, y), 5, (0, 0, 255), -1)
        cv2.imshow("Video", current_frame)
        positions.append((frame_index, (x, y)))

def compute_transform_matrix(scale_points_pixel, scale_points_real):
    scale_points_pixel = np.array(scale_points_pixel, dtype=np.float32)
    scale_points_real = np.array(scale_points_real, dtype=np.float32)
    matrix, _ = cv2.findHomography(scale_points_pixel, scale_points_real)
    return matrix

def apply_perspective_transform(matrix, pixel_points):
    points = np.array(pixel_points, dtype=np.float32).reshape(-1, 1, 2)
    transformed = cv2.perspectiveTransform(points, matrix)
    return [tuple(pt[0]) for pt in transformed]

def export_to_csv(data, filepath):
    with open(filepath, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Frame', 'X (relative)', 'Y (relative)'])
        for row in data:
            writer.writerow(row)
    print(f"Coordinates exported to {os.path.abspath(filepath)}")

def main(video_path):
    global frame_index, current_frame, clicked_points, start_frame, end_frame

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error opening video file")
        return

    print("Define at least 4 calibration points in the first frame.")
    print("These will be used to correct perspective and establish scale.")
    print("Define their real-world coordinates (e.g., in meters).")

    # Load the first frame for calibration
    ret, frame = cap.read()
    if not ret:
        print("Failed to read video.")
        return

    current_frame = frame.copy()
    cv2.imshow("Video", current_frame)
    cv2.setMouseCallback("Video", click_event)
    print("Click on at least 4 known reference points in the image...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    if len(clicked_points) < 4:
        print("Need at least 4 reference points for homography.")
        return

    print("Now enter the real-world coordinates (x, y) for the reference points.")
    scale_points_real = []
    for i, pt in enumerate(clicked_points):
        val = input(f"Real-world coordinates for point {i+1} (format: x,y): ")
        x, y = map(float, val.strip().split(","))
        scale_points_real.append((x, y))

    homography_matrix = compute_transform_matrix(clicked_points, scale_points_real)

    # Ask user for frame range
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    start_frame = int(input(f"Enter start frame (0 to {total_frames - 1}): "))
    end_frame = int(input(f"Enter end frame ({start_frame} to {total_frames - 1}): "))

    print("\nNow the calibration is done. Proceed to mark marble position in each frame.")
    print("Use arrow keys: left/right to navigate frames, space to select a point.")

    clicked_points = []
    positions.clear()
    frame_index = start_frame

    while start_frame <= frame_index <= end_frame:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ret, frame = cap.read()
        if not ret:
            break

        current_frame = frame.copy()
        cv2.imshow("Video", current_frame)
        cv2.setMouseCallback("Video", click_event)

        key = cv2.waitKey(0) & 0xFF

        if key == 81:  # Left arrow key
            frame_index = max(start_frame, frame_index - 2)
            print("Moving to frame" + str(frame_index))
        elif key == 83:  # Right arrow key
            frame_index = min(end_frame, frame_index + 2)
            print("Moving to frame" + str(frame_index))
        elif key == 32:  # Space key to confirm a point
            print("Point registered for this frame.")
            frame_index = min(end_frame, frame_index + 2)
            print("Moving to frame" + str(frame_index))
        elif key == 27:  # ESC key to exit
            break

    cv2.destroyAllWindows()

    marble_pixel_positions = [pos[1] for pos in positions]
    marble_coords = apply_perspective_transform(homography_matrix, marble_pixel_positions)

    print("\nMarble coordinates in real-world units:")
    origin = marble_coords[0]
    export_data = []
    for i, coord in enumerate(marble_coords):
        x_rel = coord[0] - origin[0]
        y_rel = coord[1] - origin[1]
        print(f"{positions[i][0]},{x_rel},{y_rel}")
        export_data.append([positions[i][0], round(x_rel, 2), round(y_rel, 2)])

    export_to_csv(export_data, CSV_EXPORT_PATH)

if __name__ == "__main__":
    video_path = input("Enter path to .mov video file: ").strip()
    main(video_path)
