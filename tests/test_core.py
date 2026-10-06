from app.core import Tender,analytics
def test_sort_data():
 r=analytics([Tender('1','x','PL','x',status='complete',winner='A',award_value=10),Tender('2','x','PL','x',status='complete',winner='A',award_value=20),Tender('3','x','PL','x',status='complete',winner='B',award_value=50)])
 assert sorted(r,key=lambda x:x['wins'],reverse=True)[0]['winner']=='A'
 assert sorted(r,key=lambda x:x['total'],reverse=True)[0]['winner']=='B'
