from datetime import datetime
import httpx
from app.core import Tender
BASE='https://public-api.prozorro.gov.ua/api/2.5/tenders'
def dt(v):
 try:return datetime.fromisoformat(str(v).replace('Z','+00:00')).replace(tzinfo=None)
 except:return None
async def fetch(limit=200):
 out=[]
 async with httpx.AsyncClient(timeout=40,follow_redirects=True) as c:
  feed=(await c.get(BASE,params={'limit':limit,'descending':1}));feed.raise_for_status()
  for row in feed.json().get('data',[]):
   x=(await c.get(f"{BASE}/{row['id']}")).json().get('data',{});v=x.get('value') or {};p=x.get('tenderPeriod') or {};a=next((a for a in x.get('awards',[]) if a.get('status')=='active'),{});s=(a.get('suppliers') or [{}])[0]
   out.append(Tender('prozorro:'+x.get('tenderID',row['id']),'prozorro','UKR',x.get('title') or x.get('tenderID',''),(x.get('procuringEntity') or {}).get('name',''),v.get('amount'),v.get('currency',''),dt(p.get('endDate')),x.get('status',''),f"https://prozorro.gov.ua/tender/{x.get('tenderID','')}",s.get('name',''),(a.get('value') or {}).get('amount'),dt(a.get('date')),description=x.get('description','')))
 return out
