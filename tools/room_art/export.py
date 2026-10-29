import json, os, shutil
from PIL import Image
from lib import *
import scene, sprites
from render import light, moonshaft, dim, vignette
OUT='export/room'; shutil.rmtree('export',ignore_errors=True)
for d in ('props','objects','ringo','markers','lights'): os.makedirs(f'{OUT}/{d}')
def save_trim(im,path):
    b=im.getbbox(); im.crop(b).save(path); return b
# stage 0: room + static ambient (moon cast, window halo, zone pockets, vignette)
st=scene.stage0().im.copy(); moonshaft(st,0.18)
light(st,242,46,52,44,(150,190,255),0.16)
for zk in scene.ORDER:
    cx,cy,rx,ry=scene.ZONES[zk]['pool']; light(st,cx,cy,rx*0.9,ry*0.9,scene.ZONES[zk]['light'],0.15)
st.save(f'{OUT}/room_stage0.png')
# vignette as separate top overlay (black with alpha)
vg=Image.new('RGBA',(W,H),(255,255,255,255)); vignette(vg); p=vg.load()
for y in range(H):
    for x in range(W):
        r=p[x,y][0]; p[x,y]=(0,0,0,255-r)
vg.save(f'{OUT}/vignette.png')
SLOT={'work_desk':('work_desk_first_reward','work_desk_consistency'),'learning_corner':('learning_corner_first_reward','learning_corner_consistency'),
'creative_corner':('creative_corner_first_reward','creative_corner_consistency'),'sleep_corner':('sleep_corner_first_reward','sleep_corner_consistency'),
'fitness_corner':('fitness_corner_first_reward','fitness_corner_consistency')}
layout={'version':1,'base':{'width':W,'height':H},'safe_area':{'y0':10,'y1':252},'keep_clear':{'window':[207,12,277,86],'rug':[205,185,346,246]},'perspective':{'vanishing_point':[240,-60],'wall_floor_y':118,
 'note':'Floor projection: x=240+(xb-240)*k, y=yf-h*k, k=(yf+60)/178. New art must use the same projection.'},
 'stage':'room_stage0.png','overlay':'vignette.png',
 'ghost':{'opacity':0.38,'filter':'grayscale(1) brightness(1.5) sepia(.2) hue-rotate(180deg)','mask':'2x2 checker'},
 'selected':{'others_dim':0.62,'light_blend':'screen'},'rest':{'room_dim':0.74,'ringo':'sleeping','ringo_pos':'A'},
 'ringo_positions':{'A':[270,214],'B':[372,246],'C':[150,240]},
 'ringo_sprites':{},'markers':{},'zones':{}}
# B30: path marker centres (base px, outside the props); 'tray' is reserved for a later slice.
PATH_MARKER={'work_desk':(78,46),'learning_corner':(160,47),'creative_corner':(311,46),'sleep_corner':(398,47),'fitness_corner':(78,174)}
# B30 S2: compact challenge tray per zone (D45): flag-tab centre (base px) and the side the list
# runs to; run = clear length (base px) along that row from the flag edge, wrap = an optional
# second row (dy, run; over_props = may cover furniture, D45 fallback). Checked by test:room-trays.
TRAY={"work_desk":{"flag":[103,42],"dir":"right","run":109},"learning_corner":{"flag":[139,46],"dir":"left","run":146},"creative_corner":{"flag":[336,46],"dir":"right","run":151},"sleep_corner":{"flag":[377,46],"dir":"left","run":94},"fitness_corner":{"flag":[103,174],"dir":"right","run":107,"wrap":{"dy":-27,"run":299,"over_props":True}}}
def cam(zk):
    cx,cy,_,_=scene.ZONES[zk]['pool']; w,h=195,135
    x0=min(max(0,cx-w//2),W-w); y0=min(max(0,cy-h//2-6),H-h); return [x0,y0,w,h]
for zk in scene.ORDER:
    z=scene.ZONES[zk]
    b=save_trim(z['prop']().im,f'{OUT}/props/prop_{zk}.png')
    slots={}
    for (ak,fn),sk in zip(z['objs'],SLOT[zk]):
        ob=save_trim(fn().im,f'{OUT}/objects/{ak}.png'); slots[sk]={'asset_key':ak,'x':ob[0],'y':ob[1],'w':ob[2]-ob[0],'h':ob[3]-ob[1]}
    # light pool (screen blend) and dim mask for the selected state
    lt=Image.new('RGBA',(W,H),(0,0,0,255)); cx,cy,rx,ry=z['pool']; light(lt,cx,cy,rx,ry,z['light'],0.62)
    lb=lt.getbbox() or (0,0,1,1); lt.crop(lb).save(f'{OUT}/lights/light_{zk}.png')
    dm=Image.new('RGBA',(W,H),(255,255,255,255)); dim(dm,z['pool']); dp=dm.load()
    for y in range(H):
        for x in range(W): r=dp[x,y][0]; dp[x,y]=(0,0,0,255-r)
    dm.save(f'{OUT}/lights/dim_{zk}.png')
    layout['zones'][zk]={'path':z['path'],'footprint':z['footprint'],'prop':{'file':f'props/prop_{zk}.png','x':b[0],'y':b[1]},
      'slots':slots,'light':{'file':f'lights/light_{zk}.png','x':lb[0],'y':lb[1],'color':'#%02x%02x%02x'%z['light'],'pool':list(z['pool'])},
      'dim':f'lights/dim_{zk}.png','path_marker':list(PATH_MARKER[zk]),'tray':TRAY.get(zk),'camera':cam(zk)}
for st_,rows in (('idle',sprites.IDLE),('sleeping',sprites.SLEEP)):
    sp=sprites.sprite(rows).im; sp.save(f'{OUT}/ringo/ringo_{st_}.png')
    layout['ringo_sprites'][st_]={'file':f'ringo/ringo_{st_}.png','anchor':'bottom-center','w':sp.width,'h':sp.height}
# #394: the bell markers are gone (B30 path markers replaced them); only the glint is exported.
sprites.glint().im.save(f'{OUT}/markers/glint.png')
layout['markers']={'glint':'markers/glint.png','anchor':'center'}
# B34 (D68): reminder clock next to Ringo's resting spot A, top-left anchor in base px. The art is
# placeholder pixel art provided by Amir (assets/room/clock/), not drawn by this script.
layout['reminder_clock']={'x':300,'y':196,'w':16,'h':18,'set':'clock/clock_set_16x18.png','ring':'clock/clock_ring_16x18.png'}
json.dump(layout,open(f'{OUT}/room_layout.json','w'),indent=2)
