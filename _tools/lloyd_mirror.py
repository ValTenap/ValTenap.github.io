"""Lloyd mirror interferometer, built and rendered headless with Blender's Python module.

    pip install bpy        (Blender as a Python module)
    python _tools/lloyd_mirror.py [out.png] [width] [samples]

A mirror and a holographic film stand at 90 degrees on a rotation stage. An expanded
HeNe beam comes in at angle ALPHA: half of it hits the film directly, half bounces
off the mirror first, and the two halves interfere in the film, writing fringes of
period  Lambda = lambda / (2 sin alpha).
"""
import math
import sys

import bpy
import bmesh
from mathutils import Vector

OUT = sys.argv[1] if len(sys.argv) > 1 else "lloyd_mirror.png"
W = int(sys.argv[2]) if len(sys.argv) > 2 else 1600
SAMPLES = int(sys.argv[3]) if len(sys.argv) > 3 else 64
ALPHA = math.radians(28)       # beam angle to the mirror plane
BEAM_W, BEAM_H = 2.2, 1.1       # expanded beam cross-section (scene units ~ cm)
MIRROR_L, FILM_L, H = 4.2, 2.6, 1.6

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene


# ---------- materials ----------------------------------------------------------------
def mat(name, color=(0.8, 0.8, 0.8), metal=0.0, rough=0.4, transmission=0.0, alpha=1.0,
        emission=None, strength=0.0, ior=1.45):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*color, 1)
    p.inputs["Metallic"].default_value = metal
    p.inputs["Roughness"].default_value = rough
    p.inputs["Transmission Weight"].default_value = transmission
    p.inputs["Alpha"].default_value = alpha
    p.inputs["IOR"].default_value = ior
    if emission:
        p.inputs["Emission Color"].default_value = (*emission, 1)
        p.inputs["Emission Strength"].default_value = strength
    return m


def beam_material(name, strength, alpha):
    """Glowing, see-through red sheet of light (cheap stand-in for a scattering volume)."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    mix = nt.nodes.new("ShaderNodeMixShader")
    em = nt.nodes.new("ShaderNodeEmission")
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    em.inputs["Color"].default_value = (1.0, 0.06, 0.03, 1)
    em.inputs["Strength"].default_value = strength
    mix.inputs["Fac"].default_value = alpha
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(em.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs[0])
    return m


def film_material():
    """Pinkish photopolymer with glowing red interference fringes where both beams overlap."""
    m = bpy.data.materials.new("film")
    m.use_nodes = True
    nt = m.node_tree
    p = nt.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (0.95, 0.55, 0.6, 1)
    p.inputs["Transmission Weight"].default_value = 0.85
    p.inputs["Roughness"].default_value = 0.15
    p.inputs["Alpha"].default_value = 0.85
    coord = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    math_n = nt.nodes.new("ShaderNodeMath"); math_n.operation = "MULTIPLY"
    math_n.inputs[1].default_value = 34.0
    sine = nt.nodes.new("ShaderNodeMath"); sine.operation = "SINE"
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.35
    ramp.color_ramp.elements[0].color = (0, 0, 0, 1)
    ramp.color_ramp.elements[1].position = 1.0
    ramp.color_ramp.elements[1].color = (1.0, 0.08, 0.04, 1)
    norm = nt.nodes.new("ShaderNodeMapRange")
    norm.inputs["From Min"].default_value = -1; norm.inputs["From Max"].default_value = 1
    nt.links.new(coord.outputs["Object"], sep.inputs[0])
    nt.links.new(sep.outputs["Y"], math_n.inputs[0])       # fringes vary across the film
    nt.links.new(math_n.outputs[0], sine.inputs[0])
    nt.links.new(sine.outputs[0], norm.inputs["Value"])
    nt.links.new(norm.outputs["Result"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], p.inputs["Emission Color"])
    p.inputs["Emission Strength"].default_value = 6.0
    return m


def breadboard_material():
    """Black anodized optical table with an M6 hole grid on a 2.5 cm pitch."""
    m = bpy.data.materials.new("breadboard")
    m.use_nodes = True
    nt = m.node_tree
    p = nt.nodes["Principled BSDF"]
    p.inputs["Roughness"].default_value = 0.55
    p.inputs["Metallic"].default_value = 0.6
    coord = nt.nodes.new("ShaderNodeTexCoord")
    mapn = nt.nodes.new("ShaderNodeMapping")
    mapn.inputs["Scale"].default_value = (1 / 1.25, 1 / 1.25, 1)
    vor = nt.nodes.new("ShaderNodeTexVoronoi")
    vor.feature = "F1"; vor.inputs["Randomness"].default_value = 0.0; vor.inputs["Scale"].default_value = 1
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.16
    ramp.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1)
    ramp.color_ramp.elements[1].position = 0.18
    ramp.color_ramp.elements[1].color = (0.045, 0.047, 0.055, 1)
    nt.links.new(coord.outputs["Object"], mapn.inputs[0])
    nt.links.new(mapn.outputs[0], vor.inputs["Vector"])
    nt.links.new(vor.outputs["Distance"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], p.inputs["Base Color"])
    return m


ALU = mat("aluminum", (0.72, 0.73, 0.76), metal=1.0, rough=0.28)
BLACK = mat("anodized", (0.02, 0.02, 0.025), metal=0.5, rough=0.35)
MIRROR = mat("mirror", (0.97, 0.97, 0.98), metal=1.0, rough=0.02)
GLASS = mat("glass", (1, 1, 1), transmission=1.0, rough=0.0, ior=1.5)
BRASS = mat("engraving", (0.9, 0.9, 0.92), metal=1.0, rough=0.2)


# ---------- helpers --------------------------------------------------------------------
def add(obj, m):
    obj.data.materials.append(m)
    for poly in obj.data.polygons:
        poly.use_smooth = True
    return obj


def box(name, size, loc, m, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object; o.name = name; o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    bev = o.modifiers.new("bevel", "BEVEL"); bev.width = 0.02; bev.segments = 3
    o.data.materials.append(m)
    return o


def cyl(name, r, depth, loc, m, rot=(0, 0, 0), verts=96):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=depth, location=loc, rotation=rot, vertices=verts)
    o = bpy.context.object; o.name = name
    bev = o.modifiers.new("bevel", "BEVEL"); bev.width = 0.015; bev.segments = 3
    bpy.ops.object.shade_smooth()
    o.data.materials.append(m)
    return o


def prism(name, poly2d, z0, z1, m):
    """Extrude a 2-D polygon (x, y) between heights z0 and z1."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bot = [bm.verts.new((x, y, z0)) for x, y in poly2d]
    top = [bm.verts.new((x, y, z1)) for x, y in poly2d]
    bm.faces.new(bot[::-1]); bm.faces.new(top)
    n = len(poly2d)
    for i in range(n):
        bm.faces.new([bot[i], bot[(i + 1) % n], top[(i + 1) % n], top[i]])
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); scene.collection.objects.link(o)
    o.data.materials.append(m)
    return o


# ---------- optical table and rotation stage -------------------------------------------
bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, -1.05))
add(bpy.context.object, breadboard_material())

stage_base = cyl("stage_base", 3.6, 0.5, (0, 0, -0.8), BLACK)
stage_top = cyl("stage_top", 3.3, 0.35, (0, 0, -0.38), ALU)
# engraved degree ticks around the rotating platform
for k in range(72):
    a = math.radians(k * 5)
    long = k % 6 == 0
    L = 0.32 if long else 0.16
    r = 3.3 - L / 2 - 0.02
    box("tick", (L, 0.025, 0.02), (r * math.cos(a), r * math.sin(a), -0.2), BRASS, rot=(0, 0, a))
# locking thumbscrew
cyl("screw", 0.12, 0.7, (0, -3.85, -0.75), ALU, rot=(math.radians(90), 0, 0), verts=32)

# ---------- mirror (along +x) and film holder (along +y), corner at the origin ----------
box("mirror_back", (MIRROR_L + 0.3, 0.25, H + 0.3), (MIRROR_L / 2, -0.16, H / 2 - 0.05), BLACK)
box("mirror", (MIRROR_L, 0.06, H), (MIRROR_L / 2, -0.01, H / 2 + 0.1), MIRROR)
box("film_frame", (0.25, FILM_L + 0.3, H + 0.3), (-0.16, FILM_L / 2, H / 2 - 0.05), BLACK)
glass = box("film_glass", (0.08, FILM_L, H), (-0.0, FILM_L / 2, H / 2 + 0.1), GLASS)
film = box("film", (0.02, FILM_L * 0.92, H * 0.85), (0.05, FILM_L / 2, H / 2 + 0.1), film_material())
for o in (glass, film):
    o.modifiers["bevel"].width = 0.005

# ---------- the beam --------------------------------------------------------------------
# Incoming direction d (towards -x, slightly towards -y). n is the in-plane normal.
d = Vector((-math.cos(ALPHA), -math.sin(ALPHA)))
n = Vector((math.sin(ALPHA), -math.cos(ALPHA)))
z0, z1 = 0.1 + (H - BEAM_H) / 2, 0.1 + (H + BEAM_H) / 2
# The beam is centred on the ray that hits the corner, so its lower half hits the mirror.
FAR = 8.6                       # the expanded beam starts at the big lens
centre_far = -d * FAR
edge_hi = centre_far - n * (BEAM_W / 2)      # ray that lands high on the film
edge_lo = centre_far + n * (BEAM_W / 2)      # ray that lands far out on the mirror


def hit_x0(p):      # where a ray from p along d crosses x = 0
    t = -p.x / d.x
    return p + d * t


def hit_y0(p):      # where a ray from p along d crosses y = 0
    t = -p.y / d.y
    return p + d * t


film_top = hit_x0(edge_hi)                   # direct half: lands on the film at y > 0
mirror_far = hit_y0(edge_lo)                 # reflected half: lands on the mirror
d_ref = Vector((d.x, -d.y))
film_ref_top = mirror_far + d_ref * (-mirror_far.x / d_ref.x)

direct = [tuple(edge_hi), tuple(centre_far), (0.0, 0.0), tuple(film_top)]
incoming_lo = [tuple(centre_far), tuple(edge_lo), tuple(mirror_far), (0.0, 0.0)]
reflected = [(0.0, 0.0), tuple(mirror_far), tuple(film_ref_top)]

prism("beam_direct", direct, z0, z1, beam_material("beam_a", 1.2, 0.09))
prism("beam_to_mirror", incoming_lo, z0, z1, beam_material("beam_b", 1.2, 0.09))
prism("beam_reflected", reflected, z0, z1, beam_material("beam_c", 1.8, 0.13))

# Beam expander (small diverging lens + big collimating lens) and the HeNe head upstream.
u = -d                                           # unit vector pointing back towards the laser
axis_ang = math.atan2(u.y, u.x)
zc = 0.1 + H / 2
ROT = (0, math.radians(90), axis_ang)            # puts a cylinder's axis along the beam


def along(dist):
    return u * dist


def post_under(c, r):
    cyl("post", 0.18, zc - r + 1.05, (c.x, c.y, (zc - r - 1.05) / 2), ALU, verts=32)
    box("post_base", (0.9, 0.9, 0.12), (c.x, c.y, -0.99), BLACK)


big_r, small_r, small_d, laser_d = 1.35, 0.32, 11.2, 13.0
for dist, r in ((FAR, big_r), (small_d, small_r)):
    c = along(dist)
    cyl("lens", r, 0.1 if r > 1 else 0.06, (c.x, c.y, zc), GLASS, rot=ROT, verts=64)
    bpy.ops.mesh.primitive_torus_add(major_radius=r + 0.05, minor_radius=0.07,
                                     location=(c.x, c.y, zc), rotation=ROT)
    t = bpy.context.object; bpy.ops.object.shade_smooth(); t.data.materials.append(BLACK)
    post_under(c, r + 0.1)

# diverging cone between the lenses and a thin beam from the laser
mid = along((FAR + small_d) / 2)
bpy.ops.mesh.primitive_cone_add(radius1=min(BEAM_W, BEAM_H) * 0.55, radius2=0.05,
                                depth=small_d - FAR, vertices=64,
                                location=(mid.x, mid.y, zc), rotation=ROT)
bpy.context.object.data.materials.append(beam_material("cone", 1.4, 0.12))
mid = along((small_d + laser_d) / 2)
cyl("beam_thin", 0.05, laser_d - small_d, (mid.x, mid.y, zc), beam_material("thin", 6, 0.6), rot=ROT, verts=24)
c = along(laser_d + 2.5)
cyl("hene_head", 0.55, 5.0, (c.x, c.y, zc), mat("hene", (0.75, 0.05, 0.04), metal=0.3, rough=0.3), rot=ROT)
c = along(laser_d)
cyl("hene_aperture", 0.2, 0.08, (c.x, c.y, zc), BLACK, rot=ROT, verts=32)

# ---------- lighting, camera, render ----------------------------------------------------
world = bpy.data.worlds.new("world"); scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.012, 0.014, 0.022, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 1.0

for loc, energy, size, col in (((6, -6, 9), 1400, 6, (0.85, 0.9, 1.0)),
                               ((-8, 5, 6), 500, 5, (0.6, 0.7, 1.0)),
                               ((2, 8, 3), 160, 3, (1.0, 0.75, 0.7))):
    bpy.ops.object.light_add(type="AREA", location=loc)
    L = bpy.context.object; L.data.energy = energy; L.data.size = size; L.data.color = col
    L.rotation_euler = (Vector((1.5, 1.0, 0.3)) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()

CAM_AZ, CAM_DIST, CAM_H = math.radians(72), 15.5, 7.4
cam_loc = Vector((CAM_DIST * math.cos(CAM_AZ), CAM_DIST * math.sin(CAM_AZ), CAM_H))
bpy.ops.object.camera_add(location=cam_loc)
cam = bpy.context.object; scene.camera = cam
cam.data.lens = 29
cam.data.dof.use_dof = True
cam.data.dof.focus_distance = (cam_loc - Vector((1.0, 1.0, 0.8))).length
cam.data.dof.aperture_fstop = 4.0
target = Vector((5.2, 3.4, 0.0))
cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()

scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = SAMPLES
scene.cycles.use_denoising = True
scene.cycles.max_bounces = 8
scene.cycles.transparent_max_bounces = 16
scene.render.resolution_x = W
scene.render.resolution_y = int(W * 0.62)
scene.render.film_transparent = False
scene.view_settings.view_transform = "AgX"
scene.view_settings.look = "AgX - Medium High Contrast"
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = OUT
bpy.ops.wm.save_as_mainfile(filepath=OUT.rsplit(".", 1)[0] + ".blend")
bpy.ops.render.render(write_still=True)
print("rendered", OUT)
