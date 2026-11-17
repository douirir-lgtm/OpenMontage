import sys,glob
from PIL import Image
fs=sorted(glob.glob("sortie/apercus/*.png"))
n=int(sys.argv[1]) if len(sys.argv)>1 else 4
for k in range(0,len(fs),n):
    sub=fs[k:k+n]
    sh=Image.new("RGB",(n*486,864))
    for j,f in enumerate(sub): sh.paste(Image.open(f).resize((486,864),Image.LANCZOS),(j*486,0))
    sh.save(f"work/ap_{k//n}.jpg",quality=88)
