from datetime import datetime
import httpx
from app.core import Tender
URL='https://api.ted.europa.eu/v3/notices/search'
def first(v):
 if isinstance(v,dict):
  for k in ('eng','pol','ukr','deu','fra'):
   if k in v:return first(v[k])
  return first(next(iter(v.values()),''))
 if isinstance(v,list):return first(v[0]) if v else ''
 return str(v or '')
def dt(v):
 try:return datetime.fromisoformat(first(v)[:10])
 except:return None
def number(v):
 try:return float(first(v))
 except:return None
async def fetch(limit=200):
 queries=['FT~"SSD" OR FT~"NVMe" OR FT~"DDR4" OR FT~"DDR5" OR FT~"memory card" OR FT~"flash drive"','classification-cpv IN (30233100 30233130 30234100 30236100 30237200)']; notices=[];err=''
 async with httpx.AsyncClient(timeout=45,follow_redirects=True,headers={'User-Agent':'CEE-Tender-Intelligence/0.5','Accept':'application/json'}) as c:
  for q in queries:
   payload={'query':q,'page':1,'limit':min(limit,200),'scope':'ALL','checkQuerySyntax':False,'paginationMode':'PAGE_NUMBER','onlyLatestVersions':True}
   r=await c.post(URL,json=payload)
   if r.status_code==200:notices=r.json().get('notices') or [];break
   err=f'HTTP {r.status_code}: {r.text[:700]}'
  else:raise RuntimeError('TED API: '+err)
 out=[]
 for x in notices:
  n=first(x.get('publication-number')) or first(x.get('notice-identifier'));w=first(x.get('winner-name'))
  out.append(Tender('ted:'+n,'ted',first(x.get('buyer-country'))[:3] or 'EU',first(x.get('notice-title')) or n,first(x.get('buyer-name')),number(x.get('total-value')),first(x.get('total-value-cur')),dt(x.get('deadline')),'awarded' if w else 'active',f'https://ted.europa.eu/en/notice/-/detail/{n}',w,number(x.get('contract-value')),dt(x.get('contract-conclusion-date')),description=first(x.get('description-proc')) or first(x.get('description-lot'))))
 return out
