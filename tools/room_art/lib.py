from PIL import Image
W,H=480,270
P={
'w0':(19,23,35),'w1':(24,30,45),'w2':(30,37,55),'w3':(36,45,66),'trim':(46,56,82),
's0':(13,16,25),'s1':(17,21,32),
'bb0':(11,14,21),'bb1':(42,51,72),
'f0':(19,23,33),'f1':(23,28,40),'f2':(27,33,47),'seam':(13,16,23),
'fr':(54,66,96),'frd':(34,42,62),'sky0':(9,15,29),'sky1':(14,24,44),'moon':(224,240,255),'moon2':(168,194,230),'star':(150,182,226),
'wd0':(40,28,23),'wd1':(66,47,36),'wd2':(94,68,50),'wd3':(124,91,65),'wd4':(156,118,84),
'g0':(38,42,52),'g1':(68,74,88),'g2':(108,116,132),'g3':(158,166,182),'g4':(210,216,228),
'sc0':(12,26,40),'sc1':(36,96,126),'sc2':(70,170,205),'cyan':(110,229,255),
'pp':(233,225,210),'pp2':(194,184,166),
'or0':(150,82,42),'or1':(197,116,61),'or2':(226,152,92),
'nv0':(24,44,74),'nv1':(38,68,108),'nv2':(58,98,148),
'rd0':(92,32,42),'rd1':(138,52,62),'rd2':(176,78,82),
'gr0':(30,60,48),'gr1':(46,94,72),'gr2':(70,132,98),'pot0':(112,62,46),'pot1':(150,88,62),
'r0':(33,27,51),'r1':(46,37,70),'r2':(61,50,92),'r3':(80,66,118),
'bl0':(34,34,70),'bl1':(48,48,96),'bl2':(64,64,124),'bl3':(84,84,150),
'sh0':(132,138,166),'sh1':(176,182,206),'sh2':(206,210,228),
'pi0':(150,152,182),'pi1':(192,194,216),'pi2':(228,228,242),
'm0':(28,64,58),'m1':(40,90,78),'m2':(58,122,104),'m3':(80,152,128),
'bt0':(40,110,140),'bt1':(80,168,200),'bt2':(150,214,236),
'ls0':(176,146,100),'ls1':(226,200,146),'ls2':(250,232,186),
'cat0':(70,74,84),'cat1':(110,115,126),'cat2':(150,155,166),'cat3':(190,194,204),'hood':(22,22,28),'hood1':(36,36,44),'hood2':(52,52,62),
'gold':(247,215,116),'gold2':(255,238,176),'eye':(242,190,70),'nose':(212,140,150),'pupil':(20,20,24),
'ink':(10,12,18),
}
def C(c): return P[c] if isinstance(c,str) else c
class L:
    def __init__(s,w=W,h=H,bg=None):
        s.im=Image.new('RGBA',(w,h),(0,0,0,0) if bg is None else C(bg)+(255,)); s.w=w; s.h=h; s.px=s.im.load()
    def put(s,x,y,c,a=255):
        if 0<=x<s.w and 0<=y<s.h: s.px[x,y]=C(c)+(a,)
    def get(s,x,y): return s.px[x,y]
    def rect(s,x0,y0,x1,y1,c):
        for y in range(y0,y1+1):
            for x in range(x0,x1+1): s.put(x,y,c)
    def hl(s,x0,x1,y,c): s.rect(x0,y,x1,y,c)
    def vl(s,x,y0,y1,c): s.rect(x,y0,x,y1,c)
    def line(s,x0,y0,x1,y1,c,w=1):
        n=max(abs(x1-x0),abs(y1-y0),1)
        for i in range(n+1):
            x=round(x0+(x1-x0)*i/n); y=round(y0+(y1-y0)*i/n)
            for k in range(w): s.put(x+k,y,c)
    def ell(s,cx,cy,rx,ry,c,fn=None):
        for y in range(int(cy-ry)-1,int(cy+ry)+2):
            for x in range(int(cx-rx)-1,int(cx+rx)+2):
                d=((x-cx)/rx)**2+((y-cy)/ry)**2
                if d<=1:
                    s.put(x,y, fn(d,x,y) if fn else c)
    def poly(s,pts,c):
        ys=[p[1] for p in pts]
        for y in range(min(ys),max(ys)+1):
            xs=[]
            n=len(pts)
            for i in range(n):
                (x0,y0),(x1,y1)=pts[i],pts[(i+1)%n]
                if (y0<=y<y1) or (y1<=y<y0):
                    xs.append(x0+(y-y0)*(x1-x0)/(y1-y0))
            xs.sort()
            for i in range(0,len(xs)-1,2):
                for x in range(round(xs[i]),round(xs[i+1])+1): s.put(x,y,c)
    def outline(s,c='ink'):
        src=s.im.copy(); sp=src.load()
        for y in range(s.h):
            for x in range(s.w):
                if sp[x,y][3]==0:
                    for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
                        xx,yy=x+dx,y+dy
                        if 0<=xx<s.w and 0<=yy<s.h and sp[xx,yy][3]>0:
                            s.put(x,y,c); break
        return s
def over(base,top,xy=(0,0)):
    base.alpha_composite(top,xy); return base
def bbox_trim(im):
    b=im.getbbox(); return im.crop(b),(b[0],b[1])
