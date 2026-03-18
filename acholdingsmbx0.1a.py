#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mario Fan Builder — All-in-One Edition
Extended SMBX 1.3 Editor + pygame-native asset generator, no Pillow needed.
All 33 bugs resolved. Run directly: python mario_fan_builder_all_in_one.py
"""

import pygame
import sys
import os
import math
import struct
import json
import configparser
from collections import deque

# ── CONFIGURATION ──────────────────────────────────────────────────────────────
WINDOW_WIDTH, WINDOW_HEIGHT = 1024, 700
SIDEBAR_WIDTH   = 200
MENU_HEIGHT     = 20
TOOLBAR_HEIGHT  = 26
STATUSBAR_HEIGHT= 24
CANVAS_X        = SIDEBAR_WIDTH
CANVAS_Y        = MENU_HEIGHT + TOOLBAR_HEIGHT
CANVAS_WIDTH    = WINDOW_WIDTH - SIDEBAR_WIDTH
CANVAS_HEIGHT   = WINDOW_HEIGHT - CANVAS_Y - STATUSBAR_HEIGHT

GRID_SIZE = 32
FPS       = 60
ZOOM_MIN, ZOOM_MAX, ZOOM_STEP = 0.25, 4.0, 0.25

# Physics
GRAVITY           =  0.5
JUMP_STRENGTH     = -10
MOVE_SPEED        =  4
TERMINAL_VELOCITY =  10

# System colours
SYS_BG         = (212, 208, 200)
SYS_BTN_FACE   = (212, 208, 200)
SYS_BTN_LIGHT  = (255, 255, 255)
SYS_BTN_DARK   = (128, 128, 128)
SYS_BTN_DK_SHD = ( 64,  64,  64)
SYS_WINDOW     = (255, 255, 255)
SYS_HIGHLIGHT  = (  0,   0, 128)
SYS_HIGHLIGHT2 = ( 51, 153, 255)
SYS_TEXT       = (  0,   0,   0)
WHITE  = (255,255,255);  BLACK  = (0,0,0)
RED    = (255,0,0);      GREEN  = (0,200,0)
BLUE   = (0,0,255);      YELLOW = (255,255,0)
GRAY   = (128,128,128);  SMBX_GRID = (40,40,40)

# Asset paths
SMBX_ASSETS   = "smbx_assets"
TILESET_DIR   = os.path.join(SMBX_ASSETS, "tilesets")
BACKGROUND_DIR= os.path.join(SMBX_ASSETS, "backgrounds")
NPC_GFX_DIR   = os.path.join(SMBX_ASSETS, "npc")
for _d in (TILESET_DIR, BACKGROUND_DIR, NPC_GFX_DIR):
    os.makedirs(_d, exist_ok=True)

# ── SMBX ID MAPPINGS ───────────────────────────────────────────────────────────
TILE_SMBX_IDS = {
    'ground':1,'grass':2,'sand':3,'dirt':4,'brick':45,'question':34,
    'pipe_vertical':112,'pipe_horizontal':113,'platform':159,'coin':10,
    'bridge':47,'stone':48,'ice':55,'mushroom_platform':91,'pswitch':60,
    'slope_left':182,'slope_right':183,'water':196,'lava':197,
    'conveyor_left':188,'conveyor_right':189,'semisolid':190,
}
BGO_SMBX_IDS = {
    'cloud':5,'bush':6,'hill':7,'fence':8,'bush_3':9,'tree':10,
    'castle':11,'waterfall':12,'sign':13,'fence2':14,'fence3':15,
}
NPC_SMBX_IDS = {
    'goomba':1,'koopa_green':2,'koopa_red':3,'paratroopa_green':4,
    'paratroopa_red':5,'piranha':6,'hammer_bro':7,'lakitu':8,
    'mushroom':9,'flower':10,'star':11,'1up':12,'buzzy':13,'spiny':14,
    'cheep':15,'blooper':16,'thwomp':17,'bowser':18,'boo':19,'podoboo':20,
    'piranha_fire':21,'sledge_bro':22,'rotodisc':23,'burner':24,'cannon':25,
    'bullet_bill':26,'bowser_statue':27,'grinder':28,'fishbone':29,
    'dry_bones':30,'boo_ring':31,'bomber_bill':32,'bony_beetle':33,
    'skull_platform':34,'start':196,
}
TILE_ID_TO_NAME = {v:k for k,v in TILE_SMBX_IDS.items()}
BGO_ID_TO_NAME  = {v:k for k,v in BGO_SMBX_IDS.items()}
NPC_ID_TO_NAME  = {v:k for k,v in NPC_SMBX_IDS.items()}

# ── THEMES ─────────────────────────────────────────────────────────────────────
themes = {
    'SMB1': {
        'background':(92,148,252),'ground':(0,128,0),'brick':(180,80,40),
        'question':(255,200,0),'coin':(255,255,0),'pipe_vertical':(0,200,0),
        'pipe_horizontal':(0,180,0),'platform':(139,69,19),'goomba':(200,100,0),
        'koopa_green':(0,200,50),'koopa_red':(200,50,50),'mushroom':(255,0,200),
        'flower':(255,140,0),'star':(255,230,0),'bgo_cloud':(220,220,220),
        'bgo_bush':(0,160,0),'bgo_hill':(100,200,100),'bgo_tree':(0,120,0),
        'grass':(60,180,60),'sand':(220,200,100),'dirt':(150,100,60),
        'stone':(140,140,140),'ice':(160,220,255),'bridge':(160,100,40),
        'mushroom_platform':(200,100,200),'pswitch':(80,80,200),
        'slope_left':(180,180,0),'slope_right':(180,180,0),
        'water':(0,100,255),'lava':(255,80,0),
        'conveyor_left':(100,100,100),'conveyor_right':(100,100,100),
        'semisolid':(150,150,200),
        # BGO fallback colours for types without bgo_ prefix in dict
        'cloud':(220,220,220),'bush':(0,160,0),'hill':(100,200,100),
        'tree':(0,120,0),'fence':(180,150,80),'bush_3':(0,160,0),
        'castle':(140,130,150),'waterfall':(60,120,255),'sign':(200,180,120),
        'fence2':(180,150,80),'fence3':(180,150,80),
    },
    'SMB3': {
        'background':(0,0,0),'ground':(160,120,80),'brick':(180,100,60),
        'question':(255,210,0),'coin':(255,255,100),'pipe_vertical':(0,180,0),
        'pipe_horizontal':(0,160,0),'platform':(100,100,100),'goomba':(255,50,50),
        'koopa_green':(0,200,0),'koopa_red':(200,0,0),'mushroom':(255,100,200),
        'flower':(255,150,0),'star':(255,255,0),'bgo_cloud':(150,150,150),
        'bgo_bush':(0,100,0),'bgo_hill':(80,160,80),'bgo_tree':(0,80,0),
        'grass':(130,100,60),'sand':(200,170,80),'dirt':(120,80,40),
        'stone':(110,110,110),'ice':(130,190,230),'bridge':(130,80,30),
        'mushroom_platform':(170,80,170),'pswitch':(60,60,170),
        'slope_left':(180,180,0),'slope_right':(180,180,0),
        'water':(0,100,255),'lava':(255,80,0),
        'conveyor_left':(100,100,100),'conveyor_right':(100,100,100),
        'semisolid':(150,150,200),
        'cloud':(150,150,150),'bush':(0,100,0),'hill':(80,160,80),
        'tree':(0,80,0),'fence':(160,130,70),'bush_3':(0,100,0),
        'castle':(120,115,130),'waterfall':(50,100,220),'sign':(180,160,100),
        'fence2':(160,130,70),'fence3':(160,130,70),
    },
    'SMW': {
        'background':(110,200,255),'ground':(200,160,100),'brick':(210,120,70),
        'question':(255,220,0),'coin':(255,240,0),'pipe_vertical':(0,220,80),
        'pipe_horizontal':(0,200,70),'platform':(180,130,70),'goomba':(210,120,0),
        'koopa_green':(0,220,80),'koopa_red':(220,60,60),'mushroom':(255,50,200),
        'flower':(255,160,0),'star':(255,240,0),'bgo_cloud':(240,240,240),
        'bgo_bush':(0,200,80),'bgo_hill':(120,220,120),'bgo_tree':(0,160,60),
        'grass':(80,200,80),'sand':(230,210,120),'dirt':(170,120,70),
        'stone':(160,160,160),'ice':(180,230,255),'bridge':(180,120,50),
        'mushroom_platform':(220,120,220),'pswitch':(100,100,220),
        'slope_left':(180,180,0),'slope_right':(180,180,0),
        'water':(0,100,255),'lava':(255,80,0),
        'conveyor_left':(100,100,100),'conveyor_right':(100,100,100),
        'semisolid':(150,150,200),
        'cloud':(240,240,240),'bush':(0,200,80),'hill':(120,220,120),
        'tree':(0,160,60),'fence':(200,170,100),'bush_3':(0,200,80),
        'castle':(150,140,160),'waterfall':(70,140,255),'sign':(220,200,140),
        'fence2':(200,170,100),'fence3':(200,170,100),
    },
}
current_theme = 'SMB1'

# ── GRAPHICS STORAGE ──────────────────────────────────────────────────────────
tile_images = {}
bgo_images  = {}
npc_images  = {}
USE_GRAPHICS = False

# ── SIDEBAR THUMBNAIL CACHE ────────────────────────────────────────────────────
# Maps (item_name, category) → scaled 28×28 pygame.Surface
_sidebar_thumb_cache = {}

_CATEGORY_DIRS = {
    "Tiles": "smbx_assets/tilesets",
    "BGOs":  "smbx_assets/backgrounds",
    "NPCs":  "smbx_assets/npc",
}

def get_sidebar_thumb(item_name, category):
    """Load (or generate on-the-fly) a 28×28 thumbnail for a sidebar item."""
    key = (item_name, category)
    if key in _sidebar_thumb_cache:
        return _sidebar_thumb_cache[key]

    surf = None
    # 1. Try loading from the saved PNG file
    folder = _CATEGORY_DIRS.get(category, "")
    if folder:
        path = os.path.join(folder, item_name + ".png")
        if os.path.exists(path):
            try:
                loaded = pygame.image.load(path).convert_alpha()
                surf = pygame.transform.smoothscale(loaded, (28, 28))
            except Exception:
                surf = None

    # 2. Fall back: call the matching _ag_* generator directly
    if surf is None:
        _AG_MAP = {
            # tiles
            "ground": _ag_ground, "grass": _ag_grass, "sand": _ag_sand,
            "dirt": _ag_dirt, "brick": _ag_brick, "question": _ag_question,
            "pipe_vertical": _ag_pipe_v, "pipe_horizontal": _ag_pipe_h,
            "platform": _ag_platform, "coin": _ag_coin, "bridge": _ag_bridge,
            "stone": _ag_stone, "ice": _ag_ice,
            "mushroom_platform": _ag_mush_plat, "pswitch": _ag_pswitch,
            "slope_left": lambda: _ag_slope(True), "slope_right": lambda: _ag_slope(False),
            "water": _ag_water, "lava": _ag_lava,
            "conveyor_left": lambda: _ag_conveyor('left'),
            "conveyor_right": lambda: _ag_conveyor('right'),
            "semisolid": _ag_semisolid,
            # BGOs
            "cloud": _ag_cloud, "bush": _ag_bush, "hill": _ag_hill,
            "fence": _ag_fence, "bush_3": _ag_bush3, "tree": _ag_tree,
            "castle": _ag_castle, "waterfall": _ag_waterfall,
            "sign": _ag_sign, "fence2": _ag_fence2, "fence3": _ag_fence3,
            # NPCs
            "goomba": _ag_goomba,
            "koopa_green": lambda: _ag_koopa(C['koop_g']),
            "koopa_red":   lambda: _ag_koopa(C['koop_r']),
            "paratroopa_green": lambda: _ag_paratroopa(C['koop_g']),
            "paratroopa_red":   lambda: _ag_paratroopa(C['koop_r']),
            "piranha": _ag_piranha, "piranha_fire": _ag_piranha,
            "hammer_bro": _ag_hammer_bro, "lakitu": _ag_lakitu,
            "mushroom": lambda: _ag_mushroom_npc((220,40,40,255)),
            "flower": _ag_flower_npc, "star": _ag_star_npc,
            "1up": _ag_1up, "buzzy": _ag_buzzy, "spiny": _ag_spiny,
            "cheep": _ag_cheep, "blooper": _ag_blooper, "thwomp": _ag_thwomp,
            "bowser": _ag_bowser, "boo": _ag_boo, "podoboo": _ag_podoboo,
            "sledge_bro": lambda: _ag_generic_npc((40,120,40,255)),
            "rotodisc": _ag_grinder, "grinder": _ag_grinder,
            "burner": lambda: _ag_generic_npc((255,120,30,255)),
            "cannon": _ag_cannon, "bullet_bill": _ag_bullet,
            "bowser_statue": lambda: _ag_generic_npc((80,100,80,255)),
            "fishbone": lambda: _ag_generic_npc((230,225,215,255)),
            "dry_bones": _ag_dry_bones,
            "boo_ring": lambda: _ag_generic_npc((230,230,240,255)),
            "bomber_bill": _ag_bullet,
            "bony_beetle": lambda: _ag_generic_npc((200,195,185,255)),
            "skull_platform": lambda: _ag_generic_npc((220,215,205,255)),
            "start": _ag_start_marker,
        }
        fn = _AG_MAP.get(item_name)
        if fn:
            try:
                raw = fn()
                surf = pygame.transform.smoothscale(raw, (28, 28))
            except Exception:
                surf = None

    _sidebar_thumb_cache[key] = surf
    return surf

# FIX B01: FONT objects are declared here but ONLY assigned after pygame.init()
# They are set as globals in main() before any drawing code runs.
FONT       = None
FONT_SMALL = None
FONT_MENU  = None
FONT_TITLE = None

# ── GRAPHICS LOADER ────────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
# BUILT-IN ASSET GENERATOR  (pygame-native, no Pillow required)
# Draws all 68 pixel-art 32×32 sprites at startup if not already present.
# ══════════════════════════════════════════════════════════════════════════════

SZ = 32  # sprite dimensions

# ── Colour palette ─────────────────────────────────────────────────────────────
C = dict(
    black=(0,0,0,255),   white=(255,255,255,255), trans=(0,0,0,0),
    sky=(92,148,252,255), ground_top=(80,200,80,255), ground_fill=(120,80,40,255),
    brick_main=(185,85,45,255), brick_dark=(140,55,25,255), brick_mortar=(220,160,110,255),
    question=(255,210,0,255), question_dark=(200,150,0,255), q_mark=(80,40,0,255),
    coin=(255,220,30,255), coin_edge=(200,160,0,255),
    pipe_main=(40,180,40,255), pipe_light=(100,230,100,255), pipe_dark=(10,100,10,255),
    platform=(180,130,70,255), platform_dark=(110,80,40,255),
    sand=(220,200,100,255), sand_dark=(170,145,60,255),
    dirt=(150,100,60,255), dirt_dark=(110,70,35,255),
    stone=(155,155,155,255), stone_dark=(100,100,100,255),
    ice=(190,230,255,255), ice_shine=(255,255,255,200),
    bridge=(175,110,45,255), bridge_dark=(120,70,25,255),
    mush_cap=(210,100,210,255), mush_stem=(230,200,170,255),
    ps=(80,80,220,255), ps_dark=(50,50,160,255),
    slope=(185,175,45,255),
    water=(30,100,255,200), water_crest=(150,200,255,220),
    lava=(250,75,0,220), lava_glow=(255,180,30,230),
    conv=(100,100,100,255), conv_arrow=(200,200,200,255),
    semi=(160,155,210,255), semi_dark=(110,105,165,255),
    goomba=(190,100,20,255), goomba_dark=(130,60,10,255), goomba_eye=(240,230,200,255),
    koop_g=(30,200,60,255), koop_r=(220,50,50,255), koop_shell=(100,200,100,255),
    mush_red=(220,30,30,255), mush_stem2=(240,220,180,255), mush_spot=(255,255,255,255),
    flower=(255,240,50,255), flower_petal=(255,60,60,255), flower_stem=(30,160,30,255),
    star=(255,240,20,255), star_eye=(30,30,30,255),
    boo=(240,240,245,255), boo_eye=(30,30,30,255),
    cloud=(240,240,250,255), cloud_shadow=(200,210,240,255),
    bush=(50,180,50,255), bush_dark=(20,120,20,255),
    hill=(100,200,100,255), hill_dark=(60,140,60,255),
    tree_top=(30,150,30,255), tree_trunk=(140,90,40,255),
    fence=(210,180,130,255), fence_dark=(160,130,80,255),
    castle=(160,150,165,255), castle_dark=(100,95,105,255),
)

# ── Pygame drawing helpers ──────────────────────────────────────────────────────
def _pnew():
    """New 32×32 transparent RGBA surface."""
    return pygame.Surface((SZ, SZ), pygame.SRCALPHA)

def _pnew_fill(color):
    s = pygame.Surface((SZ, SZ), pygame.SRCALPHA)
    s.fill(color)
    return s

def _r(s, c, x1, y1, x2, y2, w=0):
    """Filled or outlined rect using PIL-style inclusive [x1,y1,x2,y2]."""
    pygame.draw.rect(s, c, (x1, y1, x2 - x1 + 1, y2 - y1 + 1), w)

def _e(s, c, x1, y1, x2, y2, w=0):
    """Ellipse using PIL-style inclusive bounding box."""
    ww = max(1, x2 - x1 + 1)
    hh = max(1, y2 - y1 + 1)
    pygame.draw.ellipse(s, c, (x1, y1, ww, hh), w)

def _p(s, c, pts, w=0):
    """Polygon."""
    if len(pts) >= 3:
        pygame.draw.polygon(s, c, pts, w)

def _l(s, c, x1, y1, x2, y2, w=1):
    """Line."""
    pygame.draw.line(s, c, (x1, y1), (x2, y2), w)

def _a(s, c, x1, y1, x2, y2, a0, a1, w=1):
    """Arc – PIL degrees CW-from-East → pygame radians CCW-from-East."""
    start = (2 * math.pi - math.radians(a1)) % (2 * math.pi)
    stop  = (2 * math.pi - math.radians(a0)) % (2 * math.pi)
    if stop <= start:
        stop += 2 * math.pi
    ww = max(1, x2 - x1 + 1)
    hh = max(1, y2 - y1 + 1)
    pygame.draw.arc(s, c, (x1, y1, ww, hh), start, stop, w)

def _ol(s, col=None, w=1):
    """Draw a 1-px border outline over the whole surface."""
    pygame.draw.rect(s, col or C['black'], (0, 0, SZ, SZ), w)

def _sv(surf, folder, name):
    pygame.image.save(surf, os.path.join(folder, name))

# ── Tile makers ────────────────────────────────────────────────────────────────
def _ag_ground():
    s = _pnew()
    _r(s,C['ground_fill'],0,0,SZ-1,SZ-1)
    _r(s,C['ground_top'],0,0,SZ-1,5)
    for x in (4,10,18,24): _r(s,(40,160,40,255),x,2,x+1,4)
    _ol(s)
    return s

def _ag_grass():
    s = _pnew()
    _r(s,(80,200,80,255),0,0,SZ-1,SZ-1)
    _r(s,(50,170,50,255),0,0,SZ-1,3)
    for x in range(2,SZ,6): _p(s,(30,140,30,255),[(x,8),(x+2,2),(x+4,8)])
    _ol(s)
    return s

def _ag_sand():
    s = _pnew()
    _r(s,C['sand'],0,0,SZ-1,SZ-1)
    _r(s,C['sand_dark'],0,0,SZ-1,4)
    for x,y in [(5,10),(15,16),(22,9),(8,22),(26,19)]: _e(s,(200,175,80,255),x,y,x+2,y+1)
    _ol(s)
    return s

def _ag_dirt():
    s = _pnew()
    _r(s,C['dirt'],0,0,SZ-1,SZ-1)
    _r(s,C['dirt_dark'],0,0,SZ-1,4)
    for x,y in [(6,8),(18,14),(10,22),(24,10)]: _e(s,(120,80,40,255),x,y,x+3,y+2)
    _ol(s)
    return s

def _ag_brick():
    s = _pnew()
    _r(s,C['brick_main'],0,0,SZ-1,SZ-1)
    _r(s,C['brick_mortar'],0,10,SZ-1,11)
    _r(s,C['brick_mortar'],0,22,SZ-1,23)
    _r(s,C['brick_mortar'],15,0,16,10)
    _r(s,C['brick_mortar'],7,11,8,22)
    _r(s,C['brick_mortar'],23,11,24,22)
    _r(s,C['brick_mortar'],15,23,16,SZ-1)
    _l(s,C['brick_dark'],1,1,SZ-2,1)
    _l(s,C['brick_dark'],1,1,1,9)
    _ol(s)
    return s

def _ag_question():
    s = _pnew()
    _r(s,C['question'],0,0,SZ-1,SZ-1)
    _r(s,C['question_dark'],0,SZ-4,SZ-1,SZ-1)
    _r(s,C['question_dark'],0,0,3,SZ-1)
    _r(s,C['question_dark'],SZ-4,0,SZ-1,SZ-1)
    for x,y,w,h in [(10,6,12,4),(18,10,4,4),(12,16,4,4),(12,22,4,4)]:
        _r(s,C['q_mark'],x,y,x+w-1,y+h-1)
    _ol(s)
    return s

def _ag_pipe_v():
    s = _pnew()
    _r(s,C['pipe_dark'],4,8,SZ-5,SZ-1)
    _r(s,C['pipe_main'],6,8,SZ-7,SZ-1)
    _r(s,C['pipe_light'],8,8,10,SZ-1)
    _r(s,C['pipe_dark'],2,0,SZ-3,10)
    _r(s,C['pipe_main'],4,0,SZ-5,10)
    _r(s,C['pipe_light'],6,2,9,9)
    _ol(s)
    return s

def _ag_pipe_h():
    s = _pnew()
    _r(s,C['pipe_dark'],0,4,SZ-9,SZ-5)
    _r(s,C['pipe_main'],0,6,SZ-9,SZ-7)
    _r(s,C['pipe_light'],0,8,SZ-9,11)
    _r(s,C['pipe_dark'],SZ-11,2,SZ-1,SZ-3)
    _r(s,C['pipe_main'],SZ-11,4,SZ-1,SZ-5)
    _r(s,C['pipe_light'],SZ-9,6,SZ-1,9)
    _ol(s)
    return s

def _ag_platform():
    s = _pnew()
    _r(s,C['platform'],0,0,SZ-1,SZ-1)
    _r(s,(200,155,80,255),0,0,SZ-1,5)
    for x in range(0,SZ,8): _r(s,C['platform_dark'],x,6,x+3,SZ-1)
    _ol(s)
    return s

def _ag_coin():
    s = _pnew()
    _e(s,C['coin'],6,4,SZ-7,SZ-5)
    _e(s,C['coin_edge'],8,6,SZ-9,SZ-7)
    _e(s,C['coin'],10,8,SZ-11,SZ-9)
    _l(s,C['coin_edge'],14,10,14,SZ-11,3)
    _l(s,C['coin_edge'],18,10,18,SZ-11,2)
    return s

def _ag_bridge():
    s = _pnew()
    _r(s,C['bridge'],0,0,SZ-1,SZ-1)
    for x in range(0,SZ,8): _r(s,C['bridge_dark'],x,0,x+1,SZ-1)
    _r(s,C['bridge_dark'],0,8,SZ-1,10)
    _r(s,C['bridge_dark'],0,20,SZ-1,22)
    _ol(s)
    return s

def _ag_stone():
    s = _pnew()
    _r(s,C['stone'],0,0,SZ-1,SZ-1)
    _r(s,C['stone_dark'],0,0,SZ-1,1)
    _r(s,C['stone_dark'],0,0,1,SZ-1)
    _r(s,(200,200,200,255),0,SZ-2,SZ-1,SZ-1)
    _r(s,(200,200,200,255),SZ-2,0,SZ-1,SZ-1)
    for x,y,w,h in [(4,4,10,8),(18,8,8,6),(6,18,12,8),(20,20,8,8)]:
        _r(s,(135,135,135,255),x,y,x+w,y+h)
        _l(s,(180,180,180,255),x,y,x+w,y)
    _ol(s)
    return s

def _ag_ice():
    s = _pnew()
    _r(s,C['ice'],0,0,SZ-1,SZ-1)
    _r(s,C['ice_shine'],0,0,SZ-1,3)
    for px,py in [(4,4),(20,12),(10,22),(24,6)]:
        _l(s,(255,255,255,180),px-2,py,px+2,py)
        _l(s,(255,255,255,180),px,py-2,px,py+2)
    _ol(s,(100,150,200,255))
    return s

def _ag_mush_plat():
    s = _pnew()
    _e(s,C['mush_cap'],0,0,SZ-1,SZ-1)
    _e(s,(230,120,230,255),2,2,SZ-3,SZ-3)
    _e(s,(255,255,255,200),4,4,8,8)
    _e(s,(255,255,255,200),22,6,26,10)
    _r(s,C['mush_stem'],0,SZ//2,SZ-1,SZ-1)
    _ol(s)
    return s

def _ag_pswitch():
    s = _pnew()
    _r(s,C['ps'],0,0,SZ-1,SZ-1)
    _r(s,C['ps_dark'],0,SZ-4,SZ-1,SZ-1)
    _r(s,C['ps_dark'],0,0,3,SZ-1)
    _r(s,C['ps_dark'],SZ-4,0,SZ-1,SZ-1)
    _e(s,(220,220,255,255),8,6,SZ-9,SZ-7)
    # P pixel-art (no font needed)
    _r(s,(40,40,120,255),10,9,12,17)
    _r(s,(40,40,120,255),12,9,16,11)
    _r(s,(40,40,120,255),14,11,16,14)
    _r(s,(40,40,120,255),12,13,14,15)
    # ! mark
    _r(s,(40,40,120,255),19,9,21,16)
    _r(s,(40,40,120,255),19,18,21,20)
    _ol(s)
    return s

def _ag_slope(left=True):
    s = _pnew()
    pts = [(0,0),(SZ-1,0),(0,SZ-1)] if left else [(0,0),(SZ-1,0),(SZ-1,SZ-1)]
    _p(s,C['slope'],pts)
    _p(s,(120,110,20,255),pts,1)
    return s

def _ag_water():
    s = _pnew_fill((30,100,255,170))
    for x in range(0,SZ,8): _a(s,C['water_crest'],x-4,0,x+4,6,0,180,2)
    for x in range(0,SZ,8): _a(s,(100,180,255,140),x-4,12,x+4,18,0,180,1)
    return s

def _ag_lava():
    s = _pnew_fill(C['lava'])
    for x in range(0,SZ,10): _p(s,C['lava_glow'],[(x,8),(x+5,0),(x+10,8)])
    for x in range(0,SZ,10): _p(s,(255,120,20,180),[(x,20),(x+5,14),(x+10,20)])
    return s

def _ag_conveyor(direction='left'):
    s = _pnew()
    _r(s,C['conv'],0,0,SZ-1,SZ-1)
    _r(s,(130,130,130,255),0,0,SZ-1,4)
    _r(s,(130,130,130,255),0,SZ-5,SZ-1,SZ-1)
    # Arrow triangles instead of text
    for x in range(4,SZ,10):
        if direction == 'left':
            _p(s,C['conv_arrow'],[(x+6,10),(x,14),(x+6,18)])
        else:
            _p(s,C['conv_arrow'],[(x,10),(x+6,14),(x,18)])
    _ol(s)
    return s

def _ag_semisolid():
    s = _pnew()
    _r(s,C['semi'],0,0,SZ-1,12)
    _r(s,(200,195,240,255),0,0,SZ-1,4)
    _r(s,C['semi_dark'],0,0,SZ-1,12,1)
    return s

# ── BGO makers ────────────────────────────────────────────────────────────────
def _ag_cloud():
    s = _pnew()
    _e(s,C['cloud_shadow'],4,12,24,28)
    _e(s,C['cloud'],2,14,22,SZ-2)
    _e(s,C['cloud_shadow'],10,8,SZ-4,24)
    _e(s,C['cloud'],8,10,SZ-6,22)
    _e(s,C['cloud'],0,18,16,SZ-1)
    return s

def _ag_bush():
    s = _pnew()
    _e(s,C['bush_dark'],2,10,14,22)
    _e(s,C['bush'],10,6,26,22)
    _e(s,C['bush_dark'],18,10,SZ-2,22)
    _e(s,C['bush'],6,14,22,SZ-4)
    _r(s,(100,70,30,255),10,SZ-8,22,SZ-1)
    return s

def _ag_hill():
    s = _pnew()
    _e(s,C['hill'],-2,6,SZ+2,SZ+4)
    _e(s,C['hill'],0,8,SZ-1,SZ+2)
    for x,y in [(8,14),(16,12),(12,20)]: _e(s,C['hill_dark'],x,y,x+3,y+3)
    return s

def _ag_fence():
    s = _pnew()
    _r(s,C['fence'],0,8,SZ-1,11)
    _r(s,C['fence'],0,20,SZ-1,23)
    for x in range(4,SZ,10):
        _r(s,C['fence'],x,2,x+4,SZ-1)
        _p(s,C['fence'],[(x,2),(x+2,0),(x+4,2)])
    _ol(s,C['fence_dark'])
    return s

def _ag_bush3():
    s = _pnew()
    for cx in (6,16,26): _e(s,C['bush'],cx-6,8,cx+6,24)
    _e(s,C['bush'],0,12,SZ-1,SZ-4)
    return s

def _ag_tree():
    s = _pnew()
    _r(s,C['tree_trunk'],12,20,20,SZ-1)
    _e(s,(15,110,15,255),2,0,SZ-3,24)
    _e(s,C['tree_top'],4,2,SZ-5,22)
    _e(s,(60,180,60,255),6,4,SZ-7,18)
    return s

def _ag_castle():
    s = _pnew()
    _r(s,C['castle'],0,8,SZ-1,SZ-1)
    for x in (0,8,16,24): _r(s,C['castle'],x,0,x+6,8)
    _r(s,C['castle_dark'],12,18,20,SZ-1)
    _r(s,(60,50,70,255),6,14,10,24)
    _r(s,(60,50,70,255),22,14,26,24)
    _ol(s,C['castle_dark'])
    return s

def _ag_waterfall():
    s = _pnew()
    for x in range(0,SZ,8):
        for y in range(0,SZ,4):
            alpha = 180 if (x+y)%8==0 else 120
            _r(s,(60,140,255,alpha),x,y,x+6,y+2)
    return s

def _ag_sign():
    s = _pnew()
    _r(s,(140,90,40,255),12,SZ-12,16,SZ-1)
    _r(s,(220,200,140,255),4,2,SZ-5,22)
    _r(s,(140,110,60,255),4,2,SZ-5,22,1)
    _l(s,(80,60,30,255),8,8,SZ-9,8,2)
    _l(s,(80,60,30,255),8,13,SZ-9,13,2)
    _l(s,(80,60,30,255),8,18,SZ-13,18,2)
    return s

def _ag_fence2():
    s = _pnew()
    _r(s,C['fence'],0,4,SZ-1,8)
    _r(s,C['fence'],0,18,SZ-1,22)
    for x in range(2,SZ,6): _r(s,C['fence'],x,0,x+3,SZ-1)
    _ol(s,C['fence_dark'])
    return s

def _ag_fence3():
    s = _pnew()
    _r(s,C['fence'],0,12,SZ-1,16)
    for x in range(2,SZ,8):
        _r(s,C['fence'],x,0,x+4,SZ-1)
        _p(s,(230,200,140,255),[(x,0),(x+2,-3),(x+4,0)])
    _ol(s,C['fence_dark'])
    return s

# ── NPC makers ─────────────────────────────────────────────────────────────────
def _ag_goomba():
    s = _pnew()
    _e(s,C['goomba'],2,8,SZ-3,SZ-5)
    _e(s,(210,115,35,255),4,10,SZ-5,SZ-7)
    _e(s,C['goomba_eye'],4,6,12,14)
    _e(s,C['goomba_eye'],20,6,28,14)
    _e(s,(30,30,30,255),5,7,10,12)
    _e(s,(30,30,30,255),21,7,26,12)
    _r(s,C['goomba_dark'],4,SZ-7,10,SZ-1)
    _r(s,C['goomba_dark'],22,SZ-7,28,SZ-1)
    _a(s,(30,30,30,255),8,SZ-10,24,SZ-4,0,180,2)
    return s

def _ag_koopa(color):
    s = _pnew()
    _e(s,(240,220,150,255),8,0,22,14)
    _e(s,color,4,8,28,SZ-1)
    lighter = (min(255,color[0]+40), min(255,color[1]+40), min(255,color[2]+40), 255)
    _e(s,lighter,6,10,26,SZ-3)
    _l(s,(30,30,30,255),6,14,8,10,2)
    _l(s,(30,30,30,255),24,14,26,10,2)
    _e(s,(30,30,30,255),11,3,15,8)
    _r(s,(240,220,150,255),4,SZ-4,10,SZ-1)
    _r(s,(240,220,150,255),22,SZ-4,28,SZ-1)
    return s

def _ag_paratroopa(color):
    s = _ag_koopa(color)
    _p(s,(255,255,240,200),[(-2,4),(8,10),(4,16)])
    _p(s,(255,255,240,200),[(SZ+2,4),(SZ-8,10),(SZ-4,16)])
    return s

def _ag_piranha():
    s = _pnew()
    _r(s,C['pipe_dark'],12,20,20,SZ-1)
    _e(s,(220,40,40,255),4,4,SZ-5,24)
    _p(s,(255,220,200,255),[(4,8),(4,18),(0,13)])
    _p(s,(255,220,200,255),[(SZ-5,8),(SZ-5,18),(SZ-1,13)])
    _e(s,(255,255,255,255),10,8,14,12)
    _e(s,(255,255,255,255),18,8,22,12)
    _e(s,(30,30,30,255),11,9,13,11)
    _e(s,(30,30,30,255),19,9,21,11)
    return s

def _ag_hammer_bro():
    s = _pnew()
    _e(s,(240,220,150,255),8,0,22,14)
    _r(s,(40,180,40,255),4,12,28,SZ-1)
    _r(s,(60,200,60,255),6,14,26,SZ-3)
    _e(s,(30,30,30,255),10,3,15,8)
    _p(s,(80,60,30,255),[(22,0),(SZ,0),(SZ,4),(22,8)])
    return s

def _ag_lakitu():
    s = _pnew()
    _e(s,C['cloud'],2,14,26,SZ-3)
    _e(s,(240,220,150,255),8,2,24,18)
    _e(s,(30,30,30,255),10,5,14,9)
    _e(s,(30,30,30,255),18,5,22,9)
    _a(s,(30,30,30,255),12,12,20,16,0,180,2)
    return s

def _ag_mushroom_npc(color=(220,40,40,255)):
    s = _pnew()
    _r(s,C['mush_stem2'],8,14,24,SZ-1)
    _e(s,color,2,4,SZ-3,22)
    lighter = (min(255,color[0]+30),min(255,color[1]+30),min(255,color[2]+30),255)
    _e(s,lighter,4,6,SZ-5,20)
    _e(s,C['mush_spot'],8,8,13,13)
    _e(s,C['mush_spot'],19,8,24,13)
    _e(s,C['mush_spot'],12,14,17,19)
    _e(s,(30,30,30,255),12,22,16,26)
    _e(s,(30,30,30,255),16,22,20,26)
    return s

def _ag_flower_npc():
    s = _pnew()
    _r(s,C['flower_stem'],14,12,18,SZ-1)
    for dx,dy in [(-6,-6),(6,-6),(-8,0),(8,0),(-6,6),(6,6)]:
        _e(s,C['flower_petal'],14+dx-4,12+dy-4,14+dx+4,12+dy+4)
    _e(s,C['flower'],10,6,22,18)
    _e(s,(255,255,100,255),12,8,20,16)
    return s

def _ag_star_npc():
    s = _pnew()
    pts = []
    for i in range(5):
        angle = math.pi * 2 * i / 5 - math.pi / 2
        pts.append((16 + 12*math.cos(angle), 16 + 12*math.sin(angle)))
        inner_a = math.pi * 2 * (i + 0.5) / 5 - math.pi / 2
        pts.append((16 + 5*math.cos(inner_a), 16 + 5*math.sin(inner_a)))
    _p(s,C['star'],pts)
    _p(s,(200,160,0,255),pts,1)
    _e(s,C['star_eye'],12,10,16,14)
    _e(s,C['star_eye'],16,10,20,14)
    return s

def _ag_1up():
    return _ag_mushroom_npc(color=(40,200,40,255))

def _ag_buzzy():
    s = _pnew()
    _e(s,(80,80,90,255),2,2,SZ-3,SZ-3)
    _e(s,(110,110,120,255),4,4,SZ-5,SZ-5)
    _r(s,(110,110,80,255),4,SZ-8,10,SZ-1)
    _r(s,(110,110,80,255),22,SZ-8,28,SZ-1)
    _e(s,(255,255,255,255),9,8,14,13)
    _e(s,(255,255,255,255),18,8,23,13)
    _ol(s)
    return s

def _ag_spiny():
    s = _pnew()
    _e(s,(200,40,40,255),4,8,SZ-5,SZ-3)
    _e(s,(220,60,60,255),6,10,SZ-7,SZ-5)
    for x in range(4,SZ,6): _p(s,(200,40,40,255),[(x,8),(x+3,2),(x+6,8)])
    _e(s,(255,255,255,255),8,12,13,17)
    _e(s,(255,255,255,255),19,12,24,17)
    return s

def _ag_cheep():
    s = _pnew()
    _e(s,(255,80,80,255),4,8,SZ-1,SZ-8)
    _p(s,(255,80,80,255),[(4,14),(0,8),(0,SZ-8),(4,18)])
    _e(s,(255,255,255,255),18,10,24,16)
    _e(s,(30,30,30,255),20,11,23,15)
    _p(s,(255,60,60,255),[(SZ-5,12),(SZ-1,16),(SZ-5,20)])
    return s

def _ag_blooper():
    s = _pnew()
    _e(s,(230,230,240,255),4,0,SZ-5,22)
    for x in range(4,SZ-3,6): _r(s,(210,210,225,255),x,20,x+3,SZ-1)
    _e(s,(30,30,30,255),8,6,13,11)
    _e(s,(30,30,30,255),18,6,23,11)
    return s

def _ag_thwomp():
    s = _pnew()
    _r(s,(80,80,100,255),0,0,SZ-1,SZ-1)
    _r(s,(100,100,120,255),2,2,SZ-3,SZ-3)
    _r(s,(30,30,30,255),4,4,12,16)
    _r(s,(30,30,30,255),20,4,28,16)
    _r(s,(200,30,30,255),4,20,SZ-5,SZ-5)
    for x in range(0,SZ,4): _r(s,(80,80,100,255),x,SZ-5,x+2,SZ-1)
    _ol(s)
    return s

def _ag_bowser():
    s = _pnew()
    _e(s,(50,160,50,255),2,2,SZ-3,SZ-3)
    _e(s,(70,190,70,255),4,4,SZ-5,SZ-5)
    _e(s,(255,240,150,255),8,4,16,12)
    _e(s,(30,30,30,255),18,4,26,12)
    _p(s,(255,200,40,255),[(6,0),(8,6),(4,6)])
    _p(s,(255,200,40,255),[(14,0),(16,6),(12,6)])
    _p(s,(255,200,40,255),[(22,0),(24,6),(20,6)])
    _r(s,(255,150,50,255),10,18,22,SZ-1)
    return s

def _ag_boo():
    s = _pnew()
    _e(s,C['boo'],4,4,SZ-5,SZ-5)
    _e(s,(248,248,252,255),6,6,SZ-7,SZ-7)
    _e(s,C['boo_eye'],10,8,15,14)
    _e(s,C['boo_eye'],18,8,23,14)
    _a(s,C['boo_eye'],10,18,22,24,0,180,2)
    pts = [(4,SZ-5),(8,SZ-2),(12,SZ-4),(16,SZ-2),(20,SZ-4),(24,SZ-2),(SZ-5,SZ-5)]
    _p(s,C['boo'],pts)
    return s

def _ag_podoboo():
    s = _pnew()
    _e(s,(255,80,0,220),4,4,SZ-5,SZ-5)
    _e(s,(255,160,30,200),6,6,SZ-7,SZ-7)
    _e(s,(255,220,80,180),10,10,SZ-11,SZ-11)
    for i in range(4):
        a = math.pi * 2 * i / 4
        x = int(16 + 10*math.cos(a)); y = int(16 + 10*math.sin(a))
        _p(s,(255,60,0,200),[(x-3,y-3),(x,y-7),(x+3,y-3)])
    return s

def _ag_dry_bones():
    s = _pnew()
    _e(s,(240,235,220,255),6,2,26,18)
    _e(s,(30,30,30,255),8,6,14,12)
    _e(s,(30,30,30,255),18,6,24,12)
    _r(s,(235,225,210,255),4,18,28,SZ-3)
    for x in range(6,26,4): _l(s,(200,190,175,255),x,18,x,SZ-3)
    _r(s,(235,225,210,255),4,SZ-6,10,SZ-1)
    _r(s,(235,225,210,255),22,SZ-6,28,SZ-1)
    return s

def _ag_cannon():
    s = _pnew()
    _e(s,(60,60,60,255),2,6,SZ-3,SZ-3)
    _e(s,(80,80,80,255),4,8,SZ-5,SZ-5)
    _r(s,(60,60,60,255),10,0,22,12)
    _r(s,(30,30,30,255),12,2,20,10)
    _ol(s,(40,40,40,255))
    return s

def _ag_bullet():
    s = _pnew()
    _r(s,(40,40,40,255),4,8,SZ-1,SZ-8)
    _e(s,(50,50,50,255),0,6,14,SZ-6)
    _e(s,(80,80,80,255),2,8,10,SZ-8)
    _e(s,(255,255,255,200),8,12,14,20)
    return s

def _ag_grinder():
    s = _pnew()
    _e(s,(150,150,150,255),2,2,SZ-3,SZ-3)
    _e(s,(180,180,180,255),4,4,SZ-5,SZ-5)
    for i in range(8):
        a = math.pi * 2 * i / 8
        x = int(16 + 14*math.cos(a)); y = int(16 + 14*math.sin(a))
        _p(s,(130,130,130,255),[(x-2,y-2),(x+2,y-2),(x,y+4)])
    _e(s,(120,120,120,255),10,10,22,22)
    return s

def _ag_start_marker():
    s = _pnew()
    _r(s,(0,200,0,200),0,0,SZ-1,SZ-1)
    _p(s,(255,255,255,230),[(8,4),(8,SZ-4),(SZ-4,SZ//2)])
    _r(s,(0,150,0,255),0,0,SZ-1,SZ-1,2)
    return s

def _ag_generic_npc(color):
    s = _pnew()
    _e(s,color,4,4,SZ-5,SZ-5)
    _e(s,(255,255,255,200),8,8,13,13)
    _e(s,(30,30,30,255),9,9,12,12)
    _ol(s)
    return s

# ── Master render dispatch ──────────────────────────────────────────────────────
def generate_assets_pygame(base_dir="smbx_assets"):
    """Generate all 68 pixel-art sprites using pygame. Called once at startup."""
    tile_dir = os.path.join(base_dir, "tilesets")
    bgo_dir  = os.path.join(base_dir, "backgrounds")
    npc_dir  = os.path.join(base_dir, "npc")
    for d in (tile_dir, bgo_dir, npc_dir):
        os.makedirs(d, exist_ok=True)

    tiles = {
        "ground.png":            _ag_ground,
        "grass.png":             _ag_grass,
        "sand.png":              _ag_sand,
        "dirt.png":              _ag_dirt,
        "brick.png":             _ag_brick,
        "question.png":          _ag_question,
        "pipe_vertical.png":     _ag_pipe_v,
        "pipe_horizontal.png":   _ag_pipe_h,
        "platform.png":          _ag_platform,
        "coin.png":              _ag_coin,
        "bridge.png":            _ag_bridge,
        "stone.png":             _ag_stone,
        "ice.png":               _ag_ice,
        "mushroom_platform.png": _ag_mush_plat,
        "pswitch.png":           _ag_pswitch,
        "slope_left.png":        lambda: _ag_slope(left=True),
        "slope_right.png":       lambda: _ag_slope(left=False),
        "water.png":             _ag_water,
        "lava.png":              _ag_lava,
        "conveyor_left.png":     lambda: _ag_conveyor('left'),
        "conveyor_right.png":    lambda: _ag_conveyor('right'),
        "semisolid.png":         _ag_semisolid,
    }
    bgos = {
        "cloud.png":     _ag_cloud,
        "bush.png":      _ag_bush,
        "hill.png":      _ag_hill,
        "fence.png":     _ag_fence,
        "bush_3.png":    _ag_bush3,
        "tree.png":      _ag_tree,
        "castle.png":    _ag_castle,
        "waterfall.png": _ag_waterfall,
        "sign.png":      _ag_sign,
        "fence2.png":    _ag_fence2,
        "fence3.png":    _ag_fence3,
    }
    npcs = {
        "goomba.png":           _ag_goomba,
        "koopa_green.png":      lambda: _ag_koopa(C['koop_g']),
        "koopa_red.png":        lambda: _ag_koopa(C['koop_r']),
        "paratroopa_green.png": lambda: _ag_paratroopa(C['koop_g']),
        "paratroopa_red.png":   lambda: _ag_paratroopa(C['koop_r']),
        "piranha.png":          _ag_piranha,
        "hammer_bro.png":       _ag_hammer_bro,
        "lakitu.png":           _ag_lakitu,
        "mushroom.png":         lambda: _ag_mushroom_npc((220,40,40,255)),
        "flower.png":           _ag_flower_npc,
        "star.png":             _ag_star_npc,
        "1up.png":              _ag_1up,
        "buzzy.png":            _ag_buzzy,
        "spiny.png":            _ag_spiny,
        "cheep.png":            _ag_cheep,
        "blooper.png":          _ag_blooper,
        "thwomp.png":           _ag_thwomp,
        "bowser.png":           _ag_bowser,
        "boo.png":              _ag_boo,
        "podoboo.png":          _ag_podoboo,
        "piranha_fire.png":     _ag_piranha,
        "sledge_bro.png":       lambda: _ag_generic_npc((40,120,40,255)),
        "rotodisc.png":         _ag_grinder,
        "burner.png":           lambda: _ag_generic_npc((255,120,30,255)),
        "cannon.png":           _ag_cannon,
        "bullet_bill.png":      _ag_bullet,
        "bowser_statue.png":    lambda: _ag_generic_npc((80,100,80,255)),
        "grinder.png":          _ag_grinder,
        "fishbone.png":         lambda: _ag_generic_npc((230,225,215,255)),
        "dry_bones.png":        _ag_dry_bones,
        "boo_ring.png":         lambda: _ag_generic_npc((230,230,240,255)),
        "bomber_bill.png":      _ag_bullet,
        "bony_beetle.png":      lambda: _ag_generic_npc((200,195,185,255)),
        "skull_platform.png":   lambda: _ag_generic_npc((220,215,205,255)),
        "start.png":            _ag_start_marker,
    }

    count = 0
    for fn, mk in tiles.items():
        path = os.path.join(tile_dir, fn)
        if not os.path.exists(path):
            _sv(mk(), tile_dir, fn)
        count += 1
    for fn, mk in bgos.items():
        path = os.path.join(bgo_dir, fn)
        if not os.path.exists(path):
            _sv(mk(), bgo_dir, fn)
        count += 1
    for fn, mk in npcs.items():
        path = os.path.join(npc_dir, fn)
        if not os.path.exists(path):
            _sv(mk(), npc_dir, fn)
        count += 1
    print(f"[Assets] {count} sprites ready in {base_dir}/")

def generate_default_tileset_ini():
    ini_path = os.path.join(TILESET_DIR, "tileset.ini")
    if os.path.exists(ini_path):
        return
    content = """; SMBX tileset configuration
[general]
name=Default Tileset
[blocks]
1=ground.png
2=grass.png
3=sand.png
4=dirt.png
45=brick.png
34=question.png
112=pipe_vertical.png
113=pipe_horizontal.png
159=platform.png
10=coin.png
47=bridge.png
48=stone.png
55=ice.png
91=mushroom_platform.png
60=pswitch.png
182=slope_left.png
183=slope_right.png
196=water.png
197=lava.png
188=conveyor_left.png
189=conveyor_right.png
190=semisolid.png
[backgrounds]
5=cloud.png
6=bush.png
7=hill.png
8=fence.png
9=bush_3.png
10=tree.png
11=castle.png
12=waterfall.png
13=sign.png
14=fence2.png
15=fence3.png
[npcs]
1=goomba.png
2=koopa_green.png
3=koopa_red.png
4=paratroopa_green.png
5=paratroopa_red.png
6=piranha.png
7=hammer_bro.png
8=lakitu.png
9=mushroom.png
10=flower.png
11=star.png
12=1up.png
13=buzzy.png
14=spiny.png
15=cheep.png
16=blooper.png
17=thwomp.png
18=bowser.png
19=boo.png
20=podoboo.png
21=piranha_fire.png
22=sledge_bro.png
23=rotodisc.png
24=burner.png
25=cannon.png
26=bullet_bill.png
27=bowser_statue.png
28=grinder.png
29=fishbone.png
30=dry_bones.png
31=boo_ring.png
32=bomber_bill.png
33=bony_beetle.png
34=skull_platform.png
196=start.png
"""
    with open(ini_path, 'w') as f:
        f.write(content)


# FIX B02: load_smbx_graphics() must be called AFTER pygame.init() because
# pygame.image.load() requires the display to be initialised.  This function
# is now called explicitly from main() after pygame.init().
def load_smbx_graphics():
    global USE_GRAPHICS, tile_images, bgo_images, npc_images
    generate_default_tileset_ini()
    ini_path = os.path.join(TILESET_DIR, "tileset.ini")
    if not os.path.exists(ini_path):
        return

    config = configparser.ConfigParser()
    config.read(ini_path, encoding='utf-8')

    def load_image(folder, filename, size=GRID_SIZE):
        if not filename:
            return None
        path = os.path.join(folder, filename)
        if os.path.exists(path):
            try:
                img = pygame.image.load(path).convert_alpha()
                return pygame.transform.scale(img, (size, size))
            except Exception as e:
                print(f"  image load error {path}: {e}")
        return None

    if 'blocks' in config:
        for key, val in config['blocks'].items():
            try:
                img = load_image(TILESET_DIR, val)
                if img:
                    tile_images[int(key)] = img
            except ValueError:
                pass
    if 'backgrounds' in config:
        for key, val in config['backgrounds'].items():
            try:
                img = load_image(BACKGROUND_DIR, val)
                if img:
                    bgo_images[int(key)] = img
            except ValueError:
                pass
    if 'npcs' in config:
        for key, val in config['npcs'].items():
            try:
                img = load_image(NPC_GFX_DIR, val)
                if img:
                    npc_images[int(key)] = img
            except ValueError:
                pass

    USE_GRAPHICS = bool(tile_images or bgo_images or npc_images)
    print(f"Graphics loaded: {len(tile_images)} tiles, {len(bgo_images)} BGOs, {len(npc_images)} NPCs")

# ── HELPERS ────────────────────────────────────────────────────────────────────
def draw_edge(surf, rect, raised=True):
    r = pygame.Rect(rect)
    tl = SYS_BTN_LIGHT  if raised else SYS_BTN_DK_SHD
    br = SYS_BTN_DK_SHD if raised else SYS_BTN_LIGHT
    ti = SYS_BTN_FACE   if raised else SYS_BTN_DARK
    bi = SYS_BTN_DARK   if raised else SYS_BTN_FACE
    pygame.draw.line(surf,tl, r.topleft,    r.topright)
    pygame.draw.line(surf,tl, r.topleft,    r.bottomleft)
    pygame.draw.line(surf,br, r.bottomleft, r.bottomright)
    pygame.draw.line(surf,br, r.topright,   r.bottomright)
    pygame.draw.line(surf,ti, (r.left+1,r.top+1),    (r.right-1,r.top+1))
    pygame.draw.line(surf,ti, (r.left+1,r.top+1),    (r.left+1,r.bottom-1))
    pygame.draw.line(surf,bi, (r.left+1,r.bottom-1), (r.right-1,r.bottom-1))
    pygame.draw.line(surf,bi, (r.right-1,r.top+1),   (r.right-1,r.bottom-1))

def draw_text(surf, text, pos, color=None, font=None, center=False):
    if color is None:
        color = SYS_TEXT
    if font is None:
        font = FONT_SMALL
    t = font.render(text, True, color)
    r = t.get_rect(center=pos) if center else t.get_rect(topleft=pos)
    surf.blit(t, r)

def get_theme_color(name):
    """FIX B15: look up colour by exact name; handles both 'bgo_cloud' and 'cloud'."""
    tc = themes[current_theme]
    if name in tc:
        return tc[name]
    # Try without bgo_ prefix
    stripped = name.replace('bgo_', '')
    if stripped in tc:
        return tc[stripped]
    return (128, 128, 128)

# ── ICON DRAWING ───────────────────────────────────────────────────────────────
ICON_FNS = {}

def _make_icon(name, fn):
    ICON_FNS[name] = fn

def draw_icon_select(surf, rect, color=None):
    color = color or SYS_TEXT
    r = rect.inflate(-6,-6)
    for i in range(0,r.width,4):
        if (i//4)%2==0:
            pygame.draw.line(surf,color,(r.x+i,r.y),(min(r.x+i+3,r.right),r.y))
            pygame.draw.line(surf,color,(r.x+i,r.bottom),(min(r.x+i+3,r.right),r.bottom))
    for i in range(0,r.height,4):
        if (i//4)%2==0:
            pygame.draw.line(surf,color,(r.x,r.y+i),(r.x,min(r.y+i+3,r.bottom)))
            pygame.draw.line(surf,color,(r.right,r.y+i),(r.right,min(r.y+i+3,r.bottom)))
ICON_FNS['select']=draw_icon_select

def draw_icon_pencil(surf,rect,color=None):
    color=color or SYS_TEXT; cx,cy=rect.center
    pts=[(cx-1,cy+6),(cx+5,cy-3),(cx+3,cy-5),(cx-3,cy+4)]
    pygame.draw.polygon(surf,color,pts,1)
    pygame.draw.line(surf,color,(cx-1,cy+6),(cx-4,cy+8))
    pygame.draw.line(surf,color,(cx-4,cy+8),(cx-2,cy+5))
ICON_FNS['pencil']=draw_icon_pencil

def draw_icon_eraser(surf,rect,color=None):
    color=color or SYS_TEXT; r=rect.inflate(-8,-8)
    pygame.draw.rect(surf,color,(r.x,r.centery-3,r.width,7),1)
    pygame.draw.line(surf,color,(r.x+r.width//2,r.centery-3),(r.x+r.width//2,r.centery+4))
ICON_FNS['eraser']=draw_icon_eraser

def draw_icon_fill(surf,rect,color=None):
    color=color or SYS_TEXT; cx,cy=rect.center
    pygame.draw.rect(surf,color,(cx-5,cy-4,8,8),1)
    pygame.draw.rect(surf,color,(cx-4,cy-3,6,6))
    pygame.draw.circle(surf,color,(cx+5,cy+4),2)
ICON_FNS['fill']=draw_icon_fill

def draw_icon_new(surf,rect,color=None):
    color=color or SYS_TEXT; r=rect.inflate(-8,-6); fold=5
    pts=[(r.x,r.y),(r.right-fold,r.y),(r.right,r.y+fold),(r.right,r.bottom),(r.x,r.bottom)]
    pygame.draw.polygon(surf,color,pts,1)
    pygame.draw.line(surf,color,(r.right-fold,r.y),(r.right-fold,r.y+fold))
    pygame.draw.line(surf,color,(r.right-fold,r.y+fold),(r.right,r.y+fold))
ICON_FNS['new']=draw_icon_new

def draw_icon_open(surf,rect,color=None):
    color=color or SYS_TEXT; cx,cy=rect.center
    pygame.draw.rect(surf,color,(cx-7,cy-2,14,9),1)
    pygame.draw.rect(surf,color,(cx-7,cy-5,6,4),1)
ICON_FNS['open']=draw_icon_open

def draw_icon_save(surf,rect,color=None):
    color=color or SYS_TEXT; r=rect.inflate(-8,-6)
    pygame.draw.rect(surf,color,r,1)
    pygame.draw.rect(surf,SYS_BTN_FACE,(r.x+2,r.y+2,r.width-4,r.height//2-2))
    pygame.draw.rect(surf,color,(r.x+5,r.y+2,r.width-10,r.height//2-2),1)
    pygame.draw.rect(surf,color,(r.x+r.width//3,r.bottom-5,r.width//3,5))
ICON_FNS['save']=draw_icon_save

def draw_icon_undo(surf,rect,color=None):
    color=color or SYS_TEXT; cx,cy=rect.center
    pygame.draw.arc(surf,color,(cx-6,cy-4,12,10),math.pi*0.3,math.pi*1.1,2)
    pygame.draw.polygon(surf,color,[(cx-6,cy-4),(cx-9,cy),(cx-3,cy-1)])
ICON_FNS['undo']=draw_icon_undo

def draw_icon_redo(surf,rect,color=None):
    color=color or SYS_TEXT; cx,cy=rect.center
    pygame.draw.arc(surf,color,(cx-6,cy-4,12,10),math.pi*1.9,math.pi*0.7+math.pi*2,2)
    pygame.draw.polygon(surf,color,[(cx+6,cy-4),(cx+9,cy),(cx+3,cy-1)])
ICON_FNS['redo']=draw_icon_redo

def draw_icon_play(surf,rect,color=None):
    color=color or SYS_TEXT; cx,cy=rect.center
    pygame.draw.polygon(surf,color,[(cx-4,cy-6),(cx-4,cy+6),(cx+6,cy)])
ICON_FNS['play']=draw_icon_play

def draw_icon_props(surf,rect,color=None):
    color=color or SYS_TEXT; cx,cy=rect.center
    draw_text(surf,"i",(cx,cy),color,FONT_SMALL,True)
    pygame.draw.circle(surf,color,(cx,cy-5),2)
ICON_FNS['props']=draw_icon_props

def draw_icon_grid(surf,rect,color=None):
    color=color or SYS_TEXT; r=rect.inflate(-6,-6)
    for i in range(0,r.width+1,r.width//2):
        pygame.draw.line(surf,color,(r.x+i,r.y),(r.x+i,r.bottom))
    for i in range(0,r.height+1,r.height//2):
        pygame.draw.line(surf,color,(r.x,r.y+i),(r.right,r.y+i))
ICON_FNS['grid']=draw_icon_grid

def draw_icon_zoom_in(surf,rect,color=None):
    color=color or SYS_TEXT; cx,cy=rect.center
    pygame.draw.circle(surf,color,(cx-2,cy-2),5,1)
    pygame.draw.line(surf,color,(cx+2,cy+2),(cx+6,cy+6),2)
    pygame.draw.line(surf,color,(cx-4,cy-2),(cx,cy-2),1)
    pygame.draw.line(surf,color,(cx-2,cy-4),(cx-2,cy),1)
ICON_FNS['zoom_in']=draw_icon_zoom_in

def draw_icon_zoom_out(surf,rect,color=None):
    color=color or SYS_TEXT; cx,cy=rect.center
    pygame.draw.circle(surf,color,(cx-2,cy-2),5,1)
    pygame.draw.line(surf,color,(cx+2,cy+2),(cx+6,cy+6),2)
    pygame.draw.line(surf,color,(cx-4,cy-2),(cx,cy-2),1)
ICON_FNS['zoom_out']=draw_icon_zoom_out

def draw_icon_layer(surf,rect,color=None):
    color=color or SYS_TEXT; r=rect.inflate(-6,-6)
    for i in range(3):
        pygame.draw.rect(surf,color,(r.x,r.y+i*4,r.width,4),1)
ICON_FNS['layer']=draw_icon_layer

def draw_icon_event(surf,rect,color=None):
    color=color or SYS_TEXT; cx,cy=rect.center
    pygame.draw.circle(surf,color,(cx-4,cy-4),2)
    pygame.draw.circle(surf,color,(cx+4,cy-4),2)
    pygame.draw.arc(surf,color,(cx-6,cy,12,8),0,math.pi,2)
ICON_FNS['event']=draw_icon_event

# ── DIALOGS ────────────────────────────────────────────────────────────────────
class Dialog:
    def __init__(self, screen, title, w, h):
        self.screen = screen
        self.title  = title
        self.w, self.h = w, h
        self.x = (WINDOW_WIDTH  - w) // 2
        self.y = (WINDOW_HEIGHT - h) // 2
        self.rect = pygame.Rect(self.x, self.y, w, h)
        self.done   = False
        self.result = None
        self._overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        self._overlay.fill((0, 0, 0, 100))

    def _draw_frame(self):
        self.screen.blit(self._overlay, (0,0))
        pygame.draw.rect(self.screen, SYS_BTN_FACE, self.rect)
        draw_edge(self.screen, self.rect, raised=True)
        title_r = pygame.Rect(self.x+2, self.y+2, self.w-4, 20)
        pygame.draw.rect(self.screen, SYS_HIGHLIGHT, title_r)
        draw_text(self.screen, self.title, (title_r.x+4, title_r.y+3), WHITE, FONT_SMALL)
        xr = pygame.Rect(title_r.right-18, title_r.y+1, 16, 16)
        pygame.draw.rect(self.screen, SYS_BTN_FACE, xr)
        draw_edge(self.screen, xr, raised=True)
        draw_text(self.screen, "X", xr.center, BLACK, FONT_SMALL, True)
        return title_r, xr

    def run(self):
        clock = pygame.time.Clock()
        while not self.done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.done = True; self.result = None
                self.handle_event(event)
            self.draw()
            pygame.display.flip()
            clock.tick(60)
        return self.result

    def handle_event(self, event): pass
    def draw(self): self._draw_frame()


class MessageBox(Dialog):
    def __init__(self, screen, title, message, buttons=("OK",)):
        lines = message.split('\n')
        # FIX B22: width accounts for button row so they never overflow
        btn_row_w = len(buttons) * 80          # 70 wide + 10 gap each
        txt_w     = max(FONT_SMALL.size(l)[0] for l in lines) + 60
        w = max(300, btn_row_w + 40, txt_w)
        h = 80 + len(lines) * 18 + 40
        super().__init__(screen, title, w, h)
        self.message = message
        self.buttons = buttons

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            lines = self.message.split('\n')
            by = self.h - 40
            bw = 70; gap = 10
            total = len(self.buttons) * (bw + gap) - gap
            bstart = (self.w - total) // 2
            for i, b in enumerate(self.buttons):
                r = pygame.Rect(self.x + bstart + i*(bw+gap), self.y+by, bw, 24)
                if r.collidepoint(event.pos):
                    self.result = b; self.done = True

    def draw(self):
        _, xr = self._draw_frame()
        lines = self.message.split('\n')
        for i, l in enumerate(lines):
            draw_text(self.screen, l, (self.x+20, self.y+34+i*18), SYS_TEXT, FONT_SMALL)
        by=self.h-40; bw=70; gap=10
        total=len(self.buttons)*(bw+gap)-gap
        bstart=(self.w-total)//2
        for i, b in enumerate(self.buttons):
            r = pygame.Rect(self.x+bstart+i*(bw+gap), self.y+by, bw, 24)
            pygame.draw.rect(self.screen, SYS_BTN_FACE, r)
            draw_edge(self.screen, r, raised=True)
            draw_text(self.screen, b, r.center, SYS_TEXT, FONT_SMALL, True)


class InputDialog(Dialog):
    def __init__(self, screen, title, prompt, default=""):
        super().__init__(screen, title, 340, 120)
        self.prompt = prompt
        self.value  = default
        self.cursor = len(default)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.result = self.value; self.done = True
            elif event.key == pygame.K_ESCAPE:
                self.done = True
            elif event.key == pygame.K_BACKSPACE:
                if self.cursor > 0:
                    self.value = self.value[:self.cursor-1] + self.value[self.cursor:]
                    self.cursor -= 1
            elif event.key == pygame.K_LEFT:
                self.cursor = max(0, self.cursor-1)
            elif event.key == pygame.K_RIGHT:
                self.cursor = min(len(self.value), self.cursor+1)
            else:
                ch = event.unicode
                if ch and ch.isprintable():
                    self.value = self.value[:self.cursor] + ch + self.value[self.cursor:]
                    self.cursor += 1
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            ok = pygame.Rect(self.x+self.w-170, self.y+86, 70, 24)
            cn = pygame.Rect(self.x+self.w-90,  self.y+86, 70, 24)
            if ok.collidepoint(event.pos): self.result = self.value; self.done = True
            if cn.collidepoint(event.pos): self.done = True

    def draw(self):
        self._draw_frame()
        draw_text(self.screen, self.prompt, (self.x+14, self.y+34), SYS_TEXT, FONT_SMALL)
        ir = pygame.Rect(self.x+14, self.y+52, self.w-28, 22)
        pygame.draw.rect(self.screen, SYS_WINDOW, ir)
        draw_edge(self.screen, ir, raised=False)
        draw_text(self.screen, self.value, (ir.x+4, ir.y+4), SYS_TEXT, FONT_SMALL)
        if pygame.time.get_ticks() % 1000 < 500:
            cx = ir.x + 4 + FONT_SMALL.size(self.value[:self.cursor])[0]
            pygame.draw.line(self.screen, BLACK, (cx, ir.y+3), (cx, ir.y+18), 1)
        for lbl, bx in [("OK", self.w-170), ("Cancel", self.w-90)]:
            r = pygame.Rect(self.x+bx, self.y+86, 70, 24)
            pygame.draw.rect(self.screen, SYS_BTN_FACE, r)
            draw_edge(self.screen, r, raised=True)
            draw_text(self.screen, lbl, r.center, SYS_TEXT, FONT_SMALL, True)

# ── DATA STRUCTURES ────────────────────────────────────────────────────────────
class Event:
    def __init__(self, name="New Event", trigger=0, actions=None):
        self.name    = name
        self.trigger = trigger
        self.actions = actions or []

class Warp:
    def __init__(self):
        self.origin_section = 0; self.origin_x = 0; self.origin_y = 0
        self.dest_section = 0;   self.dest_x = 0;   self.dest_y = 0
        self.direction = 0; self.style = 0; self.locked = False
        self.stars_needed = 0; self.exit_type = 0

# ── SPRITE CLASSES ─────────────────────────────────────────────────────────────
class GameObject(pygame.sprite.Sprite):
    # FIX B03: layer_index is ALWAYS an int from now on
    def __init__(self, x, y, obj_type, layer_idx=0, event_id=-1, flags=0):
        super().__init__()
        self.rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
        self.layer_index = layer_idx   # always int
        self.obj_type    = obj_type
        self.event_id    = event_id
        self.flags       = flags


class Tile(GameObject):
    def __init__(self, x, y, tile_type, layer_idx=0, event_id=-1, flags=0):
        super().__init__(x, y, tile_type, layer_idx, event_id, flags)
        self.tile_type = tile_type
        self.is_solid  = tile_type not in ('coin', 'water', 'lava')
        self.update_image()

    def update_image(self):
        type_id = TILE_SMBX_IDS.get(self.tile_type, 1)
        if USE_GRAPHICS and type_id in tile_images:
            self.image = tile_images[type_id]
            return
        # FIX B09: use SRCALPHA surface for tiles that need transparency
        flags = pygame.SRCALPHA if self.tile_type in ('water','lava','coin','semisolid') else 0
        self.image = pygame.Surface((GRID_SIZE, GRID_SIZE), flags)
        col = get_theme_color(self.tile_type)
        if not flags:
            self.image.fill(col)
        if self.tile_type == 'question':
            draw_text(self.image,'?',(GRID_SIZE//2,GRID_SIZE//2),BLACK,FONT_SMALL,True)
        elif self.tile_type == 'brick':
            pygame.draw.line(self.image,BLACK,(0,GRID_SIZE//2),(GRID_SIZE,GRID_SIZE//2),2)
            pygame.draw.line(self.image,BLACK,(GRID_SIZE//2,0),(GRID_SIZE//2,GRID_SIZE),2)
        elif self.tile_type == 'coin':
            pygame.draw.circle(self.image,(*col,220),(GRID_SIZE//2,GRID_SIZE//2),GRID_SIZE//3)
        elif self.tile_type == 'pipe_vertical':
            self.image.fill((0,160,0))
            pygame.draw.rect(self.image,(0,200,0),(2,0,GRID_SIZE-4,8))
        elif self.tile_type == 'pipe_horizontal':
            self.image.fill((0,160,0))
            pygame.draw.rect(self.image,(0,200,0),(0,2,8,GRID_SIZE-4))
        elif self.tile_type == 'slope_left':
            pygame.draw.polygon(self.image,col,[(0,0),(GRID_SIZE,0),(0,GRID_SIZE)])
        elif self.tile_type == 'slope_right':
            pygame.draw.polygon(self.image,col,[(0,0),(GRID_SIZE,0),(GRID_SIZE,GRID_SIZE)])
        elif self.tile_type == 'water':
            self.image.fill((30,100,255,160))
        elif self.tile_type == 'lava':
            self.image.fill((255,80,0,200))
        elif self.tile_type == 'semisolid':
            self.image.fill((*col, 220))
        if not flags:
            pygame.draw.rect(self.image,(0,0,0,60),self.image.get_rect(),1)


class BGO(GameObject):
    def __init__(self, x, y, bgo_type, layer_idx=0, event_id=-1, flags=0):
        super().__init__(x, y, bgo_type, layer_idx, event_id, flags)
        self.bgo_type = bgo_type
        self.update_image()

    def update_image(self):
        type_id = BGO_SMBX_IDS.get(self.bgo_type, 5)
        if USE_GRAPHICS and type_id in bgo_images:
            self.image = bgo_images[type_id]
            return
        # FIX B15: use the corrected get_theme_color which handles both prefixes
        self.image = pygame.Surface((GRID_SIZE, GRID_SIZE), pygame.SRCALPHA)
        color = get_theme_color(self.bgo_type)
        pygame.draw.rect(self.image, (*color, 200), self.image.get_rect().inflate(-4,-4))
        pygame.draw.rect(self.image, (*color, 255), self.image.get_rect().inflate(-4,-4), 2)


class NPC(GameObject):
    def __init__(self, x, y, npc_type, layer_idx=0, event_id=-1, flags=0,
                 direction=1, special_data=0):
        super().__init__(x, y, npc_type, layer_idx, event_id, flags)
        self.npc_type    = npc_type
        self.direction   = direction
        self.special_data= special_data
        self.velocity    = pygame.Vector2(direction * 1, 0)
        self.on_ground   = False          # FIX B16
        self.state       = 'normal'
        self.frame       = 0
        self.update_image()

    def update_image(self):
        type_id = NPC_SMBX_IDS.get(self.npc_type, 1)
        if USE_GRAPHICS and type_id in npc_images:
            self.image = npc_images[type_id]
            return
        self.image = pygame.Surface((GRID_SIZE, GRID_SIZE), pygame.SRCALPHA)
        color = get_theme_color(self.npc_type)
        if self.npc_type == 'goomba':
            pygame.draw.ellipse(self.image, color, (4,4,GRID_SIZE-8,GRID_SIZE-4))
            pygame.draw.rect(self.image,color,(0,GRID_SIZE-8,GRID_SIZE,8))
        elif self.npc_type.startswith('koopa'):
            pygame.draw.rect(self.image,color,(4,4,GRID_SIZE-8,GRID_SIZE-4))
        elif self.npc_type == 'piranha':
            pygame.draw.rect(self.image,color,(8,8,GRID_SIZE-16,GRID_SIZE-8))
            pygame.draw.circle(self.image,(255,255,255),(GRID_SIZE//2,12),4)
        elif self.npc_type == 'thwomp':
            pygame.draw.rect(self.image,(100,100,100),(0,0,GRID_SIZE,GRID_SIZE))
            pygame.draw.rect(self.image,(50,50,50),(4,4,GRID_SIZE-8,GRID_SIZE-8))
        else:
            pygame.draw.rect(self.image,color,(4,4,GRID_SIZE-8,GRID_SIZE-4))

    def _is_flying(self):
        return self.npc_type in ('lakitu','podoboo','piranha_fire')

    def update(self, solid_tiles, player, events):
        if not self._is_flying():
            self.velocity.y += GRAVITY
            self.velocity.y  = min(self.velocity.y, TERMINAL_VELOCITY)
        self.rect.x += int(self.velocity.x)
        self._collide(solid_tiles, 'x')
        self.rect.y += int(self.velocity.y)
        self.on_ground = False
        self._collide(solid_tiles, 'y')

    def _collide(self, tiles, axis):
        for t in tiles:
            if not self.rect.colliderect(t.rect):
                continue
            if axis == 'x':
                if self.velocity.x > 0: self.rect.right = t.rect.left
                else:                   self.rect.left  = t.rect.right
                self.velocity.x *= -1
            else:
                if self.velocity.y > 0:
                    self.rect.bottom = t.rect.top
                    self.on_ground = True        # FIX B16
                else:
                    self.rect.top = t.rect.bottom
                self.velocity.y = 0
            if t.tile_type == 'lava':
                self.kill()
            elif t.tile_type == 'water':
                self.velocity.y *= 0.5


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.rect        = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
        self.image       = pygame.Surface((GRID_SIZE, GRID_SIZE))
        self.image.fill(RED)
        self.velocity    = pygame.Vector2(0, 0)
        self.on_ground   = False
        self.powerup_state  = 0
        self.invincible  = 0
        self.coins       = 0
        self.score       = 0
        self.jump_held   = False
        # FIX B30: clamp variable jump timer to avoid runaway boosts
        self.variable_jump_timer = 0
        self.level_start = (x, y)

    def update(self, solid_tiles, npc_group, events):
        keys = pygame.key.get_pressed()
        self.velocity.x = 0
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: self.velocity.x = -MOVE_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.velocity.x =  MOVE_SPEED

        if keys[pygame.K_SPACE]:
            if self.on_ground and not self.jump_held:
                self.velocity.y        = JUMP_STRENGTH
                self.on_ground         = False
                self.jump_held         = True
                # FIX B30: cap at 10 frames so players can't hold-jump forever
                self.variable_jump_timer = min(10, 8)
            elif self.variable_jump_timer > 0 and self.velocity.y < 0:
                self.velocity.y -= 0.4
                self.variable_jump_timer -= 1
        else:
            self.jump_held           = False
            self.variable_jump_timer = 0

        self.velocity.y = min(self.velocity.y + GRAVITY, TERMINAL_VELOCITY)
        self.rect.x += int(self.velocity.x)
        self._collide(solid_tiles, 'x')
        self.rect.y += int(self.velocity.y)
        self.on_ground = False
        self._collide(solid_tiles, 'y')

        # FIX B26/B28: coin collection
        layer_tiles = solid_tiles  # already includes solid only; coins are non-solid
        # Check coin tiles separately
        for t in (t for t in (t for layer in _current_section_layers
                               for t in layer.tiles) if t.tile_type == 'coin'):
            if self.rect.colliderect(t.rect):
                t.kill()
                self.coins += 1
                self.score += 200

        # NPC collisions
        for npc in pygame.sprite.spritecollide(self, npc_group, False):
            if self.velocity.y > 0 and self.rect.bottom <= npc.rect.centery + 8:
                npc.kill()
                self.velocity.y = JUMP_STRENGTH * 0.7
                self.score += 100
                if npc.npc_type == 'mushroom': self.powerup_state = 1
                elif npc.npc_type == 'flower': self.powerup_state = 2
                elif npc.npc_type == 'star':   self.invincible = 300
                elif npc.npc_type == '1up':    self.score += 1000
            elif self.invincible <= 0:
                if self.powerup_state > 0:
                    self.powerup_state = 0
                    self.invincible    = 120
                else:
                    self._respawn()
        if self.invincible > 0:
            self.invincible -= 1

    def _respawn(self):
        self.rect.topleft = self.level_start
        self.velocity.update(0, 0)
        self.score     = max(0, self.score - 50)
        self.coins     = 0
        self.invincible= 60

    def _collide(self, tiles, axis):
        for t in tiles:
            if not self.rect.colliderect(t.rect):
                continue
            if t.tile_type == 'lava':
                self._respawn(); return
            elif t.tile_type == 'water':
                self.velocity.y *= 0.5
            elif t.tile_type == 'pswitch':
                t.kill()
            # FIX B27: slope math clamped to valid range
            if t.tile_type == 'slope_left' and axis == 'y' and self.velocity.y >= 0:
                offset = max(0, min(GRID_SIZE, self.rect.right - t.rect.left))
                self.rect.bottom = t.rect.top + offset
                self.on_ground   = True
                self.velocity.y  = 0
                continue
            if t.tile_type == 'slope_right' and axis == 'y' and self.velocity.y >= 0:
                offset = max(0, min(GRID_SIZE, t.rect.right - self.rect.left))
                self.rect.bottom = t.rect.top + offset
                self.on_ground   = True
                self.velocity.y  = 0
                continue
            if axis == 'x':
                if self.velocity.x > 0: self.rect.right = t.rect.left
                else:                   self.rect.left  = t.rect.right
                self.velocity.x = 0
            elif axis == 'y':
                if self.velocity.y > 0:
                    self.rect.bottom = t.rect.top
                    self.on_ground   = True
                else:
                    self.rect.top = t.rect.bottom
                self.velocity.y = 0

    def draw(self, surf, sx, sy):
        if self.invincible > 0 and (self.invincible // 5) % 2 == 0:
            return
        surf.blit(self.image, (sx, sy))


# global reference used by Player coin collection (set by Editor.update)
_current_section_layers = []

# ── CAMERA ─────────────────────────────────────────────────────────────────────
class Camera:
    """
    camera.camera.x / .y are offsets in WORLD pixels (negative = scrolled right/down).
    Screen position = (world_pos + camera.x) * zoom + CANVAS_ORIGIN.
    FIX B07/B31/B32: all arithmetic is now consistent with this convention.
    """
    def __init__(self, width, height):
        self.camera       = pygame.Rect(0, 0, width, height)
        self.width        = width
        self.height       = height
        self.zoom         = 1.0

    def _clamp(self):
        min_x = -(self.width  - CANVAS_WIDTH  / self.zoom)
        min_y = -(self.height - CANVAS_HEIGHT / self.zoom)
        self.camera.x = max(min_x, min(0.0, self.camera.x))
        self.camera.y = max(min_y, min(0.0, self.camera.y))

    def update(self, target):
        """Centre camera on target sprite (used during playtest)."""
        self.camera.x = CANVAS_WIDTH  / (2 * self.zoom) - target.rect.centerx
        self.camera.y = CANVAS_HEIGHT / (2 * self.zoom) - target.rect.centery
        self._clamp()

    def move(self, dx, dy):
        """Move by dx/dy world pixels."""
        self.camera.x += dx
        self.camera.y += dy
        self._clamp()

    def world_to_screen(self, wx, wy):
        """Convert world coords to screen coords (FIX B06/B07/B08)."""
        sx = int((wx + self.camera.x) * self.zoom) + SIDEBAR_WIDTH
        sy = int((wy + self.camera.y) * self.zoom) + CANVAS_Y
        return sx, sy

    def screen_to_world(self, sx, sy):
        """Convert screen coords to world coords (FIX B08)."""
        wx = (sx - SIDEBAR_WIDTH) / self.zoom - self.camera.x
        wy = (sy - CANVAS_Y)      / self.zoom - self.camera.y
        return wx, wy

# ── LAYER & SECTION ────────────────────────────────────────────────────────────
class Layer:
    def __init__(self, name="Layer 1", visible=True, locked=False):
        self.name    = name
        self.visible = visible
        self.locked  = locked
        self.tiles   = pygame.sprite.Group()
        self.bgos    = pygame.sprite.Group()
        self.npcs    = pygame.sprite.Group()
        self.tile_map= {}   # (px_x, px_y) -> Tile

    def add_tile(self, tile):
        key = (tile.rect.x, tile.rect.y)
        if key in self.tile_map:
            old = self.tile_map[key]
            self.tiles.remove(old)
        self.tiles.add(tile)
        self.tile_map[key] = tile

    def remove_tile(self, tile):
        key = (tile.rect.x, tile.rect.y)
        self.tiles.discard(tile)
        if self.tile_map.get(key) is tile:
            del self.tile_map[key]


class Section:
    def __init__(self, cols=100, rows=30):
        self.width  = cols * GRID_SIZE
        self.height = rows * GRID_SIZE
        self.layers = [Layer("Layer 1")]
        self.current_layer_idx = 0
        # FIX B33: use current theme background colour
        self.bg_color = themes[current_theme].get('background', (92,148,252))
        self.music    = 1
        self.events   = []
        self.warps    = []

    def current_layer(self):
        return self.layers[self.current_layer_idx]

    def get_solid_tiles(self):
        return [t for layer in self.layers if layer.visible
                for t in layer.tiles if t.is_solid]


class Level:
    def __init__(self):
        self.sections           = [Section()]
        self.current_section_idx= 0
        self.start_pos          = (100, 500)
        self.name               = "Untitled"
        self.author             = "Unknown"
        self.no_background      = False
        self.time_limit         = 300
        self.stars              = 0
        self.level_id           = 0

    def current_section(self):
        return self.sections[self.current_section_idx]

    def current_layer(self):
        return self.current_section().current_layer()

# ── FILE I/O ────────────────────────────────────────────────────────────────────
HDR_FIXED = 4 + 4 + 32 + 32 + 4 + 4 + 4   # = 84 bytes
HDR_PAD   = 128 - HDR_FIXED                  # = 44 bytes

def read_lvl(filename):
    level = Level()
    try:
        with open(filename, 'rb') as f:
            if f.read(4) != b'LVL\x1a':
                print("Not a valid SMBX level file"); return level
            f.read(4)  # version
            level.name        = f.read(32).decode('utf-8','ignore').strip('\x00')
            level.author      = f.read(32).decode('utf-8','ignore').strip('\x00')
            level.time_limit  = struct.unpack('<I', f.read(4))[0]
            level.stars       = struct.unpack('<I', f.read(4))[0]
            flags             = struct.unpack('<I', f.read(4))[0]
            level.no_background = bool(flags & 1)
            f.read(HDR_PAD)

            num_sections = struct.unpack('<I', f.read(4))[0]
            level.sections = []
            for _ in range(num_sections):
                sec         = Section()
                sec.width   = struct.unpack('<I', f.read(4))[0]
                sec.height  = struct.unpack('<I', f.read(4))[0]
                r,g,b       = struct.unpack('<BBB', f.read(3))
                sec.bg_color= (r, g, b); f.read(1)
                sec.music   = struct.unpack('<I', f.read(4))[0]

                nb = struct.unpack('<I', f.read(4))[0]
                for _ in range(nb):
                    x,y,tid,li,eid,fl = struct.unpack('<IIIIII', f.read(24))
                    if tid in TILE_ID_TO_NAME:
                        while len(sec.layers) <= li:
                            sec.layers.append(Layer(f"Layer {len(sec.layers)+1}"))
                        t = Tile(x, y, TILE_ID_TO_NAME[tid], layer_idx=li, event_id=eid, flags=fl)
                        sec.layers[li].add_tile(t)

                ng = struct.unpack('<I', f.read(4))[0]
                for _ in range(ng):
                    x,y,tid,li,fl = struct.unpack('<IIIII', f.read(20))
                    if tid in BGO_ID_TO_NAME:
                        while len(sec.layers) <= li:
                            sec.layers.append(Layer(f"Layer {len(sec.layers)+1}"))
                        sec.layers[li].bgos.add(BGO(x,y,BGO_ID_TO_NAME[tid],layer_idx=li,flags=fl))

                nn = struct.unpack('<I', f.read(4))[0]
                for _ in range(nn):
                    x,y,tid,li,eid,fl,dr,sp = struct.unpack('<IIIIIIII', f.read(32))
                    if tid in NPC_ID_TO_NAME:
                        while len(sec.layers) <= li:
                            sec.layers.append(Layer(f"Layer {len(sec.layers)+1}"))
                        n = NPC(x,y,NPC_ID_TO_NAME[tid],layer_idx=li,event_id=eid,flags=fl,
                                direction=1 if dr else -1, special_data=sp)
                        sec.layers[li].npcs.add(n)

                nw = struct.unpack('<I', f.read(4))[0]
                for _ in range(nw):
                    f.read(64)
                    sec.warps.append(Warp())

                nev = struct.unpack('<I', f.read(4))[0]
                for _ in range(nev):
                    nl   = struct.unpack('<B', f.read(1))[0]
                    name = f.read(nl).decode('utf-8')
                    trig = struct.unpack('<I', f.read(4))[0]
                    na   = struct.unpack('<I', f.read(4))[0]
                    acts = [struct.unpack('<III', f.read(12)) for _ in range(na)]
                    sec.events.append(Event(name, trig, acts))

                level.sections.append(sec)

        for sec in level.sections:
            for layer in sec.layers:
                for npc in list(layer.npcs):
                    if npc.npc_type == 'start':
                        level.start_pos = (npc.rect.x, npc.rect.y)
                        layer.npcs.remove(npc)
    except Exception as e:
        print("Load error:", e)
    return level


def write_lvl(filename, level):
    with open(filename, 'wb') as f:
        f.write(b'LVL\x1a')
        f.write(struct.pack('<I', 1))
        f.write(level.name.encode()[:31].ljust(32, b'\x00'))
        f.write(level.author.encode()[:31].ljust(32, b'\x00'))
        f.write(struct.pack('<I', level.time_limit))
        f.write(struct.pack('<I', level.stars))
        f.write(struct.pack('<I', 1 if level.no_background else 0))
        f.write(b'\x00' * HDR_PAD)   # correct fixed padding

        f.write(struct.pack('<I', len(level.sections)))
        for sec in level.sections:
            f.write(struct.pack('<I', sec.width))
            f.write(struct.pack('<I', sec.height))
            f.write(struct.pack('<BBB', *sec.bg_color[:3]))
            f.write(b'\x00')
            f.write(struct.pack('<I', sec.music))

            blocks = [(t.rect.x, t.rect.y, TILE_SMBX_IDS.get(t.tile_type,1),
                       t.layer_index, t.event_id, t.flags)
                      for li, layer in enumerate(sec.layers) for t in layer.tiles]
            f.write(struct.pack('<I', len(blocks)))
            for b in blocks: f.write(struct.pack('<IIIIII', *b))

            bgos = [(b.rect.x, b.rect.y, BGO_SMBX_IDS.get(b.bgo_type,5),
                     b.layer_index, b.flags)
                    for layer in sec.layers for b in layer.bgos]
            f.write(struct.pack('<I', len(bgos)))
            for b in bgos: f.write(struct.pack('<IIIII', *b))

            npcs = [(n.rect.x, n.rect.y, NPC_SMBX_IDS.get(n.npc_type,1),
                     n.layer_index, n.event_id, n.flags,
                     1 if n.direction > 0 else 0, n.special_data)
                    for layer in sec.layers for n in layer.npcs]
            f.write(struct.pack('<I', len(npcs)))
            for n in npcs: f.write(struct.pack('<IIIIIIII', *n))

            f.write(struct.pack('<I', len(sec.warps)))
            for _ in sec.warps: f.write(b'\x00' * 64)

            f.write(struct.pack('<I', len(sec.events)))
            for ev in sec.events:
                nb = ev.name.encode('utf-8')
                f.write(struct.pack('<B', len(nb))); f.write(nb)
                f.write(struct.pack('<I', ev.trigger))
                f.write(struct.pack('<I', len(ev.actions)))
                for a in ev.actions: f.write(struct.pack('<III', *a))

# ── MENU SYSTEM ────────────────────────────────────────────────────────────────
class MenuItem:
    def __init__(self, label, callback=None, shortcut="",
                 checkable=False, checked=False, separator=False):
        self.label     = label
        self.callback  = callback
        self.shortcut  = shortcut
        self.checkable = checkable
        self.checked   = checked
        self.separator = separator
        self.enabled   = True


class DropMenu:
    ITEM_H = 18
    PAD    =  6

    def __init__(self, items):
        self.items   = items
        self.hovered = -1
        w = max((FONT_SMALL.size(i.label + ("  "+i.shortcut if i.shortcut else ""))[0] + 30)
                for i in items if not i.separator)
        self.w = max(140, w)
        self.h = sum(6 if i.separator else self.ITEM_H for i in items) + self.PAD * 2

    def draw(self, surf, x, y):
        r = pygame.Rect(x, y, self.w, self.h)
        pygame.draw.rect(surf, SYS_BTN_FACE, r)
        draw_edge(surf, r, raised=True)
        cy = y + self.PAD
        for i, item in enumerate(self.items):
            if item.separator:
                pygame.draw.line(surf,SYS_BTN_DARK,(x+4,cy+3),(x+self.w-4,cy+3))
                cy += 6; continue
            ir = pygame.Rect(x+2, cy, self.w-4, self.ITEM_H)
            if i == self.hovered and item.enabled:
                pygame.draw.rect(surf, SYS_HIGHLIGHT, ir)
            col = WHITE if (i==self.hovered and item.enabled) else (GRAY if not item.enabled else SYS_TEXT)
            if item.checkable:
                draw_text(surf, "✓" if item.checked else " ", (x+8,cy+2), col, FONT_SMALL)
            draw_text(surf, item.label, (x+22,cy+2), col, FONT_SMALL)
            if item.shortcut:
                sw = FONT_SMALL.size(item.shortcut)[0]
                draw_text(surf, item.shortcut, (x+self.w-sw-6,cy+2), col, FONT_SMALL)
            cy += self.ITEM_H

    def hit_item(self, pos, ox, oy):
        cy = oy + self.PAD
        for i, item in enumerate(self.items):
            if item.separator: cy += 6; continue
            if pygame.Rect(ox+2, cy, self.w-4, self.ITEM_H).collidepoint(pos):
                return i
            cy += self.ITEM_H
        return -1

    def update_hover(self, pos, ox, oy):
        self.hovered = self.hit_item(pos, ox, oy)


class MenuBar:
    BAR_H = MENU_HEIGHT

    def __init__(self, menus_def):
        self.menus    = []
        self.open_idx = -1
        x = 4
        for label, items in menus_def:
            w  = FONT_MENU.size(label)[0] + 14
            dm = DropMenu(items)
            self.menus.append([label, x, w, dm])
            x += w

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if my < self.BAR_H:
                for i, (lbl,bx,bw,dm) in enumerate(self.menus):
                    if bx <= mx < bx+bw:
                        self.open_idx = -1 if self.open_idx==i else i
                        return True
            elif self.open_idx >= 0:
                lbl,bx,bw,dm = self.menus[self.open_idx]
                idx = dm.hit_item(event.pos, bx, self.BAR_H)
                if idx >= 0:
                    item = dm.items[idx]
                    if item.enabled and item.callback:
                        item.callback()
                        if item.checkable: item.checked = not item.checked
                self.open_idx = -1
                return True
            else:
                self.open_idx = -1
        if event.type == pygame.MOUSEMOTION and self.open_idx >= 0:
            lbl,bx,bw,dm = self.menus[self.open_idx]
            dm.update_hover(event.pos, bx, self.BAR_H)
            for i,(l2,bx2,bw2,dm2) in enumerate(self.menus):
                if bx2 <= event.pos[0] < bx2+bw2 and event.pos[1] < self.BAR_H:
                    self.open_idx = i
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.open_idx = -1
        return False

    def draw(self, surf):
        pygame.draw.rect(surf,SYS_BTN_FACE,(0,0,WINDOW_WIDTH,self.BAR_H))
        pygame.draw.line(surf,SYS_BTN_DARK,(0,self.BAR_H-1),(WINDOW_WIDTH,self.BAR_H-1))
        for i,(lbl,bx,bw,dm) in enumerate(self.menus):
            r = pygame.Rect(bx,1,bw,self.BAR_H-2)
            if i == self.open_idx:
                pygame.draw.rect(surf,SYS_HIGHLIGHT,r)
                draw_text(surf,lbl,(bx+7,3),WHITE,FONT_MENU)
            else:
                draw_text(surf,lbl,(bx+7,3),SYS_TEXT,FONT_MENU)
        if self.open_idx >= 0:
            lbl,bx,bw,dm = self.menus[self.open_idx]
            dm.draw(surf,bx,self.BAR_H)

# ── TOOLBAR BUTTON ─────────────────────────────────────────────────────────────
class ToolbarButton:
    def __init__(self, rect, icon_key, callback=None, tooltip="", toggle=False):
        self.rect     = pygame.Rect(rect)
        self.icon_key = icon_key
        self.callback = callback
        self.tooltip  = tooltip
        self.hovered  = False
        self.pressed  = False
        self.toggle   = toggle
        self.active   = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.pressed = True; return True
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.pressed and self.rect.collidepoint(event.pos) and self.callback:
                if self.toggle: self.active = not self.active
                self.callback()
            self.pressed = False
        # FIX B25: clear hover when mouse leaves
        if event.type == pygame.WINDOWLEAVE:
            self.hovered = False
        return False

    def draw(self, surf):
        sunken = self.pressed or (self.toggle and self.active)
        if sunken:
            pygame.draw.rect(surf,SYS_BTN_FACE,self.rect)
            pygame.draw.line(surf,SYS_BTN_DARK,self.rect.topleft,self.rect.topright)
            pygame.draw.line(surf,SYS_BTN_DARK,self.rect.topleft,self.rect.bottomleft)
        elif self.hovered:
            pygame.draw.rect(surf,SYS_BTN_FACE,self.rect)
            pygame.draw.line(surf,SYS_BTN_LIGHT,self.rect.topleft,self.rect.topright)
            pygame.draw.line(surf,SYS_BTN_LIGHT,self.rect.topleft,self.rect.bottomleft)
            pygame.draw.line(surf,SYS_BTN_DARK,self.rect.bottomleft,self.rect.bottomright)
            pygame.draw.line(surf,SYS_BTN_DARK,self.rect.topright,self.rect.bottomright)
        else:
            pygame.draw.rect(surf,SYS_BTN_FACE,self.rect)
        fn = ICON_FNS.get(self.icon_key)
        if fn:
            off = (1,1) if sunken else (0,0)
            fn(surf, self.rect.move(*off))

# ── SIDEBAR ────────────────────────────────────────────────────────────────────
class Sidebar:
    def __init__(self):
        self.rect             = pygame.Rect(0, CANVAS_Y, SIDEBAR_WIDTH, CANVAS_HEIGHT)
        self.categories       = ["Tiles","BGOs","NPCs","Layers"]
        self.current_category = "Tiles"
        self.items            = {
            "Tiles":  list(TILE_SMBX_IDS.keys()),
            "BGOs":   list(BGO_SMBX_IDS.keys()),
            "NPCs":   list(NPC_SMBX_IDS.keys()),
            "Layers": [],
        }
        self.selected_item = 'ground'
        self.tab_h   = 20
        self.title_h = 18
        self.scroll  = 0

    def draw(self, surf, level):
        pygame.draw.rect(surf, SYS_BTN_FACE, self.rect)
        draw_edge(surf, self.rect, raised=False)
        tr = pygame.Rect(self.rect.x+2, self.rect.y+2, self.rect.width-4, self.title_h)
        pygame.draw.rect(surf, SYS_HIGHLIGHT, tr)
        draw_text(surf,"Item Palette",(tr.x+4,tr.y+3),WHITE,FONT_SMALL)
        tab_y = self.rect.y + self.title_h + 2
        tab_w = self.rect.width // len(self.categories)
        for i, cat in enumerate(self.categories):
            r   = pygame.Rect(self.rect.x+2+i*tab_w, tab_y, tab_w-2, self.tab_h)
            sel = (cat == self.current_category)
            pygame.draw.rect(surf, SYS_WINDOW if sel else SYS_BTN_FACE, r)
            draw_edge(surf, r, raised=not sel)
            draw_text(surf, cat, r.center, SYS_TEXT, FONT_SMALL, True)
        content = pygame.Rect(self.rect.x+2, tab_y+self.tab_h,
                              self.rect.width-4, self.rect.height-self.title_h-self.tab_h-4)
        pygame.draw.rect(surf, SYS_WINDOW, content)
        if self.current_category == "Layers":
            self._draw_layers(surf, content, level)
        else:
            self._draw_items(surf, content)

    def _draw_items(self, surf, area):
        items = self.items[self.current_category]
        cols  = 5
        cell  = 36
        for i, item in enumerate(items):
            col = i % cols
            row = i // cols - self.scroll
            if row < 0: continue
            r = pygame.Rect(area.x+4+col*cell, area.y+4+row*cell, 32, 32)
            if r.bottom > area.bottom: break
            # Selection highlight
            if item == self.selected_item:
                pygame.draw.rect(surf, SYS_HIGHLIGHT2, r.inflate(4, 4))
            # Draw checkerboard background (shows alpha)
            cb_colors = ((180,180,180,255),(220,220,220,255))
            for cy in range(2):
                for cx in range(2):
                    pygame.draw.rect(surf, cb_colors[(cx+cy)%2],
                                     (r.x + cx*16, r.y + cy*16, 16, 16))
            # Draw actual sprite thumbnail
            thumb = get_sidebar_thumb(item, self.current_category)
            if thumb is not None:
                surf.blit(thumb, r.topleft)
            else:
                # Fallback: coloured block with label initial
                color = get_theme_color(item)
                pygame.draw.rect(surf, color, r)
                if FONT_SMALL:
                    lbl = item[0].upper()
                    draw_text(surf, lbl, r.center, BLACK, FONT_SMALL, True)
            # Border
            pygame.draw.rect(surf, (80, 80, 80, 255), r, 1)
            # Small tooltip label at bottom of cell on hover (skip for perf; border is enough)


    def _draw_layers(self, surf, area, level):
        y = area.y + 5
        sec = level.current_section()
        for i, layer in enumerate(sec.layers):
            r = pygame.Rect(area.x+2, y, area.width-4, 18)
            pygame.draw.rect(surf, SYS_HIGHLIGHT if i==sec.current_layer_idx else SYS_WINDOW, r)
            col = WHITE if i==sec.current_layer_idx else SYS_TEXT
            draw_text(surf, layer.name, (r.x+5,r.y+1), col, FONT_SMALL)
            pygame.draw.circle(surf, GREEN if layer.visible else RED, (r.right-8,r.centery),4)
            pygame.draw.rect(surf, GRAY if layer.locked else SYS_BTN_FACE, (r.right-20,r.y+2,8,8))
            y += 22

    def handle_click(self, pos, level):
        tab_y = self.rect.y + self.title_h + 2
        tab_w = self.rect.width // len(self.categories)
        for i, cat in enumerate(self.categories):
            r = pygame.Rect(self.rect.x+2+i*tab_w, tab_y, tab_w-2, self.tab_h)
            if r.collidepoint(pos):
                self.current_category = cat; return True
        content = pygame.Rect(self.rect.x+2, tab_y+self.tab_h,
                              self.rect.width-4, self.rect.height-self.title_h-self.tab_h-4)
        if self.current_category == "Layers":
            y = content.y + 5
            sec = level.current_section()
            for i, layer in enumerate(sec.layers):
                r = pygame.Rect(content.x+2, y, content.width-4, 18)
                if r.collidepoint(pos):
                    if pos[0] > r.right-20:   layer.locked  = not layer.locked
                    elif pos[0] > r.right-35: layer.visible = not layer.visible
                    else: sec.current_layer_idx = i
                    return True
                y += 22
        else:
            items = self.items[self.current_category]
            cols  = 5; cell = 36
            for i, item in enumerate(items):
                col = i % cols; row = i // cols - self.scroll
                if row < 0: continue
                r = pygame.Rect(content.x+4+col*cell, content.y+4+row*cell, 32, 32)
                if r.collidepoint(pos):
                    self.selected_item = item; return True
        return False

    def handle_scroll(self, dy):
        self.scroll = max(0, self.scroll - dy)

# ── EDITOR ─────────────────────────────────────────────────────────────────────
class Editor:
    def __init__(self, level, screen):
        self.screen      = screen
        self.level       = level
        sec              = level.current_section()
        self.camera      = Camera(sec.width, sec.height)
        self.playtest_mode = False
        self.player      = None
        self.undo_stack  = []
        self.redo_stack  = []
        self.sidebar     = Sidebar()
        self.drag_draw   = False
        self.drag_erase  = False
        self.current_file= None
        self.selection   = []
        self.clipboard   = []
        self.tool        = 'pencil'
        self.grid_enabled= True
        self.mouse_pos   = (0, 0)
        self.tooltip_text= ""
        self.status_msg  = ""
        # cached scaled images for zoom rendering
        self._img_cache  = {}
        self._cache_zoom = 1.0
        self._build_menu()
        self._build_toolbar()

    # ── SCALED IMAGE CACHE (FIX B06) ──────────────────────────────────────────
    def _scaled(self, img):
        zoom = self.camera.zoom
        if zoom == 1.0:
            return img
        if zoom != self._cache_zoom:
            self._img_cache.clear()
            self._cache_zoom = zoom
        key = id(img)
        if key not in self._img_cache:
            sz  = max(1, int(GRID_SIZE * zoom))
            self._img_cache[key] = pygame.transform.scale(img, (sz, sz))
        return self._img_cache[key]

    # ── MENU SETUP ────────────────────────────────────────────────────────────
    def _build_menu(self):
        MI = MenuItem
        file_items = [
            MI("New Level",      self.cmd_new,        "Ctrl+N"),
            MI("Open Level…",    self.cmd_open,       "Ctrl+O"),
            MI("Save",           self.cmd_save,       "Ctrl+S"),
            MI("Save As…",       self.cmd_save_as,    "Ctrl+Shift+S"),
            MI("",separator=True),
            MI("Export as JSON", self.cmd_export_json),
            MI("",separator=True),
            MI("Exit",           self.cmd_exit,       "Alt+F4"),
        ]
        edit_items = [
            MI("Undo",       self.undo,            "Ctrl+Z"),
            MI("Redo",       self.redo,            "Ctrl+Y"),
            MI("",separator=True),
            MI("Cut",        self.cut_selection,   "Ctrl+X"),
            MI("Copy",       self.copy_selection,  "Ctrl+C"),
            MI("Paste",      self.paste_clipboard, "Ctrl+V"),
            MI("Delete",     self.delete_selected, "Del"),
            MI("",separator=True),
            MI("Select All", self.select_all,      "Ctrl+A"),
            MI("Deselect",   self.deselect_all,    "Esc"),
        ]
        view_items = [
            MI("Zoom In",      self.cmd_zoom_in,    "Ctrl+="),
            MI("Zoom Out",     self.cmd_zoom_out,   "Ctrl+-"),
            MI("Reset Zoom",   self.cmd_zoom_reset, "Ctrl+0"),
            MI("",separator=True),
            MI("Toggle Grid",  self.cmd_toggle_grid,"G", checkable=True, checked=True),
            MI("",separator=True),
            MI("Theme: SMB1",  lambda: self.cmd_set_theme('SMB1')),
            MI("Theme: SMB3",  lambda: self.cmd_set_theme('SMB3')),
            MI("Theme: SMW",   lambda: self.cmd_set_theme('SMW')),
        ]
        level_items = [
            MI("Level Properties…", self.cmd_properties, "F4"),
            MI("",separator=True),
            MI("Add Layer",         self.cmd_add_layer),
            MI("Layer Manager…",    self.cmd_layer_manager),
            MI("",separator=True),
            MI("Event Editor…",     self.cmd_event_editor, "F6"),
            MI("Warp Editor…",      self.cmd_warp_editor,  "F7"),
            MI("",separator=True),
            MI("Set Start Pos",     self.cmd_set_start),
            MI("Fill BG Colour",    self.cmd_fill_bg),
            MI("Clear All",         self.cmd_clear_all),
        ]
        tool_items = [
            MI("Select",  self.set_tool_select, "S"),
            MI("Pencil",  self.set_tool_pencil, "P"),
            MI("Eraser",  self.set_tool_erase,  "E"),
            MI("Fill",    self.set_tool_fill,   "F"),
            MI("",separator=True),
            MI("Event Trigger", self.set_tool_event, "T"),
        ]
        test_items = [
            MI("Playtest",     self.toggle_playtest,  "F5"),
            MI("",separator=True),
            MI("Reset Player", self.cmd_reset_player),
        ]
        help_items = [
            MI("Controls…", self.cmd_help,  "F1"),
            MI("About…",    self.cmd_about),
        ]
        self.menubar = MenuBar([
            ("File",  file_items),
            ("Edit",  edit_items),
            ("View",  view_items),
            ("Level", level_items),
            ("Tools", tool_items),
            ("Test",  test_items),
            ("Help",  help_items),
        ])

    def _build_toolbar(self):
        items = [
            ("new",      self.cmd_new,          "New Level (Ctrl+N)"),
            ("open",     self.cmd_open,         "Open Level (Ctrl+O)"),
            ("save",     self.cmd_save,         "Save (Ctrl+S)"),
            None,
            ("undo",     self.undo,             "Undo (Ctrl+Z)"),
            ("redo",     self.redo,             "Redo (Ctrl+Y)"),
            None,
            ("select",   self.set_tool_select,  "Select [S]"),
            ("pencil",   self.set_tool_pencil,  "Pencil [P]"),
            ("eraser",   self.set_tool_erase,   "Eraser [E]"),
            ("fill",     self.set_tool_fill,    "Fill [F]"),
            None,
            ("grid",     self.cmd_toggle_grid,  "Toggle Grid [G]",  True),
            ("zoom_in",  self.cmd_zoom_in,      "Zoom In  (Ctrl+=)"),
            ("zoom_out", self.cmd_zoom_out,     "Zoom Out (Ctrl+-)"),
            None,
            ("layer",    self.cmd_layer_manager,"Layer Manager"),
            ("event",    self.cmd_event_editor, "Event Editor [F6]"),
            ("props",    self.cmd_properties,   "Level Properties [F4]"),
            None,
            ("play",     self.toggle_playtest,  "Playtest [F5]", True),
        ]
        self.toolbar_btns = []
        x = SIDEBAR_WIDTH + 4
        for item in items:
            if item is None:
                x += 8; continue
            if len(item) == 4:
                ik, cb, tip, tog = item
                self.toolbar_btns.append(
                    ToolbarButton((x,MENU_HEIGHT+2,22,22), ik, cb, tip, toggle=tog))
            else:
                ik, cb, tip = item
                self.toolbar_btns.append(
                    ToolbarButton((x,MENU_HEIGHT+2,22,22), ik, cb, tip))
            x += 24

    # ── MENU COMMANDS ─────────────────────────────────────────────────────────
    def cmd_new(self):
        r = MessageBox(self.screen,"New Level","Discard current level?",("Yes","No")).run()
        if r == "Yes":
            self.level = Level()
            self.current_file = None
            sec = self.level.current_section()
            self.camera = Camera(sec.width, sec.height)
            self.undo_stack.clear(); self.redo_stack.clear(); self.selection.clear()
            self.status("New level created.")

    def cmd_open(self):
        fn = InputDialog(self.screen,"Open Level","Enter filename:","level.lvl").run()
        if fn:
            if os.path.exists(fn):
                self.level       = read_lvl(fn)
                self.current_file= fn
                sec = self.level.current_section()
                self.camera      = Camera(sec.width, sec.height)
                self.status(f"Opened: {fn}")
            else:
                MessageBox(self.screen,"Error",f"File not found:\n{fn}").run()

    def cmd_save(self):
        if not self.current_file: self.cmd_save_as(); return
        write_lvl(self.current_file, self.level)
        self.status(f"Saved: {self.current_file}")

    def cmd_save_as(self):
        fn = InputDialog(self.screen,"Save As","Enter filename:",
                         self.current_file or "level.lvl").run()
        if fn:
            self.current_file = fn
            write_lvl(fn, self.level)
            self.status(f"Saved as: {fn}")

    def cmd_export_json(self):
        fn  = (self.current_file or "level").replace(".lvl","") + ".json"
        sec = self.level.current_section()
        data= {"name":self.level.name,"author":self.level.author,
               "tiles":[],"bgos":[],"npcs":[]}
        for li, layer in enumerate(sec.layers):
            for t in layer.tiles:
                data["tiles"].append({"x":t.rect.x,"y":t.rect.y,"type":t.tile_type,"layer":li})
            for b in layer.bgos:
                data["bgos"].append({"x":b.rect.x,"y":b.rect.y,"type":b.bgo_type,"layer":li})
            for n in layer.npcs:
                data["npcs"].append({"x":n.rect.x,"y":n.rect.y,"type":n.npc_type,"layer":li})
        with open(fn,'w') as f: json.dump(data,f,indent=2)
        MessageBox(self.screen,"Export","Exported to:\n"+fn).run()

    def cmd_exit(self):
        r = MessageBox(self.screen,"Exit","Exit Mario Fan Builder?",("Yes","No")).run()
        if r == "Yes": pygame.quit(); sys.exit()

    def cmd_zoom_in(self):
        self.camera.zoom = min(ZOOM_MAX, round(self.camera.zoom+ZOOM_STEP, 2))
        self._img_cache.clear()
        self.status(f"Zoom: {int(self.camera.zoom*100)}%")

    def cmd_zoom_out(self):
        self.camera.zoom = max(ZOOM_MIN, round(self.camera.zoom-ZOOM_STEP, 2))
        self._img_cache.clear()
        self.camera._clamp()
        self.status(f"Zoom: {int(self.camera.zoom*100)}%")

    def cmd_zoom_reset(self):
        self.camera.zoom = 1.0
        self._img_cache.clear()
        self.camera._clamp()
        self.status("Zoom: 100%")

    def cmd_toggle_grid(self):
        self.grid_enabled = not self.grid_enabled
        # FIX B14: correct string precedence with parentheses
        self.status("Grid: " + ("ON" if self.grid_enabled else "OFF"))
        for _,_2,_3,dm in self.menubar.menus:
            for item in dm.items:
                if item.label == "Toggle Grid":
                    item.checked = self.grid_enabled
        for btn in self.toolbar_btns:
            if btn.icon_key == 'grid':
                btn.active = self.grid_enabled

    def cmd_set_theme(self, theme):
        global current_theme
        current_theme = theme
        self._img_cache.clear()
        sec = self.level.current_section()
        for layer in sec.layers:
            for t in layer.tiles: t.update_image()
            for b in layer.bgos:  b.update_image()
            for n in layer.npcs:  n.update_image()
        self.status(f"Theme: {theme}")

    def cmd_properties(self):
        name = InputDialog(self.screen,"Level Name","Enter level name:",self.level.name).run()
        if name is not None: self.level.name = name
        auth = InputDialog(self.screen,"Author","Enter author:",self.level.author).run()
        if auth is not None: self.level.author = auth

    def cmd_add_layer(self):
        sec = self.level.current_section()
        sec.layers.append(Layer(f"Layer {len(sec.layers)+1}"))
        self.status(f"Added layer {len(sec.layers)}")

    def cmd_layer_manager(self):
        sec = self.level.current_section()
        sec.current_layer_idx = (sec.current_layer_idx+1) % len(sec.layers)
        self.status(f"Active: {sec.current_layer().name}")

    def cmd_set_start(self):
        wx, wy = self.camera.screen_to_world(*self.mouse_pos)
        gx, gy = self._snap(wx, wy)
        self.level.start_pos = (gx, gy)
        if self.player: self.player.level_start = (gx, gy)
        self.status(f"Start pos: {gx//GRID_SIZE},{gy//GRID_SIZE}")

    def cmd_fill_bg(self):
        r = MessageBox(self.screen,"BG Color",
            "Choose background:\n1=Sky  2=Night  3=Black  4=Dusk  5=Cave  6=Ocean",
            ("1","2","3","4","5","6","Cancel")).run()
        if r and r != "Cancel":
            colors = [(92,148,252),(0,0,40),(0,0,0),(255,140,60),(30,20,10),(0,80,160)]
            idx = int(r)-1
            if 0 <= idx < len(colors):
                self.level.current_section().bg_color = colors[idx]

    def cmd_clear_all(self):
        r = MessageBox(self.screen,"Clear All","Clear ALL objects?\nCannot be undone!",
                       ("Yes","No")).run()
        if r == "Yes":
            for layer in self.level.current_section().layers:
                layer.tiles.empty(); layer.bgos.empty(); layer.npcs.empty()
                layer.tile_map.clear()
            self.undo_stack.clear(); self.redo_stack.clear(); self.selection.clear()
            self.status("Level cleared.")

    def cmd_reset_player(self):
        if self.player:
            self.player.rect.topleft = self.level.start_pos
            self.player.velocity.update(0,0)
            self.status("Player reset.")

    def cmd_help(self):
        MessageBox(self.screen,"Controls",
            "EDITOR:\n"
            "  Left Click / drag  - Place\n"
            "  Right Click / drag - Erase\n"
            "  Arrow Keys         - Scroll\n"
            "  Ctrl+Z/Y           - Undo/Redo\n"
            "  Ctrl+C/V/X         - Copy/Paste/Cut\n"
            "  Ctrl+A             - Select All\n"
            "  G                  - Toggle Grid\n"
            "  Ctrl +=/-          - Zoom In/Out\n"
            "  F5                 - Playtest\n\n"
            "PLAYTEST:\n"
            "  Arrows/WASD        - Move\n"
            "  Space              - Jump\n"
            "  Escape             - Back to editor").run()

    def cmd_about(self):
        MessageBox(self.screen,"About",
            "Mario Fan Builder\n"
            "CATSAN Engine  (C) AC Holding\n\n"
            "Extended SMBX 1.3 Edition\n"
            "Built with Python + Pygame").run()

    def cmd_event_editor(self):
        MessageBox(self.screen,"Event Editor","Event editing not yet implemented.").run()

    def cmd_warp_editor(self):
        MessageBox(self.screen,"Warp Editor","Warp editing not yet implemented.").run()

    def select_all(self):
        self.selection.clear()
        layer = self.level.current_layer()
        self.selection.extend(layer.tiles.sprites())
        self.selection.extend(layer.bgos.sprites())
        self.selection.extend(layer.npcs.sprites())
        self.status(f"Selected {len(self.selection)} objects")

    def deselect_all(self):
        self.selection.clear()

    def delete_selected(self):
        for obj in self.selection:
            self._delete_object(obj)
        self.selection.clear()
        self.status("Deleted selected objects")

    # ── TOOLS ─────────────────────────────────────────────────────────────────
    def set_tool_select(self): self.tool='select'; self.status("Tool: Select")
    def set_tool_pencil(self): self.tool='pencil'; self.status("Tool: Pencil")
    def set_tool_erase(self):  self.tool='erase';  self.status("Tool: Eraser")
    def set_tool_fill(self):   self.tool='fill';   self.status("Tool: Fill")
    def set_tool_event(self):  self.tool='event';  self.status("Tool: Event Picker")

    def toggle_playtest(self):
        self.menubar.open_idx = -1
        self.playtest_mode = not self.playtest_mode
        if self.playtest_mode:
            self.player = Player(*self.level.start_pos)
            self.player.level_start = self.level.start_pos
            self.camera.update(self.player)
            self.status("PLAYTEST — Esc to return")
        else:
            self.player = None
            self.status("Editor mode")
        for btn in self.toolbar_btns:
            if btn.icon_key == 'play': btn.active = self.playtest_mode

    def status(self, msg):
        self.status_msg = msg

    # ── UNDO / REDO ───────────────────────────────────────────────────────────
    def push_undo(self, action):
        self.undo_stack.append(action)
        self.redo_stack.clear()

    def undo(self):
        if not self.undo_stack: self.status("Nothing to undo"); return
        action = self.undo_stack.pop()
        action['undo']()
        self.redo_stack.append(action)
        self.status("Undo")

    def redo(self):
        if not self.redo_stack: self.status("Nothing to redo"); return
        action = self.redo_stack.pop()
        action['redo']()
        self.undo_stack.append(action)
        self.status("Redo")

    # ── COORD HELPERS ─────────────────────────────────────────────────────────
    def _snap(self, wx, wy):
        """Snap world coords to grid pixels."""
        return (int(wx)//GRID_SIZE)*GRID_SIZE, (int(wy)//GRID_SIZE)*GRID_SIZE

    def _mouse_grid(self):
        wx, wy = self.camera.screen_to_world(*self.mouse_pos)
        return self._snap(wx, wy)

    # ── OBJECT PLACEMENT (FIX B03) ────────────────────────────────────────────
    def place_object(self, gx, gy):
        sec   = self.level.current_section()
        layer = sec.current_layer()
        if layer.locked: return
        # FIX B03: always resolve the layer index as an integer
        li  = sec.current_layer_idx
        cat = self.sidebar.current_category
        key = (gx, gy)

        if cat == "NPCs":
            npc = NPC(gx, gy, self.sidebar.selected_item, layer_idx=li)
            layer.npcs.add(npc)
            self.push_undo({'undo': lambda l=layer, n=npc: l.npcs.discard(n),
                            'redo': lambda l=layer, n=npc: l.npcs.add(n)})
        elif cat == "BGOs":
            bgo = BGO(gx, gy, self.sidebar.selected_item, layer_idx=li)
            layer.bgos.add(bgo)
            self.push_undo({'undo': lambda l=layer, b=bgo: l.bgos.discard(b),
                            'redo': lambda l=layer, b=bgo: l.bgos.add(b)})
        else:
            if key in layer.tile_map: return
            tile = Tile(gx, gy, self.sidebar.selected_item, layer_idx=li)
            layer.add_tile(tile)
            self.push_undo({'undo': lambda l=layer, t=tile: l.remove_tile(t),
                            'redo': lambda l=layer, t=tile: l.add_tile(t)})

    def erase_object(self, gx, gy):
        sec   = self.level.current_section()
        layer = sec.current_layer()
        if layer.locked: return
        key = (gx, gy)
        if key in layer.tile_map:
            tile = layer.tile_map[key]
            layer.remove_tile(tile)
            self.push_undo({'undo': lambda l=layer, t=tile: l.add_tile(t),
                            'redo': lambda l=layer, t=tile: l.remove_tile(t)})
            return
        for group in (layer.npcs, layer.bgos):
            for obj in list(group):
                if obj.rect.x == gx and obj.rect.y == gy:
                    group.discard(obj)
                    self.push_undo({'undo': lambda g=group, o=obj: g.add(o),
                                    'redo': lambda g=group, o=obj: g.discard(o)})
                    return

    def fill_area(self, sx, sy):
        """FIX B05: BFS fill capped at MAX_FILL tiles to prevent hang on large empty areas."""
        MAX_FILL = 4000
        layer = self.level.current_layer()
        if layer.locked: return
        target   = self.sidebar.selected_item
        start    = (sx, sy)
        old_type = layer.tile_map[start].tile_type if start in layer.tile_map else None
        if old_type == target: return
        sec      = self.level.current_section()
        queue    = deque([start])
        visited  = set([start])
        new_tiles= []
        while queue and len(new_tiles) < MAX_FILL:
            x, y = queue.popleft()
            if old_type is None:
                if (x,y) in layer.tile_map: continue
            else:
                if (x,y) not in layer.tile_map: continue
                if layer.tile_map[(x,y)].tile_type != old_type: continue
                layer.remove_tile(layer.tile_map[(x,y)])
            t = Tile(x, y, target, layer_idx=sec.current_layer_idx)
            layer.add_tile(t)
            new_tiles.append(t)
            for dx, dy in ((GRID_SIZE,0),(-GRID_SIZE,0),(0,GRID_SIZE),(0,-GRID_SIZE)):
                nx, ny = x+dx, y+dy
                if (nx,ny) not in visited and 0 <= nx < sec.width and 0 <= ny < sec.height:
                    visited.add((nx,ny))
                    queue.append((nx,ny))
        if new_tiles:
            self.push_undo({'undo': lambda l=layer, nt=list(new_tiles): [l.remove_tile(t) for t in nt],
                            'redo': lambda l=layer, nt=list(new_tiles): [l.add_tile(t) for t in nt]})

    def handle_select(self, gx, gy, event):
        layer = self.level.current_layer()
        obj   = layer.tile_map.get((gx, gy))
        if not obj:
            for n in layer.npcs:
                if n.rect.x == gx and n.rect.y == gy: obj = n; break
        if not obj:
            for b in layer.bgos:
                if b.rect.x == gx and b.rect.y == gy: obj = b; break
        if obj:
            if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                if obj in self.selection: self.selection.remove(obj)
                else:                     self.selection.append(obj)
            else:
                self.selection = [obj]

    def handle_event_pick(self, gx, gy):
        layer = self.level.current_layer()
        obj   = layer.tile_map.get((gx, gy))
        if not obj:
            for n in layer.npcs:
                if n.rect.x==gx and n.rect.y==gy: obj=n; break
        if obj:
            r = InputDialog(self.screen,"Assign Event","Event ID (-1=none):",
                            str(obj.event_id)).run()
            if r is not None:
                try: obj.event_id = int(r)
                except ValueError: pass

    def copy_selection(self):
        self.clipboard = [(o.rect.x, o.rect.y, o.obj_type, o.layer_index)
                          for o in self.selection]
        self.status(f"Copied {len(self.clipboard)} object(s)")

    def cut_selection(self):
        self.copy_selection()
        for o in self.selection: self._delete_object(o)
        self.selection.clear()

    def paste_clipboard(self):
        if not self.clipboard: return
        wx, wy = self.camera.screen_to_world(*self.mouse_pos)
        bx, by = self._snap(wx, wy)
        ox, oy = self.clipboard[0][0], self.clipboard[0][1]
        sec    = self.level.current_section()
        pasted = []
        for x, y, otype, li in self.clipboard:
            nx, ny = bx+(x-ox), by+(y-oy)
            if li >= len(sec.layers): continue
            layer = sec.layers[li]
            if otype in TILE_SMBX_IDS:
                t = Tile(nx, ny, otype, layer_idx=li)
                layer.add_tile(t); pasted.append(('tile', layer, t))
            elif otype in BGO_SMBX_IDS:
                b = BGO(nx, ny, otype, layer_idx=li)
                layer.bgos.add(b); pasted.append(('bgo', layer, b))
            elif otype in NPC_SMBX_IDS:
                n = NPC(nx, ny, otype, layer_idx=li)
                layer.npcs.add(n); pasted.append(('npc', layer, n))
        # FIX B19: paste now has an undo entry
        def _undo_paste(items=pasted):
            for kind, lyr, obj in items:
                if kind=='tile': lyr.remove_tile(obj)
                elif kind=='bgo': lyr.bgos.discard(obj)
                elif kind=='npc': lyr.npcs.discard(obj)
        def _redo_paste(items=pasted):
            for kind, lyr, obj in items:
                if kind=='tile': lyr.add_tile(obj)
                elif kind=='bgo': lyr.bgos.add(obj)
                elif kind=='npc': lyr.npcs.add(obj)
        self.push_undo({'undo': _undo_paste, 'redo': _redo_paste})
        self.status(f"Pasted {len(self.clipboard)} object(s)")

    def _delete_object(self, obj):
        sec   = self.level.current_section()
        # FIX B03: layer_index is now guaranteed int
        li    = obj.layer_index
        if li >= len(sec.layers): return
        layer = sec.layers[li]
        if isinstance(obj, Tile):  layer.remove_tile(obj)
        elif isinstance(obj, BGO): layer.bgos.discard(obj)
        elif isinstance(obj, NPC): layer.npcs.discard(obj)

    # ── EVENT HANDLING ────────────────────────────────────────────────────────
    def handle_event(self, event):
        if event.type == pygame.QUIT:
            return False
        if self.menubar.handle_event(event):
            return True
        for btn in self.toolbar_btns:
            btn.handle_event(event)

        if event.type == pygame.MOUSEMOTION:
            self.mouse_pos  = event.pos
            self.tooltip_text = ""
            for btn in self.toolbar_btns:
                if btn.rect.collidepoint(event.pos):
                    self.tooltip_text = btn.tooltip

        if event.type == pygame.KEYDOWN:
            mods = pygame.key.get_mods()
            ctrl = bool(mods & pygame.KMOD_CTRL)
            if event.key == pygame.K_ESCAPE:
                if self.playtest_mode: self.toggle_playtest()
                elif self.menubar.open_idx >= 0: self.menubar.open_idx = -1
                else: self.deselect_all()
            if not self.playtest_mode and not ctrl:
                kt = {pygame.K_s:self.set_tool_select, pygame.K_p:self.set_tool_pencil,
                      pygame.K_e:self.set_tool_erase,  pygame.K_f:self.set_tool_fill,
                      pygame.K_t:self.set_tool_event,  pygame.K_g:self.cmd_toggle_grid,
                      pygame.K_F4:self.cmd_properties, pygame.K_F5:self.toggle_playtest,
                      pygame.K_F6:self.cmd_event_editor, pygame.K_F7:self.cmd_warp_editor,
                      pygame.K_F1:self.cmd_help, pygame.K_DELETE:self.delete_selected}
                if event.key in kt: kt[event.key]()
                # FIX B31: scroll camera by GRID_SIZE world pixels directly
                scroll = {pygame.K_LEFT:(GRID_SIZE//2,0), pygame.K_RIGHT:(-GRID_SIZE//2,0),
                          pygame.K_UP:(0,GRID_SIZE//2), pygame.K_DOWN:(0,-GRID_SIZE//2)}
                if event.key in scroll: self.camera.move(*scroll[event.key])
            if ctrl:
                ck = {pygame.K_n:self.cmd_new, pygame.K_o:self.cmd_open,
                      pygame.K_s:self.cmd_save, pygame.K_z:self.undo,
                      pygame.K_y:self.redo, pygame.K_c:self.copy_selection,
                      pygame.K_v:self.paste_clipboard, pygame.K_x:self.cut_selection,
                      pygame.K_a:self.select_all, pygame.K_EQUALS:self.cmd_zoom_in,
                      pygame.K_PLUS:self.cmd_zoom_in, pygame.K_MINUS:self.cmd_zoom_out,
                      pygame.K_0:self.cmd_zoom_reset}
                if event.key in ck: ck[event.key]()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.sidebar.rect.collidepoint(event.pos) and event.button == 1:
                self.sidebar.handle_click(event.pos, self.level)
            elif (event.pos[1] > CANVAS_Y and event.pos[0] > SIDEBAR_WIDTH
                  and not self.playtest_mode and self.menubar.open_idx < 0):
                gx, gy = self._mouse_grid()
                if event.button == 1:
                    if   self.tool == 'pencil': self.drag_draw  = True; self.place_object(gx, gy)
                    elif self.tool == 'erase':  self.drag_erase = True; self.erase_object(gx, gy)
                    elif self.tool == 'select': self.handle_select(gx, gy, event)
                    elif self.tool == 'fill':   self.fill_area(gx, gy)
                    elif self.tool == 'event':  self.handle_event_pick(gx, gy)
                elif event.button == 3:
                    self.drag_erase = True; self.erase_object(gx, gy)
                elif event.button == 4: self.cmd_zoom_in()
                elif event.button == 5: self.cmd_zoom_out()
            if self.sidebar.rect.collidepoint(event.pos) and event.button in (4,5):
                self.sidebar.handle_scroll(1 if event.button==4 else -1)

        if event.type == pygame.MOUSEMOTION and not self.playtest_mode:
            if self.drag_draw or self.drag_erase:
                gx, gy = self._mouse_grid()
                if self.drag_draw:  self.place_object(gx, gy)
                elif self.drag_erase: self.erase_object(gx, gy)

        if event.type == pygame.MOUSEBUTTONUP and event.button in (1, 3):
            self.drag_draw = False; self.drag_erase = False

        return True

    # ── UPDATE ────────────────────────────────────────────────────────────────
    def update(self):
        if not (self.playtest_mode and self.player):
            return
        sec = self.level.current_section()
        # FIX B29: collect solid tiles once per frame, not inside NPC update loops
        solid = sec.get_solid_tiles()
        # expose layers to Player coin logic
        global _current_section_layers
        _current_section_layers = sec.layers

        npc_group = pygame.sprite.Group()
        for layer in sec.layers:
            if layer.visible:
                npc_group.add(layer.npcs.sprites())

        self.player.update(solid, npc_group, sec.events)
        for npc in list(npc_group):
            npc.update(solid, self.player, sec.events)
        self.camera.update(self.player)

    # ── DRAW ──────────────────────────────────────────────────────────────────
    def draw(self, surf):
        surf.fill(SYS_BTN_FACE)

        # Toolbar background
        pygame.draw.rect(surf, SYS_BTN_FACE, (0,MENU_HEIGHT,WINDOW_WIDTH,TOOLBAR_HEIGHT))
        pygame.draw.line(surf, SYS_BTN_DARK,
                         (0,MENU_HEIGHT+TOOLBAR_HEIGHT-1),(WINDOW_WIDTH,MENU_HEIGHT+TOOLBAR_HEIGHT-1))
        for btn in self.toolbar_btns: btn.draw(surf)

        # Sidebar
        self.sidebar.draw(surf, self.level)

        # ── Canvas ───────────────────────────────────────────────────────────
        canvas_rect = pygame.Rect(SIDEBAR_WIDTH, CANVAS_Y, CANVAS_WIDTH, CANVAS_HEIGHT)
        surf.set_clip(canvas_rect)
        surf.fill(self.level.current_section().bg_color)

        zoom = self.camera.zoom
        sec  = self.level.current_section()
        cam  = self.camera

        # FIX B10: grid scaled by zoom
        if self.grid_enabled:
            gs_screen = GRID_SIZE * zoom
            if gs_screen >= 4:   # skip grid when zoomed out too far
                first_wx = (-cam.camera.x // GRID_SIZE) * GRID_SIZE
                first_wy = (-cam.camera.y // GRID_SIZE) * GRID_SIZE
                # vertical lines
                wx = first_wx
                while True:
                    px = int((wx + cam.camera.x) * zoom) + SIDEBAR_WIDTH
                    if px > canvas_rect.right: break
                    if px >= canvas_rect.left:
                        pygame.draw.line(surf, SMBX_GRID,(px,canvas_rect.top),(px,canvas_rect.bottom))
                    wx += GRID_SIZE
                # horizontal lines
                wy = first_wy
                while True:
                    py = int((wy + cam.camera.y) * zoom) + CANVAS_Y
                    if py > canvas_rect.bottom: break
                    if py >= canvas_rect.top:
                        pygame.draw.line(surf, SMBX_GRID,(canvas_rect.left,py),(canvas_rect.right,py))
                    wy += GRID_SIZE

        # FIX B06/B07: apply zoom when rendering sprites
        scaled_gs = max(1, int(GRID_SIZE * zoom))
        for layer in sec.layers:
            if not layer.visible: continue
            for bgo in layer.bgos:
                sx, sy = cam.world_to_screen(bgo.rect.x, bgo.rect.y)
                surf.blit(self._scaled(bgo.image), (sx, sy))
            for tile in layer.tiles:
                sx, sy = cam.world_to_screen(tile.rect.x, tile.rect.y)
                surf.blit(self._scaled(tile.image), (sx, sy))
            for npc in layer.npcs:
                sx, sy = cam.world_to_screen(npc.rect.x, npc.rect.y)
                surf.blit(self._scaled(npc.image), (sx, sy))

        # FIX B11: selection highlights scaled
        if not self.playtest_mode:
            for obj in self.selection:
                sx, sy = cam.world_to_screen(obj.rect.x, obj.rect.y)
                r = pygame.Rect(sx, sy, scaled_gs, scaled_gs)
                pygame.draw.rect(surf, YELLOW, r, 2)
                pygame.draw.rect(surf, WHITE, r.inflate(2,2), 1)

        # FIX B12: start marker scaled
        if not self.playtest_mode:
            spx, spy = cam.world_to_screen(*self.level.start_pos)
            sp = pygame.Rect(spx, spy, scaled_gs, scaled_gs)
            pygame.draw.rect(surf, GREEN, sp, 2)
            draw_text(surf, "S", (spx+2, spy+2), GREEN, FONT_SMALL)

        # FIX B13: player rendered at correct zoomed position
        if self.playtest_mode and self.player:
            px, py = cam.world_to_screen(self.player.rect.x, self.player.rect.y)
            pimg   = self._scaled(self.player.image)
            self.player.draw(surf, px, py)

        surf.set_clip(None)
        draw_edge(surf, canvas_rect, raised=False)

        # Status bar
        sb_y = WINDOW_HEIGHT - STATUSBAR_HEIGHT
        pygame.draw.rect(surf, SYS_BTN_FACE, (0,sb_y,WINDOW_WIDTH,STATUSBAR_HEIGHT))
        pygame.draw.line(surf, SYS_BTN_LIGHT, (0,sb_y),(WINDOW_WIDTH,sb_y))

        def panel(px, pw, text):
            pr = pygame.Rect(px, sb_y+2, pw, STATUSBAR_HEIGHT-4)
            pygame.draw.rect(surf, SYS_BTN_FACE, pr)
            draw_edge(surf, pr, raised=False)
            draw_text(surf, text, (pr.x+4, pr.y+3), SYS_TEXT, FONT_SMALL)

        mode = "PLAYTEST" if self.playtest_mode else self.tool.upper()
        panel(2,   120, f"Mode: {mode}")
        panel(126, 160, f"Layer: {self.level.current_layer().name}")
        gx, gy = self._mouse_grid()
        panel(290, 140, f"X:{gx//GRID_SIZE} Y:{gy//GRID_SIZE}")
        panel(434, 100, f"Zoom: {int(zoom*100)}%")
        if self.playtest_mode and self.player:
            panel(538, 200, f"Coins:{self.player.coins}  Score:{self.player.score}")
        elif self.status_msg:
            panel(538, WINDOW_WIDTH-542, self.status_msg)

        # FIX B24: tooltip clipped to screen, not raw mouse pos
        if self.tooltip_text:
            tx, ty = self.mouse_pos
            ty = max(CANVAS_Y, ty-20)
            tx = min(tx, WINDOW_WIDTH - FONT_SMALL.size(self.tooltip_text)[0] - 14)
            tw = FONT_SMALL.size(self.tooltip_text)[0] + 10
            tr = pygame.Rect(tx, ty, tw, 17)
            pygame.draw.rect(surf, (255,255,220), tr)
            draw_edge(surf, tr, raised=True)
            draw_text(surf, self.tooltip_text, (tr.x+5, tr.y+3), BLACK, FONT_SMALL)

        # Menu drawn last (on top)
        self.menubar.draw(surf)

# ── MAIN MENU ─────────────────────────────────────────────────────────────────
def main_menu(screen):
    clock  = pygame.time.Clock()
    btns   = [pygame.Rect(WINDOW_WIDTH//2-100, 300+i*42, 200, 34) for i in range(3)]
    labels = ["New Level","Open Level","Quit"]
    hovered= -1
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "QUIT"
            if event.type == pygame.MOUSEMOTION:
                hovered = next((i for i,r in enumerate(btns) if r.collidepoint(event.pos)), -1)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i,r in enumerate(btns):
                    if r.collidepoint(event.pos):
                        return ["NEW","LOAD","QUIT"][i]
        screen.fill(SYS_BTN_FACE)
        wr = pygame.Rect(WINDOW_WIDTH//2-220, 80, 440, 390)
        pygame.draw.rect(screen, SYS_BTN_FACE, wr)
        draw_edge(screen, wr, raised=True)
        tr = pygame.Rect(wr.x, wr.y, wr.w, 22)
        pygame.draw.rect(screen, SYS_HIGHLIGHT, tr)
        draw_text(screen,"Mario Fan Builder — Extended SMBX 1.3 Edition",
                  (tr.x+4, tr.y+4), WHITE, FONT_SMALL)
        cr = pygame.Rect(wr.x+6, tr.bottom+6, wr.w-12, wr.h-tr.h-12)
        pygame.draw.rect(screen, SYS_WINDOW, cr)
        draw_edge(screen, cr, raised=False)
        draw_text(screen,"Mario Fan Builder",(cr.centerx,cr.y+44),SYS_HIGHLIGHT,FONT_TITLE,True)
        draw_text(screen,"SMBX 1.3 Style Level Editor",(cr.centerx,cr.y+72),SYS_TEXT,FONT,True)
        draw_text(screen,"CATSAN Engine  (C) AC Holding",(cr.centerx,cr.y+94),GRAY,FONT_SMALL,True)
        for i,(r,lbl) in enumerate(zip(btns,labels)):
            sel = (i==hovered)
            pygame.draw.rect(screen, SYS_HIGHLIGHT if sel else SYS_BTN_FACE, r)
            draw_edge(screen, r, raised=not sel)
            draw_text(screen, lbl, r.center, WHITE if sel else SYS_TEXT, FONT, True)
        pygame.display.flip()
        clock.tick(60)

# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    # FIX B01: initialise pygame first, then create fonts
    pygame.init()
    pygame.display.set_caption("Mario Fan Builder — Extended SMBX 1.3 Edition")
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

    # FIX B01: assign all global FONT objects NOW, after pygame.init()
    global FONT, FONT_SMALL, FONT_MENU, FONT_TITLE
    FONT       = pygame.font.SysFont("segoeui",    14)
    FONT_SMALL = pygame.font.SysFont("segoeui",    12)
    FONT_MENU  = pygame.font.SysFont("segoeui",    13)
    FONT_TITLE = pygame.font.SysFont("segoeui",    22, bold=True)

    # Generate all pixel-art assets (pygame-native, no Pillow needed)
    generate_assets_pygame()

    # FIX B02: load graphics AFTER pygame.init() so pygame.image.load works
    load_smbx_graphics()

    clock = pygame.time.Clock()

    while True:
        result = main_menu(screen)
        if result == "QUIT":
            pygame.quit(); sys.exit()
        level = Level()
        if result == "LOAD":
            fn = InputDialog(screen,"Open Level","Enter filename:","level.lvl").run()
            if fn and os.path.exists(fn):
                level = read_lvl(fn)
        editor  = Editor(level, screen)
        running = True
        while running:
            for event in pygame.event.get():
                if not editor.handle_event(event):
                    pygame.quit(); sys.exit()
            editor.update()
            editor.draw(screen)
            pygame.display.flip()
            clock.tick(FPS)


if __name__ == "__main__":
    main()
