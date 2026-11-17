"""Planches d'aperçus : python3 scripts/sheet.py [n_par_planche] [dossier_apercus] [prefixe_sortie]
Défaut : 4, sortie/apercus, work/ap_ ; version corrigée : python3 scripts/sheet.py 4 sortie/apercus_corrigee work/corrigee/ap_"""
import sys,glob
from PIL import Image
n=int(sys.argv[1]) if len(sys.argv)>1 else 4
d=sys.argv[2] if len(sys.argv)>2 else "sortie/apercus"
pre=sys.argv[3] if len(sys.argv)>3 else "work/ap_"
fs=sorted(glob.glob(f"{d}/*.png"))
for k in range(0,len(fs),n):
    sub=fs[k:k+n]
    sh=Image.new("RGB",(n*486,864))
    for j,f in enumerate(sub): sh.paste(Image.open(f).resize((486,864),Image.LANCZOS),(j*486,0))
    sh.save(f"{pre}{k//n}.jpg",quality=88)
