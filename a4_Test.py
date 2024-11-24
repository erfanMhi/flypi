import cv2
import numpy as np

def debug_print(title, data):
    print(f"=== {title} ===")
    print(data)
    print("\n")

def order_points(pts):
    """
    Orders points in the following order:
    top-left, top-right, bottom-right, bottom-left
    """
    rect = np.zeros((4, 2), dtype="float32")

    # Sum and difference to find top-left and bottom-right
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]       # Top-left has the smallest sum
    rect[2] = pts[np.argmax(s)]       # Bottom-right has the largest sum

    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]    # Top-right has the smallest difference
    rect[3] = pts[np.argmax(diff)]    # Bottom-left has the largest difference

    return rect

def four_point_transform(image, pts):
    """
    Performs a perspective transform to obtain a top-down view of the image.
    """
    rect = order_points(pts)
    (tl, tr, br, bl) = rect

    # Compute the width of the new image
    widthA = np.linalg.norm(br - bl)
    widthB = np.linalg.norm(tr - tl)
    maxWidth = max(int(widthA), int(widthB))

    # Compute the height of the new image
    heightA = np.linalg.norm(tr - br)
    heightB = np.linalg.norm(tl - bl)
    maxHeight = max(int(heightA), int(heightB))

    # Destination points for the top-down view
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]
    ], dtype="float32")

    # Compute the perspective transform matrix
    M = cv2.getPerspectiveTransform(rect, dst)
    # Apply the perspective transform
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

    return warped

def main():
    # Path to the input image
    image_path = 'image.png'  # Replace with your image path

    # Load the image
    image = cv2.imread(image_path)

    # Check if image was loaded successfully
    if image is None:
        print("Error: Image not found or unable to load.")
        return

    debug_print("Original Image Shape", f"Height: {image.shape[0]}, Width: {image.shape[1]}, Channels: {image.shape[2]}")

    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    debug_print("Grayscale Image Stats", f"Mean: {np.mean(gray):.2f}, Std Dev: {np.std(gray):.2f}")

    # Apply a Gaussian blur to reduce noise and improve edge detection
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    debug_print("Blurred Image Stats", f"Mean: {np.mean(blurred):.2f}, Std Dev: {np.std(blurred):.2f}")

    # Perform Canny edge detection
    lower_threshold = 75
    upper_threshold = 200
    edged = cv2.Canny(blurred, lower_threshold, upper_threshold)
    edge_pixels = cv2.countNonZero(edged)
    debug_print("Canny Edge Detection", f"Lower Threshold: {lower_threshold}, Upper Threshold: {upper_threshold}, Edge Pixels Detected: {edge_pixels}")

    # Find contours in the edged image
    contours, hierarchy = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    debug_print("Contours Found", f"Total Contours Detected: {len(contours)}")

    # Sort the contours based on area, in descending order
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    # Initialize the screen contour (the A4 paper)
    screen_contour = None

    # Loop over the contours to find the one that approximates the A4 paper
    for i, contour in enumerate(contours):
        area = cv2.contourArea(contour)
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
        num_vertices = len(approx)

        # Compute the bounding rectangle to check the aspect ratio
        x, y, w, h = cv2.boundingRect(approx)
        aspect_ratio = float(w) / h if h != 0 else 0

        debug_print(f"Contour #{i}", f"Area: {area:.2f}, Perimeter: {peri:.2f}, Approx Vertices: {num_vertices}, Aspect Ratio: {aspect_ratio:.3f}")

        # If the approximated contour has four points, it might be the paper
        if num_vertices == 4:
            # A4 paper aspect ratio is approximately 0.707 (width/height)
            # Allow some tolerance for detection, considering possible rotation
            if 0.65 < aspect_ratio < 0.88:
                screen_contour = approx
                debug_print(f"Selected Contour #{i}", f"Aspect Ratio within range (0.65 - 0.88)")
                break
            else:
                debug_print(f"Contour #{i} Skipped", f"Aspect Ratio {aspect_ratio:.3f} not within range (0.65 - 0.88)")

    # Check if the paper was found
    if screen_contour is None:
        print("A4 paper not found in the image.")
    else:
        # Draw the contours on the original image (optional: save the image)
        output_image = image.copy()
        cv2.drawContours(output_image, [screen_contour], -1, (0, 0, 255), 3)

        # Print the corner points
        print("The corners of the A4 paper are:")
        for idx, point in enumerate(screen_contour):
            corner = tuple(point[0])
            print(f"Corner {idx + 1}: {corner}")

        # Optionally, save the output image with detected contour
        output_contour_path = 'a4_paper_detected.jpg'
        cv2.imwrite(output_contour_path, output_image)
        print(f"\nOutput image with detected A4 paper saved as '{output_contour_path}'.")

        # Perform the perspective transform to obtain the cropped A4 paper
        warped = four_point_transform(image, screen_contour.reshape(4, 2))

        # Optionally, save the cropped image
        cropped_output_path = 'a4_paper_cropped.jpg'
        cv2.imwrite(cropped_output_path, warped)
        print(f"Cropped A4 paper image saved as '{cropped_output_path}'.")

        # Optionally, print the shape of the cropped image
        debug_print("Cropped Image Shape", f"Height: {warped.shape[0]}, Width: {warped.shape[1]}, Channels: {warped.shape[2]}")

if __name__ == "__main__":
        main()
