import math, json, os
from lib import *
WALL_Y=118
BED='A'  # wall/floor seam
# ---------- STAGE 0 ----------
def stage0():
    s=L(bg='w1')
    # back wall bands (top darker), subtle vertical panel seams
    for y in range(0,WALL_Y):
        c='w0' if y<34 else 'w1' if y<78 else 'w2'
        s.hl(0,W-1,y,c)
    for y in (33,77):   # dithered band transitions
        for x in range(0,W,2): s.put(x+(y%2),y,'w1' if y==33 else 'w2')
    s.hl(0,W-1,62,'w0'); s.hl(0,W-1,63,'w2')   # picture rail
    for x in range(20,W-14,28):   # wainscot panels
        s.vl(x,66,110,'w1'); s.vl(x+1,66,110,'w3')
    # baseboard
    s.rect(22,WALL_Y-5,W-23,WALL_Y-1,'bb0'); s.hl(22,W-23,WALL_Y-5,'bb1')
    VPX,VPY=240,-60
    def rayx(xb,y): return VPX+(xb-VPX)*(y-VPY)/(WALL_Y-VPY)
    LW=[(0,0),(22,0),(22,WALL_Y),(0,136)]; RW=[(W-23,0),(W-1,0),(W-1,136),(W-23,WALL_Y)]
    y=WALL_Y; gap=5; rows=[]
    while y<H: rows.append((y,min(H-1,y+gap))); y+=gap; gap+=1
    for yy in range(WALL_Y,H):
        t=(yy-WALL_Y)/(H-WALL_Y)
        for x in range(W):
            c='f2' if t<0.25 else ('f1' if t<0.65 else 'f0')
            if abs(t-0.25)<0.03 and (x+yy)%2: c='f1'
            if abs(t-0.65)<0.03 and (x+yy)%2: c='f0'
            s.put(x,yy,c)
    for i,(y0,y1) in enumerate(rows):
        if i%2==0: s.hl(0,W-1,y0,'seam')
    for xb in range(22-16*14,W+16*14,16):
        for yy in range(WALL_Y,H):
            x=round(rayx(xb,yy))
            if 0<=x<W: s.put(x,yy,'seam')
    s.poly(LW,'s1'); s.poly(RW,'s1'); s.vl(22,0,WALL_Y,'s0'); s.vl(W-23,0,WALL_Y,'s0')
    s.line(22,WALL_Y-1,0,135,'bb1'); s.line(22,WALL_Y,0,136,'bb0'); s.line(22,WALL_Y+1,0,137,'bb0')
    s.line(W-23,WALL_Y-1,W-1,135,'bb1'); s.line(W-23,WALL_Y,W-1,136,'bb0'); s.line(W-23,WALL_Y+1,W-1,137,'bb0')
    # floor darkening toward front edge (dither) and back edge AO
    for y in range(WALL_Y,WALL_Y+4):
        for x in range(23,W-23):
            if (x+y)%2==0 or y<WALL_Y+2: s.put(x,y,'seam')
    # window (between Learning and Creative)
    wx0,wy0,wx1,wy1=212,14,272,78
    s.rect(wx0-2,wy0-2,wx1+2,wy1+2,'frd'); s.rect(wx0,wy0,wx1,wy1,'fr')
    s.rect(wx0+3,wy0+3,wx1-3,wy1-3,'sky0')
    for y in range(wy0+3,wy0+28):
        for x in range(wx0+3,wx1-2):
            if y<wy0+16 or (x+y)%2==0: s.put(x,y,'sky1')
    mx=(wx0+wx1)//2
    s.rect(mx-1,wy0+3,mx,wy1-3,'fr'); s.rect(wx0+3,46,wx1-3,47,'fr')
    s.hl(wx0,wx1,wy0,'trim')
    cx,cy=257,28
    for y in range(cy-7,cy+8):
        for x in range(cx-7,cx+8):
            if (x-cx)**2+(y-cy)**2<=49 and (x-cx-3)**2+(y-cy+2)**2>30:
                s.put(x,y,'moon' if (x-cx)**2+(y-cy)**2<=36 else 'moon2')
    for st in [(220,22),(232,34),(222,58),(266,62),(246,54),(238,19),(229,70),(262,42)]: s.put(*st,'star')
    s.rect(wx0-5,wy1+3,wx1+5,wy1+5,'wd2'); s.hl(wx0-5,wx1+5,wy1+3,'wd3'); s.hl(wx0-4,wx1+4,wy1+6,'bb0')
    # rug (center circulation)
    def rugf(d,x,y):
        if d>0.86: return 'r3' if (x//2+y)%2==0 else 'r2'
        if d>0.78: return 'r0'
        if 0.40<d<0.46: return 'r2'
        return 'r1' if d>0.12 else ('r2' if (x+y)%2==0 else 'r1')
    s.ell(275,215,70,30,None,rugf)
    # fringe
    for x in range(212,340,3):
        if abs(x-275)<66:
            import math
            yy=215+int(30*math.sqrt(max(0,1-((x-275)/70)**2)))
            s.put(x,yy+1,'r3'); s.put(x,yy+2,'r2')
    # wall outlet + light switch (non-interactive details)
    s.rect(180,104,184,108,'w3'); s.put(182,106,'w0')
    s.rect(368,72,371,77,'w3')
    return s

# ---------- PROPS ----------
def PJ(xb,yf,h=0):
    k=(yf+60)/178
    return (round(240+(xb-240)*k), round(yf-h*k))
def face(s,pts3,c):
    s.poly([PJ(*p) for p in pts3],c)
def box(s,x0,x1,yb,yf,h0,h1,top,front,side,sideedge=None):
    if x0>240: face(s,[(x0,yb,h1),(x0,yf,h1),(x0,yf,h0),(x0,yb,h0)],side)
    elif x1<240: face(s,[(x1,yb,h1),(x1,yf,h1),(x1,yf,h0),(x1,yb,h0)],side)
    face(s,[(x0,yf,h1),(x1,yf,h1),(x1,yf,h0),(x0,yf,h0)],front)
    face(s,[(x0,yb,h1),(x1,yb,h1),(x1,yf,h1),(x0,yf,h1)],top)
def fl(s,x0,x1,yf,h,c):   # horizontal line on a front plane
    p,q=PJ(x0,yf,h),PJ(x1,yf,h); s.line(p[0],p[1],q[0],q[1],c)
def fr(s,x0,x1,yf,h0,h1,c):  # rect on a front plane
    face(s,[(x0,yf,h1),(x1,yf,h1),(x1,yf,h0),(x0,yf,h0)],c)

def shadow(s,cx,cy,rx,ry,a=120):
    for y in range(int(cy-ry)-1,int(cy+ry)+2):
        for x in range(int(cx-rx)-1,int(cx+rx)+2):
            if 0<=x<W and 0<=y<H and ((x-cx)/rx)**2+((y-cy)/ry)**2<=1 and s.px[x,y][3]==0:
                d=((x-cx)/rx)**2+((y-cy)/ry)**2
                if d>0.6 and (x+y)%2: continue
                s.px[x,y]=(6,8,12,a)
def shift(s,dx):
    from PIL import Image
    im=Image.new('RGBA',(W,H),(0,0,0,0)); im.alpha_composite(s.im,(dx,0)); s.im=im; s.px=im.load(); return s

def prop_work_desk():
    s=L()
    X0,X1,YB,YF,H=28,142,118,132,30
    # legs (left) + drawer unit (right)
    box(s,X0,X0+4,YF-4,YF,0,H-4,'wd2','wd1','wd0')
    box(s,X0,X0+4,YB,YB+4,0,H-4,'wd1','wd0','wd0')
    box(s,110,X1-2,YB+2,YF,0,H-4,'wd3','wd2','wd1')
    fl(s,110,X1-2,YF,(H-4)//2,'wd1')
    for hh in (16,5):
        p=PJ(124,YF,hh); s.rect(p[0]-3,p[1],p[0]+3,p[1]+1,'g3')
    # top slab
    box(s,X0-2,X1+2,YB,YF+2,H-4,H,'wd3','wd2','wd1')
    fl(s,X0-2,X1+2,YF+2,H,'wd4')
    for xb in range(36,140,18):
        p,q=PJ(xb,YB+4,H),PJ(xb+7,YB+4,H); s.hl(p[0],q[0],p[1],'wd2')
    # laptop
    box(s,46,78,YB+5,YB+13,H,H+2,'g3','g2','g1')
    face(s,[(48,YB+5,H+2),(76,YB+5,H+2),(76,YB+5,H+22),(48,YB+5,H+22)],'g1')
    face(s,[(50,YB+5,H+4),(74,YB+5,H+4),(74,YB+5,H+20),(50,YB+5,H+20)],'sc0')
    for i,hh in enumerate(range(H+18,H+6,-3)):
        p=PJ(52,YB+5,hh); s.hl(p[0],p[0]+3+((i*7)%14),p[1],'sc1')
    p=PJ(52,YB+5,H+18); s.hl(p[0],p[0]+9,p[1],'sc2'); p=PJ(72,YB+5,H+19); s.put(p[0],p[1],'cyan')
    # chair (back to viewer), projected in front of the desk
    C0,C1=62,88
    box(s,73,76,146,149,0,12,'g1','g0','g0')
    p,q=PJ(C0-2,150,0),PJ(C1+2,150,0); s.hl(p[0],q[0],p[1],'g0'); s.put(p[0],p[1]+1,'g1'); s.put(q[0],q[1]+1,'g1')
    box(s,C0,C1,139,151,12,15,'g2','g1','g0')
    fl(s,C0,C1,151,15,'g3')
    box(s,C0+1,C1-1,150,152,15,33,'g1','g0','g0')
    fl(s,C0+1,C1-1,152,33,'g2'); fr(s,C0+4,C1-4,152,26,29,'g1')
    s.outline(); p=PJ(85,YF+6,0); shadow(s,p[0],p[1],64,5); q=PJ(75,151,0); shadow(s,q[0],q[1]+1,16,2,140); return s
def prop_learning_corner():
    s=L()
    X0,X1,YB,YF,H=156,206,118,130,40
    box(s,X0,X1,YB,YF,0,H,'wd3','wd1','wd0')
    fl(s,X0,X1,YF,H,'wd4')
    fr(s,X0+3,X1-3,YF,22,H-3,'wd0'); fr(s,X0+3,X1-3,YF,3,19,'wd0'); fr(s,X0+3,X1-3,YF,19,22,'wd2')
    # items inside
    fr(s,X0+6,X0+24,YF,3,11,'pot0'); fl(s,X0+6,X0+24,YF,11,'pot1'); fl(s,X0+11,X0+18,YF,7,'pp2')
    fr(s,X1-20,X1-16,YF,22,33,'nv1'); fr(s,X1-15,X1-12,YF,22,31,'g1')
    # plant on top (back right)
    p=PJ(X1-8,YB+5,H)
    s.rect(p[0]-4,p[1]-9,p[0]+4,p[1],'pot1'); s.hl(p[0]-4,p[0]+4,p[1]-9,'or2'); s.vl(p[0]+4,p[1]-9,p[1],'pot0')
    for (dx,dy) in [(0,-11),(-2,-14),(2,-15),(-4,-17),(4,-19),(0,-19),(-1,-23)]:
        s.rect(p[0]+dx-1,p[1]+dy-1,p[0]+dx+1,p[1]+dy+1,'gr1'); s.put(p[0]+dx,p[1]+dy-1,'gr2')
    s.line(p[0],p[1]-10,p[0],p[1]-21,'gr0')
    # stool
    s.ell(224,128,11,4,None,lambda d,x,y:'wd4' if d<0.4 else 'wd3')
    s.rect(214,129,234,132,'wd2')
    s.line(216,133,214,156,'wd1',2); s.line(232,133,234,156,'wd1',2); s.line(224,133,224,153,'wd0',2)
    s.hl(217,231,146,'wd1')
    s.outline(); p=PJ(181,134,0); shadow(s,p[0],p[1],30,4); shadow(s,224,158,13,3); return s
def prop_creative_corner():
    s=L()
    # easel legs
    s.line(268,168,279,56,'wd2',2); s.line(296,168,285,56,'wd2',2); s.line(282,60,284,160,'wd1',2)
    s.rect(268,128,296,130,'wd3')
    # canvas
    s.rect(264,62,300,104,'wd1'); s.rect(266,64,298,102,'pp'); s.vl(298,64,102,'pp2'); s.hl(266,298,102,'pp2')
    s.hl(272,284,90,'or1'); 
    for i,x in enumerate(range(270,294)):
        s.put(x,84-int(5*math.sin(i/3.2)),'or0')
    # small table (projected)
    X0,X1,YB,YF,H=304,344,118,132,28
    box(s,X0,X0+3,YF-3,YF,0,H-3,'wd2','wd1','wd0'); box(s,X1-3,X1,YF-3,YF,0,H-3,'wd2','wd1','wd1')
    box(s,X0,X0+3,YB,YB+3,0,H-3,'wd1','wd0','wd0')
    box(s,X0-1,X1+1,YB,YF+1,H-4,H,'wd3','wd2','wd1')
    fl(s,X0-1,X1+1,YF+1,H,'wd4')
    # brush jar (back right of table top)
    p=PJ(X1-6,YB+5,H)
    s.rect(p[0]-3,p[1]-9,p[0]+2,p[1],'g2'); s.hl(p[0]-3,p[0]+2,p[1]-9,'g3')
    s.line(p[0]-2,p[1]-10,p[0]-4,p[1]-17,'or2'); s.line(p[0],p[1]-10,p[0]+2,p[1]-18,'wd4'); s.line(p[0]-1,p[1]-10,p[0]-1,p[1]-19,'cyan')
    s.outline(); shadow(s,282,170,20,3); p=PJ(324,136,0); shadow(s,p[0],p[1],26,4); return s
def prop_sleep_corner():
    s=L()
    X0,X1=350,410; YB,YF=120,176
    # --- nightstand to the right of the bed (projected box) ---
    n0,n1,nb,nf,nh=415,435,118,132,18
    face(s,[(n0,nb,nh),(n0,nf,nh),(n0,nf,0),(n0,nb,0)],'wd1')        # left side
    face(s,[(n0,nf,nh),(n1,nf,nh),(n1,nf,0),(n0,nf,0)],'wd2')        # front
    face(s,[(n0,nb,nh),(n1,nb,nh),(n1,nf,nh),(n0,nf,nh)],'wd3')      # top
    x0,y0=PJ(n0,nf,nh); x1,_=PJ(n1,nf,nh); s.hl(x0,x1,y0,'wd4')
    _,ym=PJ(n0,nf,9); s.hl(x0,x1,ym,'wd1'); cx=(x0+x1)//2
    s.rect(cx-3,ym-5,cx+3,ym-4,'g3'); s.rect(cx-3,ym+4,cx+3,ym+5,'g3')
    # --- headboard (front face + thin top) ---
    face(s,[(X0-2,YB-2,42),(X1+2,YB-2,42),(X1+2,YB,42),(X0-2,YB,42)],'wd4')
    face(s,[(X0-2,YB,42),(X1+2,YB,42),(X1+2,YB,0),(X0-2,YB,0)],'wd2')
    for xb in range(X0+6,X1,10):
        p,q=PJ(xb,YB,38),PJ(xb,YB,18); s.vl(p[0],p[1],q[1],'wd1')
    p,q=PJ(X0-2,YB,36),PJ(X1+2,YB,36); s.hl(p[0],q[0],p[1],'wd3')
    # --- left side face (visible: bed is right of the vanishing point) ---
    face(s,[(X0,YB,10),(X0,YF,10),(X0,YF,4),(X0,YB,4)],'wd1')        # frame side
    face(s,[(X0,YB,17),(X0,YF,17),(X0,YF,10),(X0,YB,10)],'sh0')      # mattress side
    face(s,[(X0,134,17),(X0,YF,17),(X0,YF,6),(X0,134,6)],'bl0')      # blanket drape on side
    # --- front (foot) face ---
    face(s,[(X0,YF,10),(X1,YF,10),(X1,YF,4),(X0,YF,4)],'wd2')
    face(s,[(X0,YF,17),(X1,YF,17),(X1,YF,6),(X0,YF,6)],'bl1')
    p,q=PJ(X0,YF,17),PJ(X1,YF,17); s.hl(p[0],q[0],p[1],'bl3')
    _,yb=PJ(X0,YF,6)
    for x in range(p[0],q[0]+1):
        if (x-p[0])%14 in (0,1): s.vl(x,p[1]+1,yb,'bl0')
        elif (x-p[0])%14 in (6,7): s.vl(x,p[1]+2,yb-1,'bl2')
    # --- top surface: sheet, fold, blanket ---
    face(s,[(X0,YB,17),(X1,YB,17),(X1,YF,17),(X0,YF,17)],'sh1')
    face(s,[(X0,130,17),(X1,130,17),(X1,134,17),(X0,134,17)],'sh2')
    face(s,[(X0,134,17),(X1,134,17),(X1,YF,17),(X0,YF,17)],'bl1')
    for xb in range(X0+8,X1-4,9):          # blanket ribs follow the perspective
        for yf in range(136,YF,2):
            x,y=PJ(xb,yf,17); s.put(x+(yf//2)%2,y,'bl2')
    for yf in (134,):
        p,q=PJ(X0,yf,17),PJ(X1,yf,17); s.line(p[0],p[1],q[0],q[1],'sh0')
    p,q=PJ(X0,YF,17),PJ(X0,YB,17); s.line(p[0],p[1],q[0],q[1],'bl2')
    # legs
    for xb in (X0+1,X1-3):
        p,q=PJ(xb,YF,4),PJ(xb+3,YF,0); s.rect(p[0],p[1],q[0],q[1],'wd1')
    s.outline()
    p=PJ((X0+X1)//2,YF+4,0); shadow(s,p[0],p[1],44,4); p=PJ(425,134,0); shadow(s,p[0],p[1],13,3)
    return s
def prop_fitness_corner():
    s=L()
    VPX,VPY=240,-60
    def rx(xb,y): return VPX+(xb-VPX)*(y-VPY)/(118-VPY)
    def xb_of(x,y): return VPX+(x-VPX)*(118-VPY)/(y-VPY)
    L0,R0=xb_of(46,206),xb_of(172,206)
    y0,y1=206,238
    for y in range(y0,y1+1):
        xl,xr=rx(L0,y),rx(R0,y)
        for x in range(round(xl),round(xr)+1):
            c='m1'
            u=(x-xl)/(xr-xl)
            if u<0.06 or u>0.94: c='m2'
            if abs(u-0.5)<0.012: c='m2' if y%3 else 'm1'
            s.put(x,y,c)
    s.line(round(rx(L0,y0)),y0,round(rx(L0,y1)),y1,'m3')
    # thickness (front face)
    xl,xr=round(rx(L0,y1)),round(rx(R0,y1))
    s.rect(xl,y1+1,xr,y1+3,'m0'); s.hl(xl,xr,y1+1,'m1')
    # rolled end lying across the back edge: tube with a visible spiral end
    xl,xr=round(rx(L0,y0)),round(rx(R0,y0))
    s.rect(xl+3,y0-9,xr,y0,'m2'); s.hl(xl+3,xr,y0-9,'m3'); s.hl(xl+3,xr,y0-8,'m3'); s.hl(xl+3,xr,y0,'m0')
    for x in range(xl+8,xr,9): s.vl(x,y0-6,y0-1,'m1')
    s.ell(xl+3,y0-4.5,4,5,None,lambda d,x,y:'m0' if d<0.25 else ('m2' if d<0.6 else 'm1'))
    s.put(xl+3,y0-5,'m3')
    s.outline(); shadow(s,(xl+xr)//2-6,y1+5,74,4,110); return s

# ---------- OBJECTS ----------
def obj_career_planner():
    s=L(); box(s,88,108,121,129,30,32,'nv1','nv0','nv0')
    p,q=PJ(88,129,32),PJ(108,129,32); s.hl(p[0],q[0],p[1],'nv2')
    a,b=PJ(103,121,32),PJ(103,129,32); s.line(a[0],a[1],b[0],b[1],'gold')
    fl(s,88,108,129,30,'pp2'); return s.outline()

def obj_career_desk_lamp():
    s=L(); x,y=PJ(126,123,30)
    s.rect(x-6,y-3,x+6,y,'g1'); s.hl(x-6,x+6,y-3,'g2')
    s.line(x,y-4,x-8,y-20,'g2',2); s.line(x-8,y-20,x+2,y-28,'g2',2)
    s.poly([(x-2,y-30),(x+10,y-30),(x+12,y-20),(x-4,y-20)],'ls1'); s.hl(x-2,x+10,y-30,'ls2'); s.hl(x-4,x+12,y-20,'ls0'); return s.outline()

def obj_learning_first_book():
    s=L(); box(s,162,184,121,128,40,44,'rd1','rd0','rd0')
    p,q=PJ(162,128,44),PJ(184,128,44); s.hl(p[0],q[0],p[1],'rd2'); fl(s,163,184,128,41,'pp')
    p=PJ(168,124,44); s.hl(p[0],p[0]+4,p[1],'gold'); return s.outline()

def obj_learning_study_lamp():
    s=L(); x,y=PJ(190,124,40)
    s.rect(x-5,y-3,x+5,y,'g1'); s.line(x,y-4,x,y-17,'g2',2)
    s.poly([(x-7,y-25),(x+7,y-25),(x+10,y-17),(x-10,y-17)],'ls1'); s.hl(x-7,x+7,y-25,'ls2'); s.hl(x-10,x+10,y-17,'ls0'); return s.outline()

def obj_creativity_sketchbook():
    s=L(); box(s,308,328,121,129,28,32,'or1','or0','or0')
    p,q=PJ(308,129,32),PJ(328,129,32); s.hl(p[0],q[0],p[1],'or2'); fl(s,309,328,129,29,'pp')
    a,b=PJ(318,123,32),PJ(326,120,32); s.line(a[0],a[1]-1,b[0]+2,b[1]-3,'gold'); return s.outline()

def obj_creativity_desk_lamp():
    s=L(); x,y=PJ(334,124,28)
    s.rect(x-5,y-3,x+5,y,'g1'); s.line(x,y-4,x,y-19,'g2',2)
    s.poly([(x-7,y-27),(x+7,y-27),(x+10,y-19),(x-10,y-19)],'ls1'); s.hl(x-7,x+7,y-27,'ls2'); s.hl(x-10,x+10,y-19,'ls0'); return s.outline()

def obj_sleep_pillow():
    s=L()
    f=lambda d,x,y:'pi2' if d<0.35 else ('pi1' if d<0.8 else 'pi0')
    for xb in (365,395):
        x,y=PJ(xb,125,20); s.ell(x,y,13,4,None,f)
    return s.outline()
def obj_sleep_bedside_lamp():
    s=L(); x,y=PJ(425,125,18)
    s.rect(x-5,y-6,x+5,y,'pot1'); s.hl(x-5,x+5,y-6,'or2'); s.rect(x-2,y-11,x+2,y-7,'g2')
    s.poly([(x-6,y-23),(x+6,y-23),(x+9,y-12),(x-9,y-12)],'ls1'); s.hl(x-6,x+6,y-23,'ls2'); s.hl(x-9,x+9,y-12,'ls0')
    return s.outline()
def obj_fitness_water_bottle():
    s=L(); s.rect(186,196,193,218,'bt1'); s.vl(186,196,218,'bt2'); s.vl(193,196,218,'bt0')
    s.rect(187,192,192,195,'g0'); s.hl(187,192,192,'g1'); s.rect(186,204,193,206,'bt0'); s.hl(186,193,219,'bt0'); s.outline(); shadow(s,191,221,6,2,150); return s
def obj_fitness_dumbbells():
    s=L()
    for oy in (214,226):
        s.rect(118,oy,121,oy+6,'g1'); s.rect(140,oy,143,oy+6,'g1'); s.hl(118,121,oy,'g3'); s.hl(140,143,oy,'g3')
        s.rect(122,oy+2,139,oy+4,'g2'); s.hl(122,139,oy+2,'g3')
    return s.outline()

ZONES={
 'work_desk':dict(path='career',prop=prop_work_desk,objs=[('career_planner',obj_career_planner),('career_desk_lamp',obj_career_desk_lamp)],
   footprint=[(10,60),(150,60),(150,170),(10,170)],light=(214,226,255),pool=(84,110,74,52),marker=(140,64)),
 'learning_corner':dict(path='learning',prop=prop_learning_corner,objs=[('learning_first_book',obj_learning_first_book),('learning_study_lamp',obj_learning_study_lamp)],
   footprint=[(150,52),(212,52),(242,100),(242,165),(150,165)],light=(140,190,255),pool=(196,112,50,50),marker=(206,52)),
 'creative_corner':dict(path='creativity',prop=prop_creative_corner,objs=[('creativity_sketchbook',obj_creativity_sketchbook),('creativity_desk_lamp',obj_creativity_desk_lamp)],
   footprint=[(256,48),(346,48),(346,172),(250,172),(242,100)],light=(255,196,110),pool=(302,112,58,54),marker=(312,52)),
 'sleep_corner':dict(path='sleep',prop=prop_sleep_corner,objs=[('sleep_pillow',obj_sleep_pillow),('sleep_bedside_lamp',obj_sleep_bedside_lamp)],
   footprint=[(346,70),(476,70),(476,200),(346,200)],light=(190,160,255),pool=(410,135,66,56),marker=(462,86)),
 'fitness_corner':dict(path='fitness',prop=prop_fitness_corner,objs=[('fitness_water_bottle',obj_fitness_water_bottle),('fitness_dumbbells',obj_fitness_dumbbells)],
   footprint=[(16,186),(204,186),(204,252),(16,252)],light=(150,240,190),pool=(112,222,92,40),marker=(196,190)),
}
ORDER=['work_desk','learning_corner','creative_corner','sleep_corner','fitness_corner']
