import sys, types, unittest
from unittest.mock import patch
from datetime import date, timedelta
import requests
try:
 import streamlit
except ImportError:
 stub=types.ModuleType('streamlit');stub.cache_data=lambda *a,**k: lambda f:f
 sys.modules['streamlit']=stub
import nasa_conditions as nc

DATE=(date.today()-timedelta(days=5)).strftime('%Y%m%d')

def weather(*a,**kw):
 return {"T2M_MAX":{},"RH2M":{},"WS10M":{},"PRECTOTCORR":{}}

class TestFallback(unittest.TestCase):
 def test_primary(self):
  def fake(lat,lon,community,params,**kwargs):
   return {"SFMC":{DATE:0.26}} if community=='HY' else weather()
  with patch.object(nc,'_daily',side_effect=fake):
   res=nc.get_nasa_conditions(1,2)
  self.assertAlmostEqual(res['moisture']['volumetric_pct'],26)
  self.assertIsNone(res['soil_wetness'])

 def test_422_retry_in_ag(self):
  response=requests.Response();response.status_code=422;response._content=b'unsupported community'
  def fake(lat,lon,community,params,**kwargs):
   if community=='HY' and params==('SFMC',):
    e=requests.HTTPError('422');e.response=response;raise e
   if params==('SFMC',):return {'SFMC':{DATE:0.18}}
   return weather()
  with patch.object(nc,'_daily',side_effect=fake):
   res=nc.get_nasa_conditions(1,2)
  self.assertAlmostEqual(res['moisture']['volumetric_pct'],18)
  self.assertEqual(res['moisture']['community'],'AG')

 def test_wetness_not_mislabeled(self):
  def fake(lat,lon,community,params,**kwargs):
   if params==('SFMC',):return {'SFMC':{DATE:-999}}
   if params==('GWETTOP',):return {'GWETTOP':{DATE:0.73}}
   return weather()
  with patch.object(nc,'_daily',side_effect=fake):
   res=nc.get_nasa_conditions(1,2)
  self.assertIsNone(res['moisture'])
  self.assertAlmostEqual(res['soil_wetness']['fraction'],.73)
  self.assertEqual(res['moisture_status'],'wetness_fallback')

 def test_dns_failure_explained(self):
  def fake(*args,**kwargs):
   if kwargs.get('lookback_days')==180:raise requests.ConnectionError('DNS lookup failed')
   return weather()
  with patch.object(nc,'_daily',side_effect=fake):
   res=nc.get_nasa_conditions(1,2)
  self.assertEqual(res['moisture_status'],'network_error')
  self.assertIn('DNS',res['moisture_detail'])

 def test_missing(self):
  def fake(*args,**kwargs):
   if kwargs.get('lookback_days')==180:return {}
   return weather()
  with patch.object(nc,'_daily',side_effect=fake):
   res=nc.get_nasa_conditions(1,2)
  self.assertEqual(res['moisture_status'],'missing')
  self.assertIsNone(res['moisture'])
  self.assertIsNone(res['soil_wetness'])

if __name__=='__main__':unittest.main()
