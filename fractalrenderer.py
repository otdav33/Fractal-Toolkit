import numpy as np
from PIL import Image
import sympy as sy
import cv2
import concurrent.futures
import os

def mandelbrot(c, max_iter):
    """sample fractal function that can be used to render the mandelbrot set"""
    z = c
    oldz = z
    depths = np.zeros_like(z, dtype=np.float64) + max_iter
    upper_threshold = 9e23
    for n in range(max_iter):
        oldz = z
        depths[(depths == max_iter) & (abs(z) > upper_threshold)] = n
        z = z*z + c

    color1 = abs(255 - 255/(np.exp(z.real/50) + 1)) #inside/outside
    color2 = abs(255 - 255/(np.exp(z.imag/50) + 1)) #inside/outside
    color3 = abs((depths % 2) * 54) #solid bands around pattern
    color4 = abs(np.log(depths)*255/np.log(max_iter+2)) #gradient bands around pattern
    color5 = abs(z-oldz) % 2 * 54 # distance from center inside pattern
    color6 = abs(255 - 255/(np.exp(abs(depths)/50) + 1)) #distance from pattern
    return [color1, color1, color1]

def func_exp(c, max_iter):
    """sample fractal function that can be used to render the graph Euler's function in real and imaginary dimensions"""
    n = c
    oldn = n
    for v in range(max_iter):
        oldn = n
        n = np.exp(n)
    return [255 - 255/(np.exp(n.real/50) + 1), 255 - 255/(np.exp(n.imag/50) + 1), 255 - 255/(np.exp(abs(n-oldn)/50) + 1)]

def plot_func(xmin, xmax, ymin, ymax, width, height, max_iter, func):
    """Renders the fractal from the given function for the given viewport pixel-by-pixel.
    Try the function plot_func_at_once first since it is usually much faster.
    Width and height are in pixels.
    xmin, xmax, ymin and ymax describe the viewport box in coordinate space for your function.
    Returns an image."""
    r1 = np.linspace(xmin, xmax, width)
    r2 = np.linspace(ymax, ymin, height)
    data = np.array([[func(complex(r, i),max_iter) for r in r1] for i in r2])
    img = Image.fromarray(data.astype(np.uint8), 'RGB')
    return img

def plot_func_at_once(xmin, xmax, ymin, ymax, width, height, max_iter, func):
    """Renders the fractal from the given function for the given viewport for all pixels all at once as one big numpy array.
    Use the plot_func function instead if you would like to use per-pixel error handling in your function.
    Width and height are in pixels.
    xmin, xmax, ymin and ymax describe the viewport box in coordinate space for your function.
    Returns an image."""
    r1 = np.linspace(xmin, xmax, width)
    r2 = np.linspace(ymax, ymin, height)
    ins = np.array([[complex(r, i) for r in r1] for i in r2])
    outs = func(ins, max_iter)
    data = np.dstack(outs)
    img = Image.fromarray(data.astype(np.uint8), 'RGB')
    return img

def create_zoom_viewports(xi, yi, xf, yf, initial_width, final_width, initial_height, final_height, steps):
    """Create lists of viewport bounds for a fractal zoom animation.

    Arguments:
    xi -- initial x (real) coordinate for the center of the animation
    yi -- initial y (imaginary) coordinate for the center of the animation
    xf -- final x (real) coordinate for the center of the animation
    yf -- final y (imaginary) coordinate for the center of the animation
    initial_width -- width (real dimension) in coordinate space of the first frame in the animation
    final_width -- width (real dimension) in coordinate space of the last frame in the animation
    initial_height -- height (imaginary dimension) in coordinate space of the first frame in the animation
    final_height -- height (imaginary dimension) in coordinate space of the last frame in the animation
    steps -- number of frames in the animation

    Returns xmins, xmaxs, ymins, ymaxs (which describe the viewport box in coordinate space for your function)."""
    widths = np.geomspace(initial_width, final_width, steps)
    heights = np.geomspace(initial_height, final_height, steps)
    centerxs = np.linspace(xi, xf, steps)
    centerys = np.linspace(yi, yf, steps)
    xmins = centerxs - (widths/2)
    ymins = centerys - (heights/2)
    xmaxs = centerxs + (widths/2)
    ymaxs = centerys + (heights/2)
    return xmins, xmaxs, ymins, ymaxs

def create_zoom_viewports_from_viewports(xmini, xmaxi, ymini, ymaxi, xminf, xmaxf, yminf, ymaxf, steps):
    """Create lists of viewport bounds for a fractal zoom animation.
    x represents the real dimension
    y represents the imaginary dimension
    i is for "initial"
    f is for "final"
    steps -- number of frames in the animation

    Returns xmins, xmaxs, ymins, ymaxs (which describe the viewport box in coordinate space for your function)."""
    initial_width = xmaxi - xmini
    final_width = xmaxf - xminf
    initial_height = ymaxi - ymini
    final_height = ymaxf - yminf
    xi = (xmaxi + xmini) / 2
    xf = (xmaxf + xminf) / 2
    yi = (ymaxi + ymini) / 2
    yf = (ymaxf + yminf) / 2
    return create_zoom_viewports(xi, yi, xf, yf, initial_width, final_width, initial_height, final_height, steps)

def process_steps(xmins, xmaxs, ymins, ymaxs, width, height, max_iter, start, steps, func, at_once=True, animations_dir="anims"):
    """Render a fractal zoom animation (singlethreaded)
    xmins, xmaxs, ymins and ymaxs describe the viewport box in coordinate space for your function.
    width and height are in pixels.
    max_iter -- the maximum number of iterations to run the function for. 
    start -- the number of the first frame to render. Usually this will be 0. Existing frames will not be rendered regardless.
    steps -- the number of frames of the animation to be rendered.
    func -- the function to use to render the fractal should take c (input coordinate where c.real is x and c.imag is y) and max_iter as arguments and return [red, green, blue] where each color value is 0 to 255. For a test, you can use the inbuilt mandelbrot function.
    at_once -- whether to process the pixels on the fractal all at once as one big numpy array (at_once=True) or pixel-by-pixel (at_once=False). True is usually much faster but False allows for per-pixel error handling.
    animations_dir -- path to the directory to put the animation in (preferably a fresh empty directory)

    Returns a list of images and also saves those images to the specified directory."""

    #make sure the correct directory exists
    dir_exists = os.path.exists(f'{animations_dir}/{func.__name__}/')
    if not dir_exists:
        os.makedirs(f'{animations_dir}/{func.__name__}/')

    images = []
    for i in range(start, start + steps):
        #only make the calculation if there is no existing file
        try:
            os.stat(f'{animations_dir}/{func.__name__}/animation_{i}_{xmins[i]}to{xmaxs[i]}x{ymins[i]}to{ymaxs[i]}.png')
        except FileNotFoundError as e:
            if at_once:
                image = plot_func_at_once(xmins[i], xmaxs[i], ymins[i], ymaxs[i], width, height, max_iter, func)
            else:
                image = plot_func(xmins[i], xmaxs[i], ymins[i], ymaxs[i], width, height, max_iter, func)
            images += [image]
            image.save(f'{animations_dir}/{func.__name__}/animation_{i}_{xmins[i]}to{xmaxs[i]}x{ymins[i]}to{ymaxs[i]}.png')
    return images

def process_steps_multithreaded(xmins, xmaxs, ymins, ymaxs, width, height, max_iter, steps, func, num_threads, at_once=True, animations_dir="anims"):
    """Render a fractal zoom animation (multithreaded)
    xmins, xmaxs, ymins and ymaxs describe the viewport box in coordinate space for your function.
    width and height are in pixels.
    max_iter -- the maximum number of iterations to run the function for. 
    steps -- the number of frames of the animation to be rendered.
    func -- the function to use to render the fractal should take c (input coordinate where c.real is x and c.imag is y) and max_iter as arguments and return [red, green, blue] where each color value is 0 to 255. For a test, you can use the inbuilt mandelbrot function.
    num_threads -- number of threads to use for the computation. Usually you want to use just fewer than the number of processor cores on your computer. Make this a multiple of the number of steps.
    at_once -- whether to process the pixels on the fractal all at once as one big numpy array (at_once=True) or pixel-by-pixel (at_once=False). True is usually much faster but False allows for per-pixel error handling.
    animations_dir -- path to the directory to put the animation in (preferably a fresh empty directory)

    Returns a list of images and also saves those images to the specified directory."""
    images = []
    chunk_size = int(steps / num_threads)

    # Using ProcessPoolExecutor to run the function in separate processes
    with concurrent.futures.ProcessPoolExecutor() as executor:
        # Process each chunk in a separate thread and collect Future objects
        futures = [executor.submit(process_steps, xmins, xmaxs, ymins, ymaxs, width, height, max_iter, i, chunk_size, func, at_once, animations_dir) for i in range(0, steps, chunk_size)]
        # Wait for all threads to complete and get results
        concurrent.futures.wait(futures)
        # Consolidate the output from each thread
        images = [result for future in futures for result in future.result()]

    return images
