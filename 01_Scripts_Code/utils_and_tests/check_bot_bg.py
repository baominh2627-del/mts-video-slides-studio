import cv2

for name in ['frame_0pct_0.0s', 'frame_30pct_71.2s', 'frame_70pct_166.1s', 'frame_99pct_234.9s']:
    im = cv2.imread(rf'C:\Users\DELL\Documents\CODE\DU_AN\fdown_build\{name}.jpg')
    bot = im[930:1010, :]
    cv2.imwrite(rf'C:\Users\DELL\Documents\CODE\DU_AN\fdown_build\bot_{name}.jpg', bot)
print("Saved bot crops")
