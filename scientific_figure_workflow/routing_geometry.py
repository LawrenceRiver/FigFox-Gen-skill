"""Validate explicit, orthogonal macro-graph geometry without route search.

Coordinates are canvas pixels. Slots are zero-based [row, column, row_span,
column_span]. The returned ``node_boxes`` map holds [x, y, width, height].
This module checks geometry, not arrowhead rendering or conceptual microviews.
"""
from copy import deepcopy
import math

_EPS = 1e-7
_PORTS = {'north', 'east', 'south', 'west'}
_BENDS = {'mainline': 1, 'branch': 2, 'reference': 2, 'feedback': 4}


def _number(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f'{name} must be a finite number')
    return value


def _vector(value, size, name):
    if not isinstance(value, (list, tuple)) or len(value) != size:
        raise ValueError(f'{name} must contain {size} coordinates')
    return [_number(v, name) for v in value]


def _inside_bounds(point, canvas, margin):
    return all(margin <= p <= length - margin for p, length in zip(point, canvas))


def _box(value, canvas, margin, name):
    x, y, w, h = _vector(value, 4, name)
    if w <= 0 or h <= 0 or not _inside_bounds([x,y],canvas,margin) or not _inside_bounds([x+w,y+h],canvas,margin):
        raise ValueError(f'{name} must have positive size and stay inside canvas margins')
    return [x,y,w,h]


def _tracks(value, length, margin, name):
    if not isinstance(value, list) or not value:
        raise ValueError(f'{name} must be a nonempty list of tracks')
    tracks = [_vector(track,2,name) for track in value]
    gaps = []
    for i,(a,b) in enumerate(tracks):
        if a < margin or b > length-margin or a >= b:
            raise ValueError(f'{name} tracks must be positive and within canvas margins')
        if i:
            gap = a-tracks[i-1][1]
            if gap <= 0:
                raise ValueError(f'{name} tracks must be sorted and disjoint with positive gutters')
            gaps.append(gap)
    if gaps and any(not math.isclose(g,gaps[0],abs_tol=_EPS,rel_tol=0) for g in gaps):
        raise ValueError(f'{name} must have consistent gutters')
    return tracks


def _hits_box(a, b, box, clearance=0, closed=False):
    x,y,w,h=box
    lo_x,hi_x,lo_y,hi_y=x-clearance,x+w+clearance,y-clearance,y+h+clearance
    if a[1] == b[1]:
        low,high=sorted((a[0],b[0]))
        return (lo_y <= a[1] <= hi_y and high >= lo_x and low <= hi_x) if closed else (lo_y < a[1] < hi_y and high > lo_x and low < hi_x)
    low,high=sorted((a[1],b[1]))
    return (lo_x <= a[0] <= hi_x and high >= lo_y and low <= hi_y) if closed else (lo_x < a[0] < hi_x and high > lo_y and low < hi_y)


def _touches(point, box, port):
    x,y,w,h=box;px,py=point
    return {'north':py==y and x<=px<=x+w, 'south':py==y+h and x<=px<=x+w,
            'west':px==x and y<=py<=y+h, 'east':px==x+w and y<=py<=y+h}[port]


def _port_direction(endpoint, neighbor, port):
    nx,ny={'north':(0,-1),'east':(1,0),'south':(0,1),'west':(-1,0)}[port]
    dx,dy=neighbor[0]-endpoint[0],neighbor[1]-endpoint[1]
    return dx*ny == dy*nx and dx*nx+dy*ny>0


def _intersection(a,b,c,d):
    """Return None, a point, or the two ends of a positive overlap."""
    horizontal=a[1]==b[1]; other_horizontal=c[1]==d[1]
    if horizontal != other_horizontal:
        h1,h2,v1,v2=(a,b,c,d) if horizontal else (c,d,a,b)
        p=[v1[0],h1[1]]
        if min(h1[0],h2[0])<=p[0]<=max(h1[0],h2[0]) and min(v1[1],v2[1])<=p[1]<=max(v1[1],v2[1]):
            return p
        return None
    axis=0 if horizontal else 1;fixed=1-axis
    if a[fixed]!=c[fixed]:return None
    lo=max(min(a[axis],b[axis]),min(c[axis],d[axis]));hi=min(max(a[axis],b[axis]),max(c[axis],d[axis]))
    if lo>hi:return None
    p=list(a);p[axis]=lo
    if lo==hi:return p
    q=list(a);q[axis]=hi
    return [p,q]


def _on_segment(point,a,b):
    return _intersection(a,b,point,point)==point


def _shared_stem(left,right):
    a,b=left['points'][:2];c,d=right['points'][:2]
    if left['source_id'] != right['source_id'] or a!=c:return None
    if (b[0]-a[0])*(d[0]-c[0])+(b[1]-a[1])*(d[1]-c[1])<=0:return None
    hit=_intersection(a,b,c,d)
    return hit if hit and isinstance(hit[0],list) else None


def compile_routing_geometry(geometry, routes, component_ids):
    """Return detached normalized geometry/routes, or raise a descriptive ValueError."""
    if isinstance(geometry, dict) and geometry.get('routing_policy') == 'simple':
        return _compile_simple_routes(geometry, routes, component_ids)
    if not isinstance(geometry,dict) or not isinstance(routes,list):
        raise ValueError('routing geometry must be an object and routes must be a list')
    g=deepcopy(geometry);result=deepcopy(routes)
    canvas=_vector(g.get('canvas'),2,'canvas')
    if min(canvas)<=0:raise ValueError('canvas dimensions must be positive')
    margin=_number(g.get('margin',20),'margin');clearance=_number(g.get('clearance',8),'clearance')
    if margin<0 or clearance<0:raise ValueError('margin and clearance must be nonnegative')
    cols=_tracks(g.get('columns'),canvas[0],margin,'columns');rows=_tracks(g.get('rows'),canvas[1],margin,'rows')
    slots=g.get('slots');ids=list(component_ids)
    if not isinstance(slots,dict) or len(ids)!=len(set(ids)) or set(slots)!=set(ids):
        raise ValueError('slots must assign every exact component ID once')
    boxes={};occupied=set()
    for ident,slot in slots.items():
        if not isinstance(slot,(list,tuple)) or len(slot)!=4 or any(type(v) is not int for v in slot):
            raise ValueError(f'slot {ident} must contain four integers')
        row,col,rs,cs=slot
        if min(row,col)<0 or min(rs,cs)<=0 or row+rs>len(rows) or col+cs>len(cols):
            raise ValueError(f'slot {ident} has invalid span or bounds')
        cells={(r,c) for r in range(row,row+rs) for c in range(col,col+cs)}
        if cells & occupied:raise ValueError(f'slot {ident} overlaps occupied cells')
        occupied.update(cells)
        x,y=cols[col][0],rows[row][0]
        boxes[ident]=[x,y,cols[col+cs-1][1]-x,rows[row+rs-1][1]-y]
    g.update(canvas=canvas,margin=margin,clearance=clearance,columns=cols,rows=rows,node_boxes=boxes)
    for index,route in enumerate(result):
        if not isinstance(route,dict):raise ValueError(f'route {index} must be an object')
        source,target=route.get('source_id'),route.get('target_id')
        if source not in boxes or target not in boxes:raise ValueError(f'route {index} references unknown component')
        kind=route.get('route_kind')
        if kind not in _BENDS:raise ValueError(f'route {index} requires a valid route_kind')
        points=route.get('points')
        if not isinstance(points,list) or len(points)<2:raise ValueError(f'route {index} needs at least two distinct points')
        points=[_vector(p,2,f'route {index} point') for p in points]
        if any(not _inside_bounds(p,canvas,margin) for p in points):raise ValueError(f'route {index} is outside canvas margins')
        cleaned=[]
        for p in points:
            if cleaned and p==cleaned[-1]:continue
            if cleaned and p[0]!=cleaned[-1][0] and p[1]!=cleaned[-1][1]:raise ValueError(f'route {index} has a diagonal segment')
            # Only collapse forward collinearity; reversals remain invalid overlaps.
            while len(cleaned)>=2 and ((cleaned[-1][0]-cleaned[-2][0])*(p[1]-cleaned[-1][1]) == (cleaned[-1][1]-cleaned[-2][1])*(p[0]-cleaned[-1][0])) and ((cleaned[-1][0]-cleaned[-2][0])*(p[0]-cleaned[-1][0])+(cleaned[-1][1]-cleaned[-2][1])*(p[1]-cleaned[-1][1])>0):cleaned.pop()
            cleaned.append(p)
        if len(cleaned)<2:raise ValueError(f'route {index} needs at least two distinct points')
        for endpoint,ident,field in [(cleaned[0],source,'source_port'),(cleaned[-1],target,'target_port')]:
            port=route.get(field)
            if port not in _PORTS or not _touches(endpoint,boxes[ident],port):raise ValueError(f'route {index} endpoint is detached or on wrong {field}')
        for endpoint,neighbor,field in [(cleaned[0],cleaned[1],'source_port'),(cleaned[-1],cleaned[-2],'target_port')]:
            if not _port_direction(endpoint,neighbor,route[field]):
                raise ValueError(f'route {index} has wrong direction at {field}')
        segments=list(zip(cleaned,cleaned[1:]))
        for a,b in segments:
            for ident,box in boxes.items():
                if _hits_box(a,b,box):raise ValueError(f'route {index} crosses node {ident} interior')
                if ident not in (source,target) and _hits_box(a,b,box,clearance):raise ValueError(f'route {index} violates node {ident} clearance')
        for i,(a,b) in enumerate(segments):
            for j,(c,d) in enumerate(segments[i+1:],i+1):
                hit=_intersection(a,b,c,d)
                if hit is not None and (j!=i+1 or isinstance(hit[0],list)):
                    raise ValueError(f'route {index} intersects or overlaps itself')
        if len(cleaned)-2>_BENDS[kind]:raise ValueError(f'route {index} has excessive bends for {kind}')
        first,last=cleaned[0],cleaned[-1]
        if (len(cleaned)>2 and (first[0]==last[0] or first[1]==last[1])
                and _port_direction(first,last,route['source_port'])
                and _port_direction(last,first,route['target_port'])):
            if all(not _hits_box(first,last,box,0 if ident in (source,target) else clearance) for ident,box in boxes.items()):
                raise ValueError(f'route {index} makes a needless detour from a clear direct path')
        route['points']=cleaned
    _validate_crossings(g,result)
    _validate_captions(g,result)
    return g,result


def _compile_simple_routes(geometry, routes, component_ids):
    """Basic lines/one smooth Bezier, with conservative sampled curve checks.

    This preflight catches gross obstructions; pixel inspection is still required.
    Cubic control points describe the curve, never an orthogonal staircase.
    """
    from .svg_workflow import simple_degree_check
    legacy = deepcopy(geometry)
    legacy.pop('routing_policy')
    g, _ = compile_routing_geometry(legacy, [], component_ids)
    g['routing_policy'] = 'simple'
    boxes = g['node_boxes']
    simple_degree_check(g, routes)
    result = deepcopy(routes)
    sampled = []
    for index, route in enumerate(result):
        source, target = route.get('source_id'), route.get('target_id')
        if source not in boxes or target not in boxes:
            raise ValueError('Simple route references an unknown component')
        if route.get('route_kind') not in _BENDS:
            raise ValueError('Simple route requires route_kind')
        points = [_vector(p, 2, 'simple route point') for p in route.get('points', [])]
        curve = route.get('curve')
        if curve:
            expected = {'quadratic': 3, 'cubic': 4}.get(curve)
            if expected is None or len(points) != expected:
                raise ValueError('Simple curve needs quadratic/cubic control points')
            n = len(points) - 1
            samples = [[sum(math.comb(n,k) * (1-t)**(n-k) * t**k * p[axis]
                            for k,p in enumerate(points)) for axis in (0,1)]
                       for t in [i/128 for i in range(129)]]
        else:
            if len(points) not in (2,3) or (len(points) == 3 and not all(a[0] == b[0] or a[1] == b[1] for a,b in zip(points,points[1:]))):
                raise ValueError('No staircase routes: redesign frames or use one simple curve')
            samples = points
        if any(not _inside_bounds(p, g['canvas'], g['margin']) for p in [*points, *samples]):
            raise ValueError('Simple route leaves the canvas')
        if any(a == b for a,b in zip(points,points[1:])):
            raise ValueError('Simple route has duplicate points')
        for p, neighbor, ident, field in [(points[0],points[1],source,'source_port'), (points[-1],points[-2],target,'target_port')]:
            port = route.get(field)
            if port not in _PORTS or not _touches(p,boxes[ident],port) or not _port_direction(p,neighbor,port):
                raise ValueError('Simple route endpoint is detached or has wrong port direction')
        for ident, box in boxes.items():
            x,y,w,h = box
            gap = 0 if ident in (source,target) else g['clearance']
            # Segment clipping, so even a diagonal passing between samples is checked.
            for a,b in zip(samples,samples[1:]):
                lo,hi = 0.,1.
                for start,delta,low,high in [(a[0],b[0]-a[0],x-gap,x+w+gap),(a[1],b[1]-a[1],y-gap,y+h+gap)]:
                    if abs(delta) < _EPS:
                        if not low+_EPS < start < high-_EPS:lo,hi=1.,0.;break
                    else:
                        t0,t1=sorted(((low-start)/delta,(high-start)/delta))
                        lo,hi=max(lo,t0),min(hi,t1)
                if hi-lo > _EPS:
                    raise ValueError(f'Simple route {index} crosses node {ident}; move frames before routing')
        route['points'] = points
        sampled.append(samples)
    # Unrelated paths must not cross. A straight/curve family has no crossover bridge escape hatch.
    def intersects(a,b,c,d):
        def cross(p,q,r):return (q[0]-p[0])*(r[1]-p[1])-(q[1]-p[1])*(r[0]-p[0])
        return cross(a,b,c)*cross(a,b,d) < -_EPS and cross(c,d,a)*cross(c,d,b) < -_EPS
    for i,left in enumerate(sampled):
        for j,right in enumerate(sampled[i+1:],i+1):
            if any(intersects(a,b,c,d) for a,b in zip(left,left[1:]) for c,d in zip(right,right[1:])):
                raise ValueError(f'Simple routes {i} and {j} cross; redesign frame positions')
    captions=[]
    for index,route in enumerate(result):
        caption=route.get('caption','')
        if not isinstance(caption,str):raise ValueError('Simple route caption must be text')
        if not caption.strip():continue
        box=_box(route.get('caption_box'),g['canvas'],g['margin'],f'route {index} caption box')
        x,y,w,h=box
        for other in list(boxes.values())+captions:
            ox,oy,ow,oh=other
            if x<ox+ow and x+w>ox and y<oy+oh and y+h>oy:
                raise ValueError('Simple route caption overlaps a node or another caption')
        for path in sampled:
            for a,b in zip(path,path[1:]):
                lo,hi=0.,1.
                for start,delta,low,high in [(a[0],b[0]-a[0],x,x+w),(a[1],b[1]-a[1],y,y+h)]:
                    if abs(delta)<_EPS:
                        if not low-_EPS<=start<=high+_EPS:lo,hi=1.,0.;break
                    else:
                        t0,t1=sorted(((low-start)/delta,(high-start)/delta))
                        lo,hi=max(lo,t0),min(hi,t1)
                if hi>=lo:
                    raise ValueError('Simple route caption obstructs a line or sampled curve')
        captions.append(box);route['caption_box']=box
    return g,result


def _validate_crossings(geometry,routes):
    records=geometry.get('crossings',[])
    if not isinstance(records,list):raise ValueError('crossings must be a list')
    declared={}
    for record in records:
        if not isinstance(record,dict):raise ValueError('crossing must be an object')
        pair=record.get('routes')
        if not isinstance(pair,list) or len(pair)!=2 or any(type(i) is not int or i<0 or i>=len(routes) for i in pair) or pair[0]==pair[1]:raise ValueError('crossing routes must name two different route indices')
        point=_vector(record.get('point'),2,'crossing point')
        if record.get('treatment') not in ('bridge','distinct_ink') or not isinstance(record.get('reason'),str) or not record['reason'].strip():raise ValueError('crossing needs a bridge/distinct_ink treatment and nonempty reason')
        key=(tuple(sorted(pair)),tuple(point))
        if key in declared:raise ValueError('duplicate crossing record')
        declared[key]=record
    actual=set();counts=[0]*len(routes)
    for i,left in enumerate(routes):
        for j in range(i+1,len(routes)):
            right=routes[j];stem=_shared_stem(left,right);hits=set()
            if left['points'][-1] == right['points'][-1]:
                raise ValueError(f'routes {i} and {j} merge at a target; use separate ports')
            for a,b in zip(left['points'],left['points'][1:]):
                for c,d in zip(right['points'],right['points'][1:]):
                    hit=_intersection(a,b,c,d)
                    if hit is None:continue
                    overlap=isinstance(hit[0],list)
                    if overlap:
                        if stem and all(_on_segment(p,*stem) for p in hit):continue
                        raise ValueError(f'routes {i} and {j} have a forbidden overlap')
                    if stem and _on_segment(hit,*stem):continue
                    if hit==left['points'][-1] or hit==right['points'][-1]:raise ValueError(f'routes {i} and {j} merge at a target; use separate ports')
                    hits.add(tuple(hit))
            for hit in hits:
                key=((i,j),hit);actual.add(key);counts[i]+=1;counts[j]+=1
                if key not in declared:raise ValueError(f'undeclared crossing between routes {i} and {j} at {hit}')
    if set(declared)!=actual:raise ValueError('stale or unused crossing record does not match a real intersection')
    if any(n>1 for n in counts):raise ValueError('at most one crossing per route; rearrange the layout')


def _validate_captions(geometry,routes):
    captions=[]
    for index,route in enumerate(routes):
        caption=route.get('caption','')
        if not isinstance(caption,str):raise ValueError(f'route {index} caption must be text')
        if not caption.strip():continue
        box=_box(route.get('caption_box'),geometry['canvas'],geometry['margin'],f'route {index} caption_box')
        x,y,w,h=box
        for other in list(geometry['node_boxes'].values())+captions:
            ox,oy,ow,oh=other
            if x<ox+ow and x+w>ox and y<oy+oh and y+h>oy:raise ValueError(f'route {index} caption overlaps a node or another caption')
        for other in routes:
            if any(_hits_box(a,b,box,closed=True) for a,b in zip(other['points'],other['points'][1:])):raise ValueError(f'route {index} caption obstructs a route shaft')
        captions.append(box);route['caption_box']=box
