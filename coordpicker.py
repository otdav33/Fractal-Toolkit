from PIL import Image, ImageTk
import tkinter as tk
import argparse

parser = argparse.ArgumentParser(description='A tool for finding value investing deals and backtesting the methods used for value investing')

parser.add_argument("image_path",
        help='Path to the image file',
        nargs=1)

args = parser.parse_args()
image_path = args.image_path[0]

def get_bounds_from_filepath(filepath):
    filename = filepath.split('/')[-1][:-4]
    lastbit = filename.split('_')[-1]
    xs, ys = lastbit.split('x')
    xmin, xmax = xs.split('to')
    ymin, ymax = ys.split('to')
    xmin, xmax, ymin, ymax = float(xmin), float(xmax), float(ymin), float(ymax)
    print(xmin, xmax, ymin, ymax)
    return xmin, xmax, ymin, ymax

def pixel_coordinates(event):
    pixelx, pixely = event.x, event.y
    print(f'{pixelx=}, {pixely=}')
    space_width = xmax - xmin
    space_height = ymax - ymin
    x = (pixelx/img.width) * space_width + xmin
    y = ymax - (pixely/img.height) * space_height
    s = f"{x} + {y}j"
    print(s)
    window.clipboard_clear()
    window.clipboard_append(s)

xmin, xmax, ymin, ymax = get_bounds_from_filepath(image_path)

# Create a tkinter window
window = tk.Tk()
window.title("Coordinate Picker (outputs to clipboard and stdout)")
window.geometry("1980x1020")

# Open the image
img = Image.open(image_path)
pimg = ImageTk.PhotoImage(img)
img_label = tk.Label(image=pimg)
img_label.place(x=0, y=0)
img_label.bind("<Button-1>", pixel_coordinates)

# Start the tkinter event loop
window.mainloop()
