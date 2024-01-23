import numpy as np
import fractalrenderer

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
    return [color3, color4, color6]

xmins, xmaxs, ymins, ymaxs = fractalrenderer.create_zoom_viewports(0.36, 0.1, 0.36, 0.1, 2, 0.02, 1.6, 0.016, 10)
fractalrenderer.process_steps_multithreaded(xmins, xmaxs, ymins, ymaxs, 1920, 1080, 255, 10, mandelbrot, 10, True, "anims")
