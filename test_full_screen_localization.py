"""Offline smoke test that does not require Streamlit or live APIs."""
import sys, types
from pathlib import Path
import json

if 'streamlit' not in sys.modules:
    st=types.ModuleType('streamlit')
    st.session_state={}
    sys.modules['streamlit']=st
else:
    st=sys.modules['streamlit']

from i18n import t, get_language
from ui_translate import ui_text, ui_html

langs=['tr','ja','fr','de','es','pt','zh','ar']
checks=[
 'Country & language',
 '1. Select a location and describe your farm',
 'How would you like to find your farm?',
 'What did you grow last season?',
 'What is your soil type?',
 'When does the growing season start?',
 'How many months does the season last?',
 'What is your priority?',
 'Analyze farm scenarios',
 'Space on Earth · Farm Dashboard',
 'Farm Map', 'Farm Summary', 'Action Summary',
 'Soil moisture', 'Fire risk',
 'Water need*','Sowing period*','Harvest period*','Interpretation',
 'Change farm location / Edit farm details',
]
for lang in langs:
    st.session_state['ui_language']=lang
    for item in checks:
        got=t(item)
        assert got and got != item, (lang,item,got)
    for raw in ['#### Farmer information','#### 🌿 Farm Summary','**Annual mean temperature**']:
        assert ui_text(raw)!=raw,(lang,raw)
    html="<style>.soe-head{color:red;}</style><div class='soe-head'><h1>Space on Earth · Farm Dashboard</h1><p>NASA-powered climate context · A simple overview before detailed analysis</p></div>"
    rendered=ui_html(html)
    assert "<style>.soe-head{color:red;}</style>" in rendered
    assert 'NASA-powered climate context · A simple overview before detailed analysis' not in rendered, lang
    assert 'Space on Earth · Farm Dashboard' not in rendered,lang
    assert ui_text('🌱 Chickpea')!='🌱 Chickpea', lang
    print(lang, 'core UI labels localized')
print('PASS',len(langs),'languages x',len(checks),'core labels; HTML/CSS preserved')
