import sys
from PIL import Image
ns=sys.argv[2:];ims=[Image.open(n).convert('RGB') for n in ns]
w,h=640,480;c=min(3,len(ims));r=(len(ims)+c-1)//c
o=Image.new('RGB',(w*c,h*r))
for i,im in enumerate(ims): o.paste(im.resize((w,h)),(w*(i%c),h*(i//c)))
o.save(sys.argv[1])
