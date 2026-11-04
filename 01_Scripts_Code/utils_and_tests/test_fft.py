import cv2
import numpy as np

img = cv2.imread(r"c:\Users\DELL\Documents\CODE\DU_AN\crop_box_orig.png", cv2.IMREAD_GRAYSCALE)

# Compute 2D FFT
dft = cv2.dft(np.float32(img), flags=cv2.DFT_COMPLEX_OUTPUT)
dft_shift = np.fft.fftshift(dft)
magnitude_spectrum = 20 * np.log(cv2.magnitude(dft_shift[:,:,0], dft_shift[:,:,1]) + 1)

# Normalize for saving
mag_norm = cv2.normalize(magnitude_spectrum, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
cv2.imwrite(r"c:\Users\DELL\Documents\CODE\DU_AN\fft_mag.png", mag_norm)
print("Saved fft_mag.png")
