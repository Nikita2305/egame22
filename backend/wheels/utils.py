import numpy as np
import math
import copy
#from backend.graph import Graph

"""
Stackoverflow suggestion

Create required number of nodes
Assign random x,y locations to the nodes.
WHILE nodes with no connected edges
    Select N a random node with no edge
    LOOP select M a different node at random
        IF edge N-M does NOT intersect previous edges
             Add N-M edge to graph
             BREAK out of LOOP
"""

class Vert:
    def __init__(self,x,y,i=0,power=100):
        self.x = x
        self.y = y
        self.i = i
        self.power = power
    def rotate(self,angle):
        return Vert(self.x*np.cos(angle)-self.y*np.sin(angle), self.x*np.sin(angle)+self.y*np.cos(angle), self.i, self.power)
    def distance_sq(self,o):
        return (self.x-o.x)**2+(self.y-o.y)**2
    def __str__(self):
        return "("+str(self.x)+","+str(self.y)+"["+str(self.i)+","+str(self.power)+"])"
    def triangle_area(self,v2,v3):
        x1, y1, x2, y2, x3, y3 = self.x, self.y, v2.x, v2.y, v3.x, v3.y
        return abs(0.5 * (((x2-x1)*(y3-y1))-((x3-x1)*(y2-y1))))
    def min_altitude(self,v2,v3):
        a = self.triangle_area(v2,v3)
        l = max(self.distance_sq(v2),self.distance_sq(v3))
        l = max(l,v2.distance_sq(v3))
        return 2*a/np.sqrt(l)

def check_spread(v,verts,r):
    for v2 in verts:
        if v.distance_sq(v2) < r**2:
            return False
    return True

def check_triangles_altitudes(v,verts,lim):
    for i in range(len(verts)):
        for j in range(i+1,len(verts)):
            if v.min_altitude(verts[i],verts[j]) < lim:
                return False
    return True

def generate_in_sector(rng, r1, r2, max_angle):
    r = rng.uniform(r1,r2)
    angle = rng.uniform(0,max_angle)
    return (r*np.cos(angle), r*np.sin(angle))

def ccw(A,B,C):
    return (C.y-A.y) * (B.x-A.x) > (B.y-A.y) * (C.x-A.x)

# Return true if line segments AB and CD intersect
def intersect(A,B,C,D):
    return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)

def intersect_check(e,lst):
    for edge in lst:
        if e[0] is edge[0] or e[0] is edge[1] or e[1] is edge[0] or e[1] is edge[1]:
            continue
        if intersect(e[0],e[1],edge[0],edge[1]):
            return True
    return False

import matplotlib.pyplot as plt

def plot_graph(verts,edges, spec_edges=None):
    plt.plot([a.x for a in verts], [a.y for a in verts],
             color='green', linestyle='none', linewidth = 3,
             marker='o', markerfacecolor='green', markersize=5)
    for e in edges:
        plt.plot([e[0].x, e[1].x], [e[0].y, e[1].y], linestyle='dashed', color='green')
    if spec_edges is not None:
        for e in spec_edges:
            plt.plot([e[0].x, e[1].x], [e[0].y, e[1].y], linestyle='dashed', color='blue')
    plt.show()

def generate_edges(verts, nedges):
    possible_edges = []
    edges = []
    for i in range(len(verts)):
        for j in range(i+1,len(verts)):
            possible_edges.append((verts[i],
                                   verts[j],
                                   np.sqrt(verts[i].distance_sq(verts[j]))))
    possible_edges.sort(key=lambda x: x[2])
    lst = list(verts)
    for e in possible_edges:
        if intersect_check(e,edges):
            continue
        edges.append(e)
        try:
            lst.remove(e[0])
        except ValueError:
            pass
        try:
            lst.remove(e[1])
        except ValueError:
            pass
        if len(lst) == 0 and len(edges) >= nedges:
            break
    return edges

def GraphGenerator(nteams, 
                   n_outer_ring_vert_per_team, 
                   n_core_vert_per_team,
                   n_outer_edges,
                   n_core_edges,
                   n_links,
                   seed=1223123,
                   debug=False):
    rng = np.random.default_rng(seed)
    outer_sector_v = []
    max_angle = 2*np.pi/nteams
    R = 100
    r1 = np.sqrt(n_core_vert_per_team)*R/np.sqrt(n_core_vert_per_team+n_core_vert_per_team)
    while len(outer_sector_v) != n_outer_ring_vert_per_team:
        v = generate_in_sector(rng,r1,R,max_angle)
        vv = Vert(v[0],v[1])
        if not check_spread(vv,outer_sector_v,9):
            continue
        if not check_triangles_altitudes(vv,outer_sector_v,1):
            continue
        outer_sector_v.append(vv)
    outer_sector_e = generate_edges(outer_sector_v, n_outer_edges)
    if debug:
        plot_graph(outer_sector_v,outer_sector_e)
    
    core_sector_v = []
    while len(core_sector_v) != n_core_vert_per_team:
        v = generate_in_sector(rng,0,r1*np.cos(max_angle/2.),max_angle)
        vv = Vert(v[0],v[1])
        if not check_spread(vv,core_sector_v,6):
            continue
        if not check_triangles_altitudes(vv,core_sector_v,1):
            continue
        core_sector_v.append(vv)
    core_sector_e = generate_edges(core_sector_v, n_core_edges)
    if debug:
        plot_graph(core_sector_v,core_sector_e)
    
    possible_edges = []
    for vc in core_sector_v:
        for vo in outer_sector_v:
            e  = (vc,vo,np.sqrt(vc.distance_sq(vo)))
            if intersect_check(e,outer_sector_e):
                continue
            if intersect_check(e,core_sector_e):
                continue
            possible_edges.append(e)
    possible_edges.sort(key=lambda x: x[2])
    
    sector_v = list(core_sector_v)
    sector_v += outer_sector_v
    sector_e = list(core_sector_e)
    sector_e += outer_sector_e
    sector_e += possible_edges[0:1]
    if debug:
        plot_graph(sector_v,sector_e)
    l = len(sector_v)
    sectors_v = [sector_v]
    sectors_e = [sector_e]
    for i in range(l):
        sector_v[i].i = i
        sector_v[i].power = rng.poisson(50)*2
    
    for i in range(1,nteams):
        sectors_v.append([])
        for v in sectors_v[0]:
            sectors_v[i].append(v.rotate(max_angle*i))
    
    for i in range(1,nteams):
        sectors_e.append([])
        for e in sectors_e[0]:
            sectors_e[i].append((sectors_v[i][e[0].i],
                                 sectors_v[i][e[1].i],
                                 e[2]))
    
    possible_edges = []
    for vc in sectors_v[0]:
        for vo in sectors_v[1]:
            e  = (vc,vo,np.sqrt(vc.distance_sq(vo)))
            if intersect_check(e,sectors_e[0]):
                continue
            if intersect_check(e,sectors_e[1]):
                continue
            possible_edges.append(e)
    possible_edges.sort(key=lambda x: x[2])
    
    links = []
    vertices0 = set(range(len(sectors_v[0])))
    vertices1 = set(range(len(sectors_v[0])))
    for e in possible_edges:
        if e[0].i in vertices0 and e[1].i in vertices1:
            links.append((e[0].i,e[1].i))
            vertices0.remove(e[0].i)
            vertices1.remove(e[1].i)
    
    links_e = []
    for i in range(nteams):
        j = (i+1) % nteams
        count = 0
        for l in links:
            v1 = sectors_v[i][l[0]]
            v2 = sectors_v[j][l[1]]
            e = (v1,v2,np.sqrt(v1.distance_sq(v2)))
            if intersect_check(e,links_e):
                continue
            links_e.append(e)
            count+=1
            if count >= n_links:
                break
        
    vv = sum(sectors_v,[])
    for i in range(len(vv)):
        vv[i].i = i
    ee = sum(sectors_e,[])
    
    if debug:
        plot_graph(vv,ee, links_e)
    
    ee += links_e
    for v in vv:
        v.x = float(v.x)
        v.y = float(v.y)
        v.power = float(v.power)
    return (vv,ee)


if __name__=="__main__":
    GraphGenerator(nteams=5, 
                   n_outer_ring_vert_per_team=12, 
                   n_core_vert_per_team=6,
                   n_outer_edges=16,
                   n_core_edges=8,
                   n_links=4)
