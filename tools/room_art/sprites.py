from lib import *
IDLE=[
"...aa..............aa...",
"..abba............abba..",
"..abcba..........abcba..",
".abccbaaaaaaaaaaaabccba.",
".abbbbbbbbbbbbbbbbbbbba.",
"abbbbbbbbbbbbbbbbbbbbbba",
"abbbbbbbbbbbbbbbbbbbbbba",
"abbcccbbbbbbbbbbbbcccbba",
"abbceepbbbbbbbbbbpeecbba",
"abbceepbbbbbbbbbbpeecbba",
"abbbcccbbbbbbbbbbcccbbba",
"abbbbbbbbbbnnbbbbbbbbbba",
".abbbbbbbbcbbcbbbbbbbba.",
".abbbbbbbbbccbbbbbbbbba.",
"..aabbbbbbbbbbbbbbbbaa..",
"...aaabbbbbbbbbbbbaaa...",
"....hhhhhhhhhhhhhhhh....",
"..hhhhhhhhhhhhhhhhhhhh..",
".hhhhhHhhhhhhhhhHhhhhhh.",
".hhhhHhhhhhhhhhhhHhhhhh.",
"hhhhhHhhhhggggghhhHhhhhh",
"hhhhhHhhhhgGGGghhhHhhhhh",
"hhhhhHhhhhggggghhhHhhhhh",
"hhhhhhhhhhhhhhhhhhhhhhhh",
"hhhhhhhhhhhhhhhhhhhhhhhh......aa",
".hhhhhhhhhhhhhhhhhhhhhh.....abba",
".hhhhhhhhhhhhhhhhhhhhhh....abcba",
"..bbbbbb........bbbbbb....abba..",
".bbcccbb........bbcccbbaaabba...",
".bbbbbbb........bbbbbbbbbbba....",
"..aaaaa..........aaaaa.aaaa.....",
]
SLEEP=[
"....a.....a...................",
"...aba...aba..................",
"..abcbaaabcba.................",
"..abbbbbbbbba..hhhhhhhhhh.....",
".abbbbbbbbbbbahhhhhhhhhhhhh...",
".abbbbbbbbbbbhhhhhhhhhhhhhhh..",
".abkkkbbbkkkbhhhhHhhhhhhhhhhh.",
".abbbbbnbbbbbhhhhHhhhhhhhhhhh.",
"..abbbcbcbbbahhhhhhhhhhhhhhhh.",
"..aabbbbbbbaahhhhhhhhhhhhhhha.",
".abbcbbbbcbbbbbbbbbbbbbbbbbba.",
".aaaaaaaaaaaaaaabbbbbbbccccba.",
".................aaaaaaaaaaa..",
]
CM={'a':'cat0','b':'cat1','c':'cat2','e':'eye','p':'pupil','n':'nose','h':'hood','H':'hood2','g':'gold','G':'gold2','k':'ink'}
def sprite(rows):
    w=max(len(r) for r in rows); s=L(w+2,len(rows)+2)
    for j,r in enumerate(rows):
        for i,ch in enumerate(r):
            if ch in CM: s.put(i+1,j+1,CM[ch])
    return s.outline()
def bell():
    s=L(11,12)
    rows=["....g....","...ggg...","..ggggg..","..ggggg..","..ggggg..",".ggggggg.","ggggggggg","....G...."]
    for j,r in enumerate(rows):
        for i,ch in enumerate(r):
            if ch=='g': s.put(i+1,j+1,'pp')
            if ch=='G': s.put(i+1,j+1,'pp2')
    return s.outline()
def glint():
    s=L(9,9)
    for (x,y,c) in [(4,1,'gold2'),(4,2,'gold'),(4,3,'gold2'),(1,4,'gold2'),(2,4,'gold'),(3,4,'gold2'),(4,4,'pp'),(5,4,'gold2'),(6,4,'gold'),(7,4,'gold2'),(4,5,'gold2'),(4,6,'gold'),(4,7,'gold2')]:
        s.put(x,y,c)
    return s
