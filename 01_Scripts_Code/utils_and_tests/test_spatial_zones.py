import cv2
import numpy as np

img = cv2.imread(r"c:\Users\DELL\Documents\CODE\DU_AN\inspect_vid\sec_08.jpg")
h, w, c = img.shape

# White levels
res = img.astype(np.float32)
res[:,:,0] = np.clip((res[:,:,0] - 10.2) / (181.05 - 10.2) * 255.0, 0, 255)
res[:,:,1] = np.clip((res[:,:,1] - 10.2) / (191.25 - 10.2) * 255.0, 0, 255)
res[:,:,2] = np.clip((res[:,:,2] - 10.2) / (201.45 - 10.2) * 255.0, 0, 255)
clean = res.astype(np.uint8)

# 1. Zone left of rod (excluding Question Card and Badge):
# Card bounding box: [65:588, 32:772]
# Badge: [20:105, 20:360]
# Everything else left of rod (X < 965) is BACKGROUND WALL!
clean[30:65, 30:965] = [255, 255, 255] # above card
clean[588:740, 30:965] = [255, 255, 255] # below card
clean[65:588, 772:965] = [255, 255, 255] # right of card
clean[65:588, 30:35] = [255, 255, 255] # left of card

# 2. Zone between rod and thermometer:
# Rod is at X: 968..985. Thermometer is at X: 1080..1125.
# Connector arm is at Y: 118..132, X: 980..1085.
clean[30:118, 985:1080] = [255, 255, 255]
clean[132:1040, 985:1080] = [255, 255, 255]

# 3. Zone above beaker/burner (Y < 300, X: 1125..1890):
clean[30:300, 1125:1890] = [255, 255, 255]

# 4. Now let's save and inspect this immediate result!
cv2.imwrite(r"c:\Users\DELL\Documents\CODE\DU_AN\test_spatial_clean_08.jpg", clean)
print("Saved test_spatial_clean_08.jpg")
