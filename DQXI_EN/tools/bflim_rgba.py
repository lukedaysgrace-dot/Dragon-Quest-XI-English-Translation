import struct
from PIL import Image
import sys
sys.path.insert(0,'/home/claude/tools')
import bflim
def dec4444(d):
    w,h,fmt,swz,size=bflim.info(d)
    pw,ph=bflim._dims(w,h,swz)
    img=Image.new('RGBA',(pw,ph)); px=img.load(); o=0
    for ty in range(0,ph,8):
        for tx in range(0,pw,8):
            for i in range(64):
                x=y=0
                for b in range(3):
                    x|=((i>>(2*b))&1)<<b; y|=((i>>(2*b+1))&1)<<b
                v=struct.unpack_from('<H',d,o)[0]; o+=2
                px[tx+x,ty+y]=(((v>>12)&15)*17,((v>>8)&15)*17,((v>>4)&15)*17,(v&15)*17)
    if swz==4: img=img.transpose(Image.Transpose.ROTATE_90)
    return img.crop((0,0,w,h))

def enc4444(orig,img):
    w,h,fmt,swz,size=bflim.info(orig)
    img=img.convert('RGBA')
    if swz==4: img=img.transpose(Image.Transpose.ROTATE_270)
    pw,ph=bflim._dims(w,h,swz)
    cv=Image.new('RGBA',(pw,ph)); cv.paste(img,(0,0)); px=cv.load(); out=bytearray()
    for ty in range(0,ph,8):
        for tx in range(0,pw,8):
            for i in range(64):
                x=y=0
                for b in range(3):
                    x|=((i>>(2*b))&1)<<b; y|=((i>>(2*b+1))&1)<<b
                r,g,b_,a=px[tx+x,ty+y]
                v=((r+8)//17)<<12|((g+8)//17)<<8|((b_+8)//17)<<4|((a+8)//17)
                out+=struct.pack('<H',v)
    assert len(out)==size
    return bytes(out)+orig[size:]
