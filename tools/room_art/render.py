import json, os, sys
from PIL import Image
from lib import *
import scene, sprites
def inpoly(x,y,pts):
    c=False; n=len(pts)
    for i in range(n):
        (x0,y0),(x1,y1)=pts[i],pts[(i+1)%n]
        if (y0>y)!=(y1>y) and x < x0+(y-y0)*(x1-x0)/(y1-y0): c=not c
    return c
def light(im,cx,cy,rx,ry,col,k):
    px=im.load()
    for y in range(max(0,int(cy-ry)),min(H,int(cy+ry)+1)):
        for x in range(max(0,int(cx-rx)),min(W,int(cx+rx)+1)):
            d=((x-cx)/rx)**2+((y-cy)/ry)**2
            if d>=1: continue
            lv=1.0 if d<0.18 else 0.66 if d<0.42 else 0.4 if d<0.7 else 0.16
            for t,a,b in ((0.18,1.0,0.66),(0.42,0.66,0.4),(0.7,0.4,0.16)):
                if abs(d-t)<0.04 and (x+y)%2: lv=b if d<t else a
            if d>0.9 and (x+y)%2: lv=0
            a=k*lv; r,g,b,al=px[x,y]
            px[x,y]=(min(255,int(r+col[0]*a*0.5)),min(255,int(g+col[1]*a*0.5)),min(255,int(b+col[2]*a*0.5)),al)
def ghost(obj):
    o=obj.copy(); p=o.load()
    for y in range(o.height):
        for x in range(o.width):
            r,g,b,a=p[x,y]
            if a==0: continue
            l=(r*0.3+g*0.59+b*0.11)
            t=(int(l*0.35+150*0.65),int(l*0.35+186*0.65),int(l*0.35+238*0.65))
            p[x,y]=t+((150 if (x+y)%2==0 else 55),)
    return o
def dim(im,pool,k=0.62):
    p=im.load()
    for y in range(H):
        for x in range(W):
            f=k
            if pool:
                cx,cy,rx,ry=pool
                d=((x-cx)/(rx*1.45))**2+((y-cy)/(ry*1.45))**2
                if d<0.75: continue
                if d<1.0: f=1-(1-k)*0.5 if (x+y)%2 else 1
                elif d<1.3: f=1-(1-k)*0.5 if (x+y)%2==0 else k
            r,g,b,a=p[x,y]; p[x,y]=(int(r*f),int(g*f),int(b*f),a)
def glow(im,cx,cy,rx,ry,col,k):
    light(im,cx,cy,rx,ry,col,k)
def moonshaft(im,k=0.10):
    p=im.load()
    quad=[(196,150),(252,150),(238,200),(170,200)]
    for y in range(150,201):
        for x in range(165,256):
            if not inpoly(x,y,quad): continue
            t=(y-150)/50; xl=196+(170-196)*t; xr=252+(238-252)*t; u=(x-xl)/max(1,(xr-xl))
            if abs(u-0.5)<0.03 or abs(t-0.5)<0.05: continue
            f=1.0 if 0.06<u<0.94 and 0.08<t<0.92 else 0.5
            if f<1 and (x+y)%2: continue
            r,g,b,a=p[x,y]; p[x,y]=(min(255,int(r+40*k*f*3)),min(255,int(g+60*k*f*3)),min(255,int(b+95*k*f*3)),a)
def vignette(im,k=0.5):
    p=im.load()
    for y in range(H):
        for x in range(W):
            dx=(x-W/2)/(W/2); dy=(y-H/2)/(H/2); d=dx*dx*0.8+dy*dy*0.9
            if d>0.55:
                f=1-min(1,(d-0.55)/0.9)*k
                if (x+y)%2 and d<0.65: continue
                r,g,b,a=p[x,y]; p[x,y]=(int(r*f),int(g*f),int(b*f),a)
def compose(placed,ghosts,selected=None,ringo=('idle',(270,214)),rest=False,markers=(),glints=(),extra=None):
    im=scene.stage0().im.copy()
    moonshaft(im,0.30 if rest else 0.18)
    for z in scene.ORDER: over(im,scene.ZONES[z]['prop']().im)
    allobjs={k:f for z in scene.ORDER for k,f in scene.ZONES[z]['objs']}
    for k in placed: over(im,allobjs[k]().im)
    for k in ghosts: over(im,ghost(allobjs[k]().im))
    if extra: extra(im)
    if not rest:
        for zk in scene.ORDER:
            cx,cy,rx,ry=scene.ZONES[zk]['pool']; light(im,cx,cy,rx*0.9,ry*0.9,scene.ZONES[zk]['light'],0.15)
    light(im,242,46,52,44,(150,190,255),0.16 if not rest else 0.26)
    if ringo:
        st,(ax,ay)=ringo
        sp=sprites.sprite(sprites.IDLE if st=='idle' else sprites.SLEEP).im
        # shadow
        p=im.load()
        for x in range(ax-sp.width//2+2,ax+sp.width//2-1):
            for y in (ay-1,ay,ay+1):
                if 0<=x<W and 0<=y<H and ((x+y)%2==0 or y==ay):
                    r,g,b,a=p[x,y]; p[x,y]=(int(r*0.6),int(g*0.6),int(b*0.6),a)
        over(im,sp,(ax-sp.width//2,ay-sp.height+1))
    if selected:
        z=scene.ZONES[selected]; cx,cy,rx,ry=z['pool']
        dim(im,z['pool'])
        light(im,cx,cy,rx,ry,z['light'],0.62)
    if rest:
        dim(im,None,0.74)
    for (x,y,due) in markers:
        b=sprites.bell().im
        if due:
            bp=b.load()
            for yy in range(b.height):
                for xx in range(b.width):
                    r,g,bb,a=bp[xx,yy]
                    if a and (r,g,bb)!=P['ink']: bp[xx,yy]=P['cyan']+(255,)
        over(im,b,(x-b.width//2,y-b.height//2))
    for (x,y) in glints:
        g=sprites.glint().im; over(im,g,(x-4,y-4))
    vignette(im)
    return im
