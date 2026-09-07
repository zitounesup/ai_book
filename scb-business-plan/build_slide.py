# -*- coding: utf-8 -*-
"""Build a single-slide .pptx presenting the SCB five-year business plan as an
ascending timeline flow (FY2027 -> FY2031). Hand-writes OOXML (no external
deps) and zips it into a valid .pptx."""
import zipfile, os

EMU = 914400  # per inch

# ---- palette (dark / premium) ----
BG1    = "0E1B33"   # gradient top-left
BG2    = "1C3A66"   # gradient bottom-right
CARD   = "1B3358"   # phase panel fill
CARDLN = "33517E"   # panel border
CHIP   = "213A60"   # pillar chip fill
CHIPLN = "35547F"   # pillar chip border
TEAL   = "17A2B8"   # primary accent
TEALLT = "45C4D4"   # light accent
GOLD   = "E0A93B"   # phase-3 accent
WHITE  = "FFFFFF"
ICE    = "DCE7F6"   # body text on dark
MUT    = "9DB2D2"   # muted text
NAVYTX = "0E1B33"

def emu(inch): return int(round(inch * EMU))

def esc(t): return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

_id = [1]
def nid():
    _id[0] += 1
    return _id[0]

def run(text, sz, color, bold=False, font="Calibri", italic=False, spc=None):
    b = ' b="1"' if bold else ''
    i = ' i="1"' if italic else ''
    s = f' spc="{spc}"' if spc is not None else ''
    return (f'<a:r><a:rPr lang="en-US" sz="{sz}"{b}{i}{s} dirty="0">'
            f'<a:solidFill><a:srgbClr val="{color}"/></a:solidFill>'
            f'<a:latin typeface="{font}"/></a:rPr><a:t>{esc(text)}</a:t></a:r>')

def para(runs, align="l", bullet=False, bucolor=None, space_after=0, line=None):
    algn = f' algn="{align}"' if align else ''
    marL = ' marL="155000" indent="-155000"' if bullet else ''
    if bullet:
        buc = f'<a:buClr><a:srgbClr val="{bucolor}"/></a:buClr>' if bucolor else ''
        bu = f'{buc}<a:buFont typeface="Arial"/><a:buChar char="&#8226;"/>'
    else:
        bu = '<a:buNone/>'
    sa = f'<a:spcAft><a:spcPts val="{space_after}"/></a:spcAft>' if space_after else ''
    ln = f'<a:lnSpc><a:spcPct val="{line}"/></a:lnSpc>' if line else ''
    return (f'<a:p><a:pPr{marL}{algn}>{ln}{sa}{bu}</a:pPr>' + "".join(runs) + '</a:p>')

def txbox(x, y, w, h, paras, anchor="t", wrap=True, mL=0.06, mR=0.06, mT=0.02, mB=0.02):
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{nid()}" name="tx{nid()}"/>'
            f'<p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr><a:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/>'
            f'<a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm>'
            f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr>'
            f'<p:txBody><a:bodyPr wrap="square" lIns="{emu(mL)}" tIns="{emu(mT)}" '
            f'rIns="{emu(mR)}" bIns="{emu(mB)}" anchor="{anchor}"/>'
            f'<a:lstStyle/>' + "".join(paras) + '</p:txBody></p:sp>')

def _fill(fill):
    if isinstance(fill, tuple):  # gradient (c1, c2, angle_deg)
        c1, c2, ang = fill
        return (f'<a:gradFill><a:gsLst>'
                f'<a:gs pos="0"><a:srgbClr val="{c1}"/></a:gs>'
                f'<a:gs pos="100000"><a:srgbClr val="{c2}"/></a:gs>'
                f'</a:gsLst><a:lin ang="{int(ang*60000)}" scaled="1"/></a:gradFill>')
    return f'<a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>'

def shape(x, y, w, h, fill, prst="rect", line=None, lw=1.0, shadow=False,
          rot=None, adj=None, paras=None, anchor="ctr"):
    av = adj if adj else '<a:avLst/>'
    ln = ''
    if line:
        ln = (f'<a:ln w="{emu(lw/72.0)}"><a:solidFill>'
              f'<a:srgbClr val="{line}"/></a:solidFill></a:ln>')
    sh = ''
    if shadow:
        sh = ('<a:effectLst><a:outerShdw blurRad="120000" dist="45000" dir="5400000" '
              'rotWithShape="0"><a:srgbClr val="000000"><a:alpha val="34000"/>'
              '</a:srgbClr></a:outerShdw></a:effectLst>')
    r = f' rot="{rot}"' if rot is not None else ''
    body = ("".join(paras) if paras else '<a:p/>')
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{nid()}" name="s{nid()}"/>'
            f'<p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr><a:xfrm{r}><a:off x="{emu(x)}" y="{emu(y)}"/>'
            f'<a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm>'
            f'<a:prstGeom prst="{prst}">{av}</a:prstGeom>{_fill(fill)}{ln}{sh}'
            f'</p:spPr><p:txBody>'
            f'<a:bodyPr anchor="{anchor}" lIns="0" tIns="0" rIns="0" bIns="0"/>'
            f'<a:lstStyle/>{body}</p:txBody></p:sp>')

# ---------------- content ----------------
pillars = ["Digital Assets", "24×7 Architecture", "Derivatives",
           "Securities Finance", "Wealth Mgmt", "Modernization", "Reg. Resilience"]

phases = [
    ("FY 2027", "Secure the base", "01", TEALLT, [
        "Conclude the 2.11 exit; move to rental licensing",
        "Secure PDD direction on 24×7 architecture",
        "Stabilize & modernize Razor (heat map, CVEs)",
        "Confirm digital-assets path; DORA / RRP resilience",
    ]),
    ("FY 2028–2029", "Transform & prove", "02", TEAL, [
        "Pilot 24×7, HA, MxEvolve & cloud dev/test",
        "Move digital assets toward native implementation",
        "Securities Finance discovery & pre-scoping",
        "Prove Wealth use case; define return-to-platform",
    ]),
    ("FY 2030–2031", "Scale & expand", "03", GOLD, [
        "Industrialize the 24×7 operating model",
        "Expand tokenized deposits, securities & custody",
        "Establish SecFin & multi-asset collateral footprint",
        "Advance Wealth; embed evergreen modernization",
    ]),
]

# ---------------- layout ----------------
SW, SH = 13.333, 7.5
S = []

# background gradient
S.append(shape(0, 0, SW, SH, (BG1, BG2, 45), prst="rect"))

# header
S.append(txbox(0.55, 0.34, 9.6, 0.55,
    [para([run("SCB — Five-Year Business Plan", 2600, WHITE, bold=True, font="Cambria")])],
    anchor="t", mL=0.02))
S.append(txbox(0.57, 0.92, 9.6, 0.32,
    [para([run("A phased journey across seven strategic directions",
               1250, MUT)])], anchor="t", mL=0.02))
# journey tagline (right)
S.append(shape(9.63, 0.44, 3.15, 0.52, CARD, prst="roundRect",
    adj='<a:avLst><a:gd name="adj" fmla="val 50000"/></a:avLst>', line=CARDLN, lw=1.0,
    paras=[para([run("SECURE ", 1050, TEALLT, bold=True, spc=40),
                 run("→ TRANSFORM ", 1050, TEAL, bold=True, spc=40),
                 run("→ SCALE", 1050, GOLD, bold=True, spc=40)], align="ctr")]))

# ---- pillars strip ----
S.append(txbox(0.55, 1.34, 9, 0.26,
    [para([run("SEVEN STRATEGIC DIRECTIONS", 1000, TEALLT, bold=True, spc=200)])],
    anchor="t", mL=0.02))
n = 7
left, rm, gap = 0.55, 0.55, 0.13
cw = (SW - left - rm - gap*(n-1))/n
py0, ph0 = 1.66, 0.56
for i, name in enumerate(pillars):
    cx = left + i*(cw+gap)
    S.append(shape(cx, py0, cw, ph0, CHIP, prst="roundRect",
        adj='<a:avLst><a:gd name="adj" fmla="val 16000"/></a:avLst>', line=CHIPLN, lw=1.0))
    # accent dot
    S.append(shape(cx+0.12, py0+ph0/2-0.05, 0.10, 0.10, TEAL, prst="ellipse"))
    S.append(txbox(cx+0.26, py0, cw-0.32, ph0,
        [para([run(name, 900, ICE, bold=True)], align="l", line="96000")],
        anchor="ctr", mL=0.0, mR=0.02))

# ---- ascending phase flow ----
pw = 3.5
pgap = 0.83
px = [0.60, 0.60+pw+pgap, 0.60+2*(pw+pgap)]     # 0.60, 4.93, 9.26
tops = [3.42, 2.86, 2.30]                        # ascending
phh = 2.72

# connecting arrows (drawn first, behind cards)
def card_center(idx): return (px[idx]+pw/2, tops[idx]+phh/2)
for k in range(2):
    x0, y0 = px[k]+pw, tops[k]+phh/2
    x1 = px[k+1]
    aw, ah = 0.82, 0.5
    ax = (x0 + x1)/2 - aw/2
    ay = ((tops[k]+phh/2) + (tops[k+1]+phh/2))/2 - ah/2
    S.append(shape(ax, ay, aw, ah, TEAL, prst="rightArrow",
        adj='<a:avLst><a:gd name="adj1" fmla="val 55000"/><a:gd name="adj2" fmla="val 55000"/></a:avLst>',
        rot=20050000, shadow=False))

for j, (tag, title, num, acc, bullets) in enumerate(phases):
    x, y = px[j], tops[j]
    S.append(shape(x, y, pw, phh, CARD, prst="roundRect",
        adj='<a:avLst><a:gd name="adj" fmla="val 7000"/></a:avLst>',
        line=CARDLN, lw=1.25, shadow=True))
    # phase number badge
    d = 0.56
    S.append(shape(x+0.20, y+0.20, d, d, acc, prst="ellipse",
        paras=[para([run(num, 1500, NAVYTX, bold=True, font="Cambria")], align="ctr")]))
    # year tag + title
    S.append(txbox(x+0.86, y+0.22, pw-1.0, 0.30,
        [para([run(tag, 1200, acc, bold=True, spc=40)])], anchor="ctr", mL=0.0))
    S.append(txbox(x+0.86, y+0.52, pw-1.0, 0.34,
        [para([run(title, 1550, WHITE, bold=True, font="Cambria")])], anchor="ctr", mL=0.0))
    # bullets
    bp = [para([run(b, 900, ICE)], align="l", bullet=True, bucolor=acc,
               space_after=500, line="100000") for b in bullets]
    S.append(txbox(x+0.24, y+1.02, pw-0.46, phh-1.14, bp, anchor="t", mL=0.0, mR=0.02))

# ---- timeline spine (2027 -> 2031) ----
axis_y = 6.42
S.append(shape(0.75, axis_y, SW-1.5, 0.028, CARDLN, prst="roundRect",
    adj='<a:avLst><a:gd name="adj" fmla="val 50000"/></a:avLst>'))
years = ["2027", "2028", "2029", "2030", "2031"]
ycol  = [TEALLT, TEAL, TEAL, GOLD, GOLD]
xs = 0.95
xe = SW-0.95
for i, yr in enumerate(years):
    cxp = xs + i*((xe-xs)/(len(years)-1))
    dd = 0.17
    S.append(shape(cxp-dd/2, axis_y+0.014-dd/2, dd, dd, ycol[i], prst="ellipse",
        line=BG1, lw=1.5))
    S.append(txbox(cxp-0.6, axis_y+0.24, 1.2, 0.34,
        [para([run(yr, 1350, ycol[i], bold=True, font="Cambria")], align="ctr")],
        anchor="t", mL=0.0))

slide_shapes = "".join(S)

# ---------------- package XML ----------------
SLIDE = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>{slide_shapes}</p:spTree></p:cSld><p:clrMapOvr><a:overrideClrMapping bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/></p:clrMapOvr></p:sld>'''

CONTENT_TYPES = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/><Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/><Override PartName="/ppt/slides/slide1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/><Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/><Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/><Override PartName="/ppt/presProps.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presProps+xml"/><Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/><Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/></Types>'''

RELS = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/><Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/></Relationships>'''

PRESENTATION = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/></p:sldMasterIdLst><p:sldIdLst><p:sldId id="256" r:id="rId2"/></p:sldIdLst><p:sldSz cx="{emu(SW)}" cy="{emu(SH)}" type="screen16x9"/><p:notesSz cx="6858000" cy="9144000"/></p:presentation>'''

PRESENTATION_RELS = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide1.xml"/><Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="theme/theme1.xml"/><Relationship Id="rId4" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/presProps" Target="presProps.xml"/></Relationships>'''

PRESPROPS = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentationPr xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"/>'''

SLIDE_RELS = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/></Relationships>'''

SLIDE_MASTER = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldMaster xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:cSld><p:bg><p:bgPr><a:solidFill><a:srgbClr val="0E1B33"/></a:solidFill><a:effectLst/></p:bgPr></p:bg><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr></p:spTree></p:cSld><p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/><p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst><p:txStyles><p:titleStyle><a:lvl1pPr><a:defRPr sz="2400"><a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill><a:latin typeface="Calibri"/></a:defRPr></a:lvl1pPr></p:titleStyle><p:bodyStyle><a:lvl1pPr><a:defRPr sz="1400"><a:solidFill><a:srgbClr val="DCE7F6"/></a:solidFill><a:latin typeface="Calibri"/></a:defRPr></a:lvl1pPr></p:bodyStyle><p:otherStyle><a:lvl1pPr><a:defRPr sz="1400"><a:latin typeface="Calibri"/></a:defRPr></a:lvl1pPr></p:otherStyle></p:txStyles></p:sldMaster>'''

SLIDE_MASTER_RELS = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="../theme/theme1.xml"/></Relationships>'''

SLIDE_LAYOUT = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldLayout xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" type="blank" preserve="1"><p:cSld name="Blank"><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr></p:spTree></p:cSld><p:clrMapOvr><a:overrideClrMapping bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/></p:clrMapOvr></p:sldLayout>'''

SLIDE_LAYOUT_RELS = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/></Relationships>'''

THEME = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="Office Theme"><a:themeElements><a:clrScheme name="Office"><a:dk1><a:sysClr val="windowText" lastClr="000000"/></a:dk1><a:lt1><a:sysClr val="window" lastClr="FFFFFF"/></a:lt1><a:dk2><a:srgbClr val="0E1B33"/></a:dk2><a:lt2><a:srgbClr val="DCE7F6"/></a:lt2><a:accent1><a:srgbClr val="17A2B8"/></a:accent1><a:accent2><a:srgbClr val="45C4D4"/></a:accent2><a:accent3><a:srgbClr val="E0A93B"/></a:accent3><a:accent4><a:srgbClr val="1B3358"/></a:accent4><a:accent5><a:srgbClr val="9DB2D2"/></a:accent5><a:accent6><a:srgbClr val="33517E"/></a:accent6><a:hlink><a:srgbClr val="45C4D4"/></a:hlink><a:folHlink><a:srgbClr val="9DB2D2"/></a:folHlink></a:clrScheme><a:fontScheme name="Office"><a:majorFont><a:latin typeface="Cambria"/><a:ea typeface=""/><a:cs typeface=""/></a:majorFont><a:minorFont><a:latin typeface="Calibri"/><a:ea typeface=""/><a:cs typeface=""/></a:minorFont></a:fontScheme><a:fmtScheme name="Office"><a:fillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:fillStyleLst><a:lnStyleLst><a:ln w="9525" cap="flat" cmpd="sng" algn="ctr"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:prstDash val="solid"/></a:ln><a:ln w="9525" cap="flat" cmpd="sng" algn="ctr"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:prstDash val="solid"/></a:ln><a:ln w="9525" cap="flat" cmpd="sng" algn="ctr"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:prstDash val="solid"/></a:ln></a:lnStyleLst><a:effectStyleLst><a:effectStyle><a:effectLst/></a:effectStyle><a:effectStyle><a:effectLst/></a:effectStyle><a:effectStyle><a:effectLst/></a:effectStyle></a:effectStyleLst><a:bgFillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:bgFillStyleLst></a:fmtScheme></a:themeElements><a:objectDefaults/><a:extraClrSchemeLst/></a:theme>'''

CORE = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><dc:title>SCB Five-Year Business Plan - Roadmap Flow</dc:title></cp:coreProperties>'''

APP = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes"><Application>Microsoft Office PowerPoint</Application><Slides>1</Slides></Properties>'''

files = {
    "[Content_Types].xml": CONTENT_TYPES,
    "_rels/.rels": RELS,
    "docProps/core.xml": CORE,
    "docProps/app.xml": APP,
    "ppt/presentation.xml": PRESENTATION,
    "ppt/_rels/presentation.xml.rels": PRESENTATION_RELS,
    "ppt/presProps.xml": PRESPROPS,
    "ppt/theme/theme1.xml": THEME,
    "ppt/slideMasters/slideMaster1.xml": SLIDE_MASTER,
    "ppt/slideMasters/_rels/slideMaster1.xml.rels": SLIDE_MASTER_RELS,
    "ppt/slideLayouts/slideLayout1.xml": SLIDE_LAYOUT,
    "ppt/slideLayouts/_rels/slideLayout1.xml.rels": SLIDE_LAYOUT_RELS,
    "ppt/slides/slide1.xml": SLIDE,
    "ppt/slides/_rels/slide1.xml.rels": SLIDE_RELS,
}

out = "SCB_Business_Plan_Summary.pptx"
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for name, data in files.items():
        z.writestr(name, data)
print("wrote", out, os.path.getsize(out), "bytes")
