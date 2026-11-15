"""Fast offline checks for visible small-text localization across dashboard tables."""
import sys
import types
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
try:
    import streamlit as st
except ImportError:
    st = types.ModuleType('streamlit')
    st.session_state = {}
    st.cache_data = lambda *a, **k: lambda f: f
    sys.modules['streamlit']=st
import pandas as pd
from i18n import t
from display_localization import localize_table, FORECAST_STATUSES, MONITOR_STATUSES

class SmallLabelTranslationTests(unittest.TestCase):
    def setUp(self):
        st.session_state['ui_language'] = 'en'

    def test_weather_headers_and_rows_tr(self):
        frame=pd.DataFrame({'Date':['2026-11-13'],'Rain (mm)':[4.5],
                            'Rain chance (%)':[62.0],
                            'Field check':['Rain possible — check forecast before watering']})
        before=frame.copy(deep=True)
        st.session_state['ui_language']='tr'
        localized=localize_table(frame,known_statuses=FORECAST_STATUSES)
        self.assertIn('Yağış (mm)',localized.columns)
        self.assertIn('Yağış olasılığı (%)',localized.columns)
        self.assertIn('Saha kontrolü',localized.columns)
        self.assertEqual(localized['Saha kontrolü'][0], 'Yağış olabilir — sulamadan önce tahmini kontrol et')
        self.assertEqual(localized['Yağış (mm)'][0],4.5)
        pd.testing.assert_frame_equal(frame,before)

    def test_six_more_languages_have_months_and_status(self):
        for lang in ('fr','ja','de','es','pt','zh','ar'):
            st.session_state['ui_language']=lang
            with self.subTest(lang=lang):
                self.assertNotEqual(t('January'),'January')
                self.assertNotEqual(t('Check local conditions'),'Check local conditions')
                self.assertNotEqual(t('Rain (mm)'),'Rain (mm)')

    def test_irrigation_months_categories_tr(self):
        frame=pd.DataFrame({'Month':['January','February'],
                            'Monitoring context':['Higher dry-day frequency','Lower dry-day frequency'],
                            'Mean rainfall (mm)':[12.2,16.3]})
        st.session_state['ui_language']='tr'
        localized=localize_table(frame,known_statuses=MONITOR_STATUSES,localize_months=True)
        self.assertEqual(localized['Ay'].tolist(),['Ocak','Şubat'])
        self.assertEqual(localized[t('Monitoring context')].tolist(),[t('Higher dry-day frequency'),t('Lower dry-day frequency')])
        self.assertEqual(localized['Ortalama yağış (mm)'].tolist(),[12.2,16.3])

    def test_dynamic_crop_labels(self):
        for lang in ('tr','fr','ja','de','es'):
            st.session_state['ui_language']=lang
            self.assertNotEqual(t('Annual rain'), 'Annual rain',lang)
            self.assertNotEqual(t('Temp'),'Temp',lang)

if __name__=='__main__': unittest.main()
