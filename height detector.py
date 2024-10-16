import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk


reference_image = None
person_image = None
reference_height = None

def load_reference_image(canvas):

    global reference_image
    file_path = filedialog.askopenfilename()
    if file_path:
        reference_image = cv2.imread(file_path)
        display_image(reference_image, canvas)

def load_person_image(canvas):

    global person_image
    file_path = filedialog.askopenfilename()
    if file_path:
        person_image = cv2.imread(file_path)
        display_image(person_image, canvas)

def display_image(image, canvas):

    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = Image.fromarray(image)
    image = image.resize((300, 400), Image.LANCZOS)
    photo = ImageTk.PhotoImage(image=image)
    canvas.create_image(0, 0, anchor=tk.NW, image=photo)
    canvas.image = photo

def preprocess_image(image):

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) # grayscale
    
    blurred = cv2.GaussianBlur(gray, (5, 5), 0) # Gaussian blur
    
    edges = cv2.Canny(blurred, 50, 150) # Canny edge detection
    
    return gray, edges

def find_top_bottom_edges(edges):
    
    y_coords, x_coords = np.nonzero(edges)
    
    if len(y_coords) == 0:
        return None, None
    
    top_y = np.min(y_coords)
    bottom_y = np.max(y_coords)
    
    top_x = x_coords[np.argmin(y_coords)]
    bottom_x = x_coords[np.argmax(y_coords)]

    return (top_x, top_y), (bottom_x, bottom_y)

def calculate_height(reference_canvas, person_canvas, reference_height_var):
    
    global reference_image, person_image, reference_height

    if reference_image is None or person_image is None:
        messagebox.showerror("Error", "Please load both images first.")
        return

    reference_height = reference_height_var.get()

    if not reference_height:
        messagebox.showerror("Error", "Please enter the reference height.")
        return

    # preprocessing grayscale + edges
    ref_gray, ref_edges = preprocess_image(reference_image)
    person_gray, person_edges = preprocess_image(person_image)

    ref_top, ref_bottom = find_top_bottom_edges(ref_edges)
    person_top, person_bottom = find_top_bottom_edges(person_edges)

    if ref_top is None or person_top is None:
        messagebox.showerror("Error", "Could not detect person or reference object in one or both images.")
        return

    # calculate the pixel height of the reference and person
    ref_pixel_height = ref_bottom[1] - ref_top[1]
    person_pixel_height = person_bottom[1] - person_top[1]

    # pixel height to actual height
    pixels_per_cm = ref_pixel_height / reference_height
    person_height_cm = person_pixel_height / pixels_per_cm

    mark_edges(reference_image, ref_top, ref_bottom, reference_canvas)
    mark_edges(person_image, person_top, person_bottom, person_canvas)

    messagebox.showinfo("Result", f"Estimated height: {person_height_cm:.2f} cm")

def mark_edges(image, top, bottom, canvas):  #2 red circles, 1 at top most edge and 1 at bottom most edge, and a line between them

    marked_image = image.copy()
    cv2.circle(marked_image, top, 5, (0, 0, 255), -1)  
    cv2.circle(marked_image, bottom, 5, (0, 0, 255), -1)  
    cv2.line(marked_image, top, bottom, (0, 0, 255), 2)  
    
    display_image(marked_image, canvas)

def create_gui():
    root = tk.Tk()
    root.title("Height Calculator")
    root.geometry("800x600")

    reference_height_var = tk.DoubleVar()

    tk.Button(root, text="Load Reference Image", command=lambda: load_reference_image(reference_canvas)).pack()
    tk.Button(root, text="Load Person Image", command=lambda: load_person_image(person_canvas)).pack()
    
    tk.Label(root, text="Reference Height (cm):").pack()
    tk.Entry(root, textvariable=reference_height_var).pack()

    tk.Button(root, text="Calculate Height", command=lambda: calculate_height(reference_canvas, person_canvas, reference_height_var)).pack()

    reference_canvas = tk.Canvas(root, width=300, height=400)
    reference_canvas.pack(side=tk.LEFT)

    person_canvas = tk.Canvas(root, width=300, height=400)
    person_canvas.pack(side=tk.RIGHT)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
