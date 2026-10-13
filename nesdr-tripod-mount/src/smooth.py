import numpy as np, struct, sys
from skimage.measure import marching_cubes
variant = sys.argv[1]  # selftap | nut | insert
S = 0.3  # grid step (mm)
# --- parameters (mm), same as the boxy version ---
sw, st, clr = 16.9, 14.2, 0.4
W, T = sw+2*clr, st+2*clr
wall, H, off, lip = 2.4, 50.0, 45.0, 2.4
ow, ot = 13.4, 11.0
foot, fh = 30.0, 14.0
OW, OT = W+2*wall, T+2*wall
x = np.arange(-18, 60, S); y = np.arange(-18, 18, S); z = np.arange(-1.5, 53, S)
X, Y, Z = np.meshgrid(x, y, z, indexing='ij')
def rrect2(px, py, cx, cy, hx, hy, r):
    qx = np.abs(px-cx)-(hx-r); qy = np.abs(py-cy)-(hy-r)
    return np.hypot(np.maximum(qx,0), np.maximum(qy,0)) + np.minimum(np.maximum(qx,qy),0) - r
def prism(cx, cy, hx, hy, z0, z1, rv, rt):
    # rounded rectangle (vertical corner radius rv) extruded z0..z1 with rounded top/bottom edges rt
    d2 = rrect2(X, Y, cx, cy, hx, hy, rv)
    zc, hz = (z0+z1)/2, (z1-z0)/2
    wx = d2 + rt; wy = np.abs(Z-zc) - (hz - rt)
    return np.minimum(np.maximum(wx, wy), 0) + np.hypot(np.maximum(wx,0), np.maximum(wy,0)) - rt
def smin(a, b, k):
    h = np.clip(0.5+0.5*(b-a)/k, 0, 1); return b*(1-h)+a*h - k*h*(1-h)
def smax(a, b, k): return -smin(-a, -b, k)
# solids (extend 3 mm below the bed, then cut flat so the bottom stays sharp and flat)
footd  = prism(0, 0, foot/2, foot/2, -3, fh, 4.0, 2.5)
armd   = prism((foot/2+off)/2, 0, (off-foot/2)/2, 6, -3, fh-2, 3.0, 2.0)
sleeve = prism(off, 0, OW/2, OT/2, -3, H, 3.5, 1.5)
d = smin(smin(footd, armd, 3.0), sleeve, 3.0)
# cuts
cav  = prism(off, 0, W/2, T/2, lip, H+5, 1.2, 0.01)
d = smax(d, -cav, 0.6)
usb  = prism(off, 0, ow/2, ot/2, -5, lip+0.5, 1.5, 0.01)
d = np.maximum(d, -usb)
# vent windows: stadium slots through both wide faces (normal +-y)
vz0, vz1, vw = 10.0, 40.0, 8.0
r = vw/2; zc = np.clip(Z, vz0+r, vz1-r)
slot = np.hypot(X-off, Z-zc) - r
slot = np.maximum(slot, np.abs(Y) - (OT/2+2))
d = smax(d, -slot, 0.8)
if variant == 'selftap':
    hole = np.hypot(X, Y) - 5.4/2
    cham = np.hypot(X, Y) - (5.4/2 + 1.0 - Z)        # 1 mm entry chamfer at the bottom
    d = np.maximum(d, -np.minimum(hole, cham))
elif variant == 'insert':
    ins_d, ins_l = 7.6, 8.5          # heat-set insert hole: 8 mm OD insert, 8 mm long (+0.5 for melt-out)
    pocket = np.maximum(np.hypot(X, Y) - ins_d/2, Z - ins_l)
    cham = np.hypot(X, Y) - (ins_d/2 + 0.6 - Z)      # small lead-in chamfer
    thru = np.hypot(X, Y) - 6.6/2                     # clearance above for longer tripod screws
    d = np.maximum(d, -np.minimum(np.minimum(pocket, cham), thru))
else:
    af, nt = 11.11, 5.56; sw_, sh_ = af+0.5, nt+0.5; nz = 4.0
    slotn = prism((-foot/2-2 + 6.6)/2, 0, (6.6-(-foot/2-2))/2, sw_/2, nz, nz+sh_, 0.01, 0.01)
    bolt = np.hypot(X, Y) - 6.8/2
    d = np.maximum(d, -np.minimum(slotn, bolt))
d = np.maximum(d, -Z)  # flat bottom at z=0
v, f, n, _ = marching_cubes(d.astype(np.float32), 0.0, spacing=(S, S, S))
v += np.array([x[0], y[0], z[0]])
tri = v[f]
vol = np.sum(np.einsum('ij,ij->i', tri[:,0], np.cross(tri[:,1], tri[:,2])))/6
if vol < 0: f = f[:, ::-1]; tri = v[f]; vol = -vol
nrm = np.cross(tri[:,1]-tri[:,0], tri[:,2]-tri[:,0]); nrm /= np.linalg.norm(nrm, axis=1, keepdims=True)+1e-12
out = f'nesdr-tripod-mount-{variant}.stl'
rec = np.zeros(len(f), dtype=[('n','<f4',3),('v','<f4',(3,3)),('a','<u2')])
rec['n'] = nrm; rec['v'] = tri
with open(out,'wb') as fh_:
    fh_.write(b'nesdr tripod mount smooth'.ljust(80,b' ')); fh_.write(struct.pack('<I', len(f))); fh_.write(rec.tobytes())
# edge check
e = np.sort(np.concatenate([f[:,[0,1]], f[:,[1,2]], f[:,[2,0]]]), axis=1)
_, cnt = np.unique(e, axis=0, return_counts=True)
print(out, 'tris', len(f), 'volume', round(vol), 'non-2 edges', int((cnt!=2).sum()), 'bbox', v.min(0).round(2), v.max(0).round(2))
