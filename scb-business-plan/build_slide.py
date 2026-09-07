# -*- coding: utf-8 -*-
"""Build a single-slide .pptx summarizing the SCB five-year business plan.
Hand-writes OOXML (no external deps) and zips it into a valid .pptx."""
import zipfile, os

EMU = 914400  # per inch

# ---- palette ----
NAVY   = "16294B"
NAVY2  = "20406F"
TEAL   = "127B8C"
TEALLT = "39A7B2"
GOLD   = "C79236"
CARDBG = "EEF2F8"
CARDLN = "D3DCEA"
INK    = "24303F"
MUT    = "5B6A7E"
WHITE  = "FFFFFF"

def emu(inch):
    return int(round(inch * EMU))

def esc(t):
    return (t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

def run(text, sz, color, bold=False, font="Calibri", italic=False, spc=None):
    b = ' b="1"' if bold else ''
    i = ' i="1"' if italic else ''
    s = f' spc="{spc}"' if spc is not None else ''
    return (f'<a:r><a:rPr lang="en-US" sz="{sz}"{b}{i}{s} dirty="0">'
            f'<a:solidFill><a:srgbClr val="{color}"/></a:solidFill>'
            f'<a:latin typeface="{font}"/></a:rPr>'
            f'<a:t>{esc(text)}</a:t></a:r>')

def para(runs, align="l", bullet=False, space_before=0, space_after=0, line=None):
    algn = f' algn="{align}"' if align else ''
    marL = ' marL="164000" indent="-164000"' if bullet else ''
    bu = ('<a:buFont typeface="Arial"/><a:buChar char="•"/>' if bullet
          else '<a:buNone/>')
    sb = f'<a:spcBef><a:spcPts val="{space_before}"/></a:spcBef>' if space_before else ''
    sa = f'<a:spcAft><a:spcPts val="{space_after}"/></a:spcAft>' if space_after else ''
    ln = f'<a:lnSpc><a:spcPct val="{line}"/></a:lnSpc>' if line else ''
    return (f'<a:p><a:pPr{marL}{algn}>{ln}{sb}{sa}{bu}</a:pPr>'
            + "".join(runs) + '</a:p>')

_id = [1]
def nid():
    _id[0] += 1
    return _id[0]

def txbox(x, y, w, h, paras, anchor="t", wrap=True, mL=0.06, mR=0.06, mT=0.03, mB=0.03):
    w_ = ' wrap="square"' if wrap else ' wrap="none"'
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{nid()}" name="tx{nid()}"/>'
            f'<p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr><a:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/>'
            f'<a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm>'
            f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr>'
            f'<p:txBody><a:bodyPr{w_} lIns="{emu(mL)}" tIns="{emu(mT)}" '
            f'rIns="{emu(mR)}" bIns="{emu(mB)}" anchor="{anchor}"/>'
            f'<a:lstStyle/>' + "".join(paras) + '</p:txBody></p:sp>')

def rect(x, y, w, h, fill, line=None, lw=1.0, rounded=False, shadow=False):
    geom = "roundRect" if rounded else "rect"
    av = '<a:avLst><a:gd name="adj" fmla="val 8000"/></a:avLst>' if rounded else '<a:avLst/>'
    ln = ''
    if line:
        ln = (f'<a:ln w="{emu(lw/72.0)}"><a:solidFill>'
              f'<a:srgbClr val="{line}"/></a:solidFill></a:ln>')
    sh = ''
    if shadow:
        sh = ('<a:effectLst><a:outerShdw blurRad="90000" dist="38100" dir="5400000" '
              'rotWithShape="0"><a:srgbClr val="1A2233"><a:alpha val="26000"/>'
              '</a:srgbClr></a:outerShdw></a:effectLst>')
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{nid()}" name="rc{nid()}"/>'
            f'<p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr><a:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/>'
            f'<a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm>'
            f'<a:prstGeom prst="{geom}">{av}</a:prstGeom>'
            f'<a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>{ln}{sh}'
            f'</p:spPr><p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody></p:sp>')

def circle(x, y, d, fill, text, sz, tcolor):
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{nid()}" name="cir{nid()}"/>'
            f'<p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr><a:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/>'
            f'<a:ext cx="{emu(d)}" cy="{emu(d)}"/></a:xfrm>'
            f'<a:prstGeom prst="ellipse"><a:avLst/></a:prstGeom>'
            f'<a:solidFill><a:srgbClr val="{fill}"/></a:solidFill></p:spPr>'
            f'<p:txBody><a:bodyPr anchor="ctr" lIns="0" tIns="0" rIns="0" bIns="0"/>'
            f'<a:lstStyle/>'
            + para([run(text, sz, tcolor, bold=True)], align="ctr")
            + '</p:txBody></p:sp>')

# ---------------- content ----------------
directions = [
    ("1", "Digital Assets & Crypto",
     "Spot BTC/ETH & crypto NDF live; custody (Anchorage, Zodia), HKDAP stablecoin. Grow into tokenized deposits, securities, treasury & 24×7 custody."),
    ("2", "24×7 Trading Architecture",
     "MX.3 next-gen for 24×7 & real-time settlement; cloud-native dev/test, active-active HA, MxEvolve; Razor sustains higher FX volumes."),
    ("3", "Derivatives Strategy",
     "Conclude 2.11 exit; amortize lost maintenance; shift to rental licensing; phased return-to-platform gated on FMRP delivery."),
    ("4", "Securities Finance & Repo",
     "Consolidate systems; challenge APEX / BBG / Broadridge across repo, loan trading, stock borrow-lend & collateral optimization."),
    ("5", "Wealth Management",
     "Explore a differentiated MX.3 / Razor use case to challenge Temenos — a space outside the FMRP plan."),
    ("6", "Platform Modernization",
     "Keep Razor top-tier for FX: OSP heat map, more frequent patches, CI/CD alignment and an evergreen upgrade model."),
    ("7", "Regulatory Resilience",
     "Recurring services on DORA, RRP / BRRD, operational resilience, CVE remediation and regulatory reporting."),
]

phases = [
    ("FY 2027", "Secure the base", TEALLT, [
        "Conclude 2.11 commercial discussions",
        "Obtain PDD direction on 24×7 architecture",
        "Stabilize & modernize Razor (heat map, CVEs, FX volume)",
        "Confirm digital-assets & stablecoin path",
        "Qualify Securities Finance & Wealth opportunities",
        "Launch upgrade program; DORA / RRP resilience",
    ]),
    ("FY 2028–2029", "Transform & prove", TEAL, [
        "Pilot 24×7, HA, MxEvolve & cloud dev/test",
        "Move digital assets toward native implementation",
        "Run Securities Finance discovery & pre-scoping",
        "Prove a differentiated Wealth use case on Razor",
        "Define return-to-platform & rental-model options",
    ]),
    ("FY 2030–2031", "Scale & expand", GOLD, [
        "Industrialize the 24×7 operating model",
        "Expand tokenized deposits, securities, custody, treasury",
        "Establish SecFin & multi-asset collateral footprint",
        "Progress Wealth Management platform positioning",
        "Embed evergreen modernization & resilience services",
    ]),
]

# ---------------- layout ----------------
SW, SH = 13.333, 7.5
shapes = []

# background
shapes.append(rect(0, 0, SW, SH, WHITE))

# title
shapes.append(txbox(0.45, 0.30, 12.4, 0.55,
    [para([run("SCB — Five-Year Business Plan", 2600, NAVY, bold=True, font="Cambria")],
          align="l")], anchor="t", mL=0.02))
shapes.append(txbox(0.47, 0.90, 12.4, 0.34,
    [para([run("Seven strategic directions delivered across a phased FY2027 – FY2031 roadmap",
               1250, MUT)], align="l")], anchor="t", mL=0.02))

# ---- 7 direction cards ----
n = 7
left, right_m = 0.45, 0.45
gap = 0.14
cw = (SW - left - right_m - gap * (n - 1)) / n
cy, ch = 1.45, 2.32
for i, (num, title, desc) in enumerate(directions):
    cx = left + i * (cw + gap)
    shapes.append(rect(cx, cy, cw, ch, CARDBG, line=CARDLN, lw=1.0, rounded=True, shadow=True))
    # badge
    d = 0.44
    shapes.append(circle(cx + 0.14, cy + 0.16, d, TEAL, num, 1500, WHITE))
    # title
    shapes.append(txbox(cx + 0.02, cy + 0.66, cw - 0.04, 0.62,
        [para([run(title, 1050, NAVY, bold=True)], align="l", line="98000")],
        anchor="t", mL=0.11, mR=0.06))
    # descriptor
    shapes.append(txbox(cx + 0.02, cy + 1.24, cw - 0.04, ch - 1.30,
        [para([run(desc, 800, INK)], align="l", line="104000")],
        anchor="t", mL=0.11, mR=0.08))

# ---- roadmap label ----
ry_label = 4.02
shapes.append(txbox(0.45, ry_label, 12.4, 0.32,
    [para([run("PHASED ROADMAP", 1250, TEAL, bold=True, spc=180),
           run("      FY2027  →  FY2031", 1250, MUT, bold=False)],
          align="l")], anchor="t", mL=0.02))

# ---- 3 phase columns ----
pn = 3
pgap = 0.30
pw = (SW - left - right_m - pgap * (pn - 1)) / pn
py, phh = 4.42, 2.74
for j, (tag, ptitle, tagcol, bullets) in enumerate(phases):
    px = left + j * (pw + pgap)
    shapes.append(rect(px, py, pw, phh, NAVY, rounded=True, shadow=True))
    # accent chip
    shapes.append(circle(px + 0.22, py + 0.24, 0.16, tagcol, "", 900, NAVY))
    # tag
    shapes.append(txbox(px + 0.44, py + 0.15, pw - 0.6, 0.32,
        [para([run(tag, 1200, tagcol, bold=True, spc=60)], align="l")],
        anchor="ctr", mL=0.0))
    # phase title
    shapes.append(txbox(px + 0.20, py + 0.50, pw - 0.4, 0.42,
        [para([run(ptitle, 1600, WHITE, bold=True, font="Cambria")], align="l")],
        anchor="t", mL=0.0))
    # bullets
    bparas = [para([run(b, 900, "DCE4F0")], align="l", bullet=True,
                   space_after=400, line="100000") for b in bullets]
    shapes.append(txbox(px + 0.22, py + 1.00, pw - 0.42, phh - 1.10,
        bparas, anchor="t", mL=0.0, mR=0.02))

slide_shapes = "".join(shapes)

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
<p:sldMaster xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:cSld><p:bg><p:bgPr><a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill><a:effectLst/></p:bgPr></p:bg><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr></p:spTree></p:cSld><p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/><p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst><p:txStyles><p:titleStyle><a:lvl1pPr><a:defRPr sz="2400"><a:solidFill><a:srgbClr val="16294B"/></a:solidFill><a:latin typeface="Calibri"/></a:defRPr></a:lvl1pPr></p:titleStyle><p:bodyStyle><a:lvl1pPr><a:defRPr sz="1400"><a:solidFill><a:srgbClr val="24303F"/></a:solidFill><a:latin typeface="Calibri"/></a:defRPr></a:lvl1pPr></p:bodyStyle><p:otherStyle><a:lvl1pPr><a:defRPr sz="1400"><a:latin typeface="Calibri"/></a:defRPr></a:lvl1pPr></p:otherStyle></p:txStyles></p:sldMaster>'''

SLIDE_MASTER_RELS = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="../theme/theme1.xml"/></Relationships>'''

SLIDE_LAYOUT = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldLayout xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" type="blank" preserve="1"><p:cSld name="Blank"><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr></p:spTree></p:cSld><p:clrMapOvr><a:overrideClrMapping bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/></p:clrMapOvr></p:sldLayout>'''

SLIDE_LAYOUT_RELS = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/></Relationships>'''

THEME = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="Office Theme"><a:themeElements><a:clrScheme name="Office"><a:dk1><a:sysClr val="windowText" lastClr="000000"/></a:dk1><a:lt1><a:sysClr val="window" lastClr="FFFFFF"/></a:lt1><a:dk2><a:srgbClr val="16294B"/></a:dk2><a:lt2><a:srgbClr val="EEF2F8"/></a:lt2><a:accent1><a:srgbClr val="127B8C"/></a:accent1><a:accent2><a:srgbClr val="39A7B2"/></a:accent2><a:accent3><a:srgbClr val="C79236"/></a:accent3><a:accent4><a:srgbClr val="20406F"/></a:accent4><a:accent5><a:srgbClr val="5B6A7E"/></a:accent5><a:accent6><a:srgbClr val="D3DCEA"/></a:accent6><a:hlink><a:srgbClr val="127B8C"/></a:hlink><a:folHlink><a:srgbClr val="20406F"/></a:folHlink></a:clrScheme><a:fontScheme name="Office"><a:majorFont><a:latin typeface="Cambria"/><a:ea typeface=""/><a:cs typeface=""/></a:majorFont><a:minorFont><a:latin typeface="Calibri"/><a:ea typeface=""/><a:cs typeface=""/></a:minorFont></a:fontScheme><a:fmtScheme name="Office"><a:fillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:fillStyleLst><a:lnStyleLst><a:ln w="9525" cap="flat" cmpd="sng" algn="ctr"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:prstDash val="solid"/></a:ln><a:ln w="9525" cap="flat" cmpd="sng" algn="ctr"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:prstDash val="solid"/></a:ln><a:ln w="9525" cap="flat" cmpd="sng" algn="ctr"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:prstDash val="solid"/></a:ln></a:lnStyleLst><a:effectStyleLst><a:effectStyle><a:effectLst/></a:effectStyle><a:effectStyle><a:effectLst/></a:effectStyle><a:effectStyle><a:effectLst/></a:effectStyle></a:effectStyleLst><a:bgFillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:bgFillStyleLst></a:fmtScheme></a:themeElements><a:objectDefaults/><a:extraClrSchemeLst/></a:theme>'''

CORE = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><dc:title>SCB Five-Year Business Plan - Strategic Directions</dc:title></cp:coreProperties>'''

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
