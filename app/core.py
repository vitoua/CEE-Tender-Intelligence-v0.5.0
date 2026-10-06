from dataclasses import dataclass,field
from datetime import datetime
from collections import defaultdict
@dataclass
class Tender:
 id:str;source:str;country:str;title:str;buyer:str='';value:float|None=None;currency:str='';deadline:datetime|None=None;status:str='active';url:str='';winner:str='';award_value:float|None=None;award_date:datetime|None=None;category:str='Other';description:str=''
class Store:
 def __init__(self):self.data={};self.runs=[]
 def add(self,src,rows):
  for x in rows:self.data[x.id]=x
  self.runs.insert(0,{'source':src,'status':'ok','count':len(rows),'error':''})
 def error(self,src,e):self.runs.insert(0,{'source':src,'status':'error','count':0,'error':str(e)})
 def countries(self):return sorted({x.country for x in self.data.values() if x.country})
store=Store()
def active(x):return (x.status or '').lower() not in {'complete','completed','awarded','cancelled','canceled','closed'} and (not x.deadline or x.deadline>=datetime.utcnow())
def analytics(rows,countries=None,df=None,dt=None):
 g=defaultdict(lambda:{'wins':0,'total':0.0});countries=set(countries or [])
 for x in rows:
  d=x.award_date or x.deadline
  if not x.winner or (countries and x.country not in countries) or (df and (not d or d.date()<df)) or (dt and (not d or d.date()>dt)):continue
  g[x.winner]['wins']+=1;g[x.winner]['total']+=x.award_value if x.award_value is not None else (x.value or 0)
 total=sum(v['total'] for v in g.values())
 return [{'winner':k,**v,'share':v['total']/total*100 if total else 0} for k,v in g.items()]
