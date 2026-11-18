"""Deterministic PDF evidence extraction. No model, API, OCR inference or SAM."""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import fitz


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def extract_assets(pdf_path, out_dir, crops=None, render_scale=2):
    """Extract positioned text and actual embedded images; optional page-rect crops.

    ``crops`` is a list of {id,type,page,bbox,caption}; pages are one-based and
    bboxes use the PDF's point coordinate system, not pixels. Geometry is never
    guessed for vector figures: the Harness must inspect and request a crop.
    """
    def checked_scale(value):
        if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or not .25<=value<=16:raise ValueError('render_scale must be finite and between .25 and 16')
        return value
    render_scale=checked_scale(render_scale)
    pdf_path=Path(pdf_path).resolve(); out=Path(out_dir).resolve()
    raw=pdf_path.read_bytes(); source_hash=_sha(raw)
    doc=fitz.open(pdf_path)
    if doc.needs_pass: raise ValueError('PDF is encrypted and cannot be read')
    out.mkdir(parents=True,exist_ok=True); (out/'images').mkdir(exist_ok=True)
    (out/'pages').mkdir(exist_ok=True)
    table={'format':'posfoxgen-assets-v1','root':str(out),
           'source':{'path':str(pdf_path),'paper_sha256':source_hash,'page_count':len(doc)},
           'pages':[],'assets':[],
           'extraction_notes':['Text and embedded images are extracted from the PDF; vector figure/table crops require inspected rectangles.','No scientific correctness is inferred by this tool.']}
    used=set()
    def add(record):
        if record['id'] in used:raise ValueError('duplicate asset id: '+record['id'])
        used.add(record['id']);record['source']={'page':record['page'],'locator':record['source_locator'],'paper_sha256':source_hash}
        if record.get('path') and record.get('width') and record.get('height'):
            x0,y0,x1,y1=record['bbox']
            record['geometry']={'pdf_size_pt':[x1-x0,y1-y0], 'pixel_size':[record['width'],record['height']], 'aspect_ratio':record['width']/record['height']}
        table['assets'].append(record)
    for page_index,page in enumerate(doc):
        page_num=page_index+1
        preview=f'pages/page-{page_num:03d}.png'
        page.get_pixmap(matrix=fitz.Matrix(1.5,1.5),alpha=False).save(str(out/preview))
        blocks=[b for b in page.get_text('blocks') if len(b)>6 and b[6]==0 and b[4].strip()]
        table['pages'].append({'page':page_num,'width':page.rect.width,'height':page.rect.height,'text':page.get_text(),'preview':preview,'source_locator':f'PDF page {page_num}'})
        for j,b in enumerate(blocks,1):
            text=b[4].strip();bbox=list(map(float,b[:4]))
            add({'id':f'text-p{page_num:03d}-{j:03d}','type':'text','page':page_num,'bbox':bbox,'text':text,'caption':'','source_locator':f'PDF page {page_num}, text block {j}','sha256':_sha(text.encode())})
        seen=set();image_index=0
        for image in page.get_images(full=True):
            xref=image[0]
            if xref in seen:continue
            seen.add(xref)
            data=doc.extract_image(xref)
            for rect in page.get_image_rects(xref):
                image_index+=1;path=f'images/figure-p{page_num:03d}-{image_index:03d}.{data["ext"]}'
                (out/path).write_bytes(data['image'])
                candidates=[b for b in blocks if b[1]>=rect.y1-5 and b[1]-rect.y1<160 and re.match(r'\s*(?:Fig(?:ure)?\.?|Table)\s*[\dIVX]',b[4],re.I)]
                caption=min(candidates,key=lambda b:b[1])[4].strip() if candidates else ''
                add({'id':f'figure-p{page_num:03d}-{image_index:03d}','type':'figure','page':page_num,'bbox':[float(v) for v in rect],'path':path,'caption':caption,'source_locator':f'PDF page {page_num}, embedded image xref {xref}, occurrence {image_index}','sha256':_sha(data['image']),'width':data['width'],'height':data['height']})
    for requested in crops or []:
        name=requested.get('id','')
        if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_.-]*',name):raise ValueError('crop id must be a stable identifier')
        n=requested.get('page')
        if not isinstance(n,int) or isinstance(n,bool) or not 1<=n<=len(doc):raise ValueError('crop page is outside PDF')
        bbox=requested.get('bbox',[])
        if len(bbox)!=4:raise ValueError('crop bounds require four coordinates')
        rect=fitz.Rect(bbox);page=doc[n-1]
        if rect.is_empty or rect.is_infinite or not page.rect.contains(rect):raise ValueError('crop bounds are outside page')
        kind=requested.get('type','figure')
        if kind not in {'figure','table'}:raise ValueError('crop type must be figure or table')
        scale=checked_scale(requested.get('render_scale',render_scale))
        path='images/'+name+'.png';pixmap=page.get_pixmap(matrix=fitz.Matrix(scale,scale),clip=rect,alpha=False);pixmap.set_dpi(round(scale*72),round(scale*72));pixmap.save(str(out/path))
        add({'id':name,'type':kind,'page':n,'bbox':[float(v) for v in rect],'path':path,'caption':requested.get('caption',''),'source_locator':requested.get('source_locator',f'PDF page {n}, inspected rectangular crop {list(rect)}'),'sha256':_sha((out/path).read_bytes()),'extraction':'page_rect_crop','render_scale':scale,'render_dpi':scale*72,'width':pixmap.width,'height':pixmap.height,'source_bounds_verified':True})
    (out/'asset_table.json').write_text(json.dumps(table,ensure_ascii=False,indent=2))
    doc.close();return table


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pdf');parser.add_argument('--out',required=True)
    parser.add_argument('--crops',help='JSON array of inspected page/bbox crops')
    parser.add_argument('--render-scale',type=float,default=2,help='PDF crop pixels per point (default 2; 4 gives 288 DPI). Per-crop render_scale can override it.')
    args=parser.parse_args(argv)
    crops=json.loads(Path(args.crops).read_text()) if args.crops else None
    table=extract_assets(args.pdf,args.out,crops,render_scale=args.render_scale)
    print(json.dumps({'asset_table':str(Path(args.out)/'asset_table.json'),'pages':len(table['pages']),'assets':len(table['assets'])}))


if __name__=='__main__':main()
