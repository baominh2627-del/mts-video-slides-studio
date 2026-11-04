import shutil
from PIL import Image

im = Image.open(r'C:\Users\DELL\Documents\CODE\DU_AN\fdown_build\test_cover_cyclotron.jpg')

p1 = r'C:\Users\DELL\Documents\CODE\DU_AN\ẢNH BÌA TIKTOK_MÁY GIA TỐC CYCLOTRON.png'
p2 = r'C:\Users\DELL\Documents\CODE\DU_AN\ẢNH BÌA TT_MÁY GIA TỐC CYCLOTRON.png'
p3 = r'C:\Users\DELL\Documents\Downloads\ẢNH BÌA TIKTOK_MÁY GIA TỐC CYCLOTRON.png'
p4 = r'C:\Users\DELL\Documents\Downloads\ẢNH BÌA TT_MÁY GIA TỐC CYCLOTRON.png'

im.save(p1, format='PNG')
shutil.copy(p1, p2)
shutil.copy(p1, p3)
shutil.copy(p1, p4)

print("Saved all 4 Cyclotron cover files successfully!")
