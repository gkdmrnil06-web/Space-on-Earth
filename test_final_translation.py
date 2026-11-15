"""Offline smoke tests for the final free multilingual integration (no network needed)."""
import ast
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

try:
    import streamlit as st
except ImportError:
    st = types.ModuleType('streamlit')
    st.session_state = {}
    st.cache_data = lambda *args, **kwargs: lambda func: func
    sys.modules['streamlit'] = st

from i18n import t
from country_language import default_language
from input_guidance_panel import _l, _line, _display_status
from input_guidance_logic import evaluate
from free_translation import get_saved, save


class TranslationSmokeTests(unittest.TestCase):
    def setUp(self):
        st.session_state['ui_language'] = 'en'

    def test_language_country_mapping(self):
        for country, expected in [('TR','tr'),('FR','fr'),('JP','ja'),('DE','de'),('ES','es'),('US','en'),('BR','pt')]:
            self.assertEqual(default_language(country),expected)

    def test_switching_does_not_reuse_prior_language(self):
        source = 'Crop'
        for lang, expected in [('fr','Culture'),('ja','作物'),('tr','Ürün'),('en','Crop'),('de','Kulturpflanze'),('es','Cultivo')]:
            st.session_state['ui_language'] = lang
            # source 'Crop' has curated values for tr and new offline catalogs for others.
            value = t(source)
            self.assertEqual(value,expected,(lang,value))

    def test_section_three_labels_switch(self):
        st.session_state['ui_language'] = 'tr'
        self.assertEqual(_l('Zararlıyı kontrol et'), 'Zararlıyı kontrol et')
        st.session_state['ui_language'] = 'en'
        self.assertEqual(_l('Zararlıyı kontrol et'), 'Check for pests')
        self.assertEqual(_l('Tahlil gerek'),'Soil test needed')
        st.session_state['ui_language'] = 'fr'
        self.assertEqual(_l('Zararlıyı kontrol et'), 'Chercher des ravageurs')

    def test_dynamic_text_language(self):
        st.session_state['ui_language'] = 'tr'
        self.assertEqual(_line('Last 7d rain: {rain} mm', '7 günlük yağış: {rain} mm', rain='8.5'), '7 günlük yağış: 8.5 mm')
        st.session_state['ui_language'] = 'en'
        self.assertEqual(_line('Last 7d rain: {rain} mm', '7 günlük yağış: {rain} mm', rain='8.5'), 'Last 7d rain: 8.5 mm')

    def test_climate_decisions_remain_separate(self):
        rainy = {'humidity_7d_avg_pct':90,'rainfall_7d_mm':40,'temperature_max_7d_avg_c':27,'wind_7d_avg_ms':2}
        dry = {'humidity_7d_avg_pct':45,'rainfall_7d_mm':0,'temperature_max_7d_avg_c':18,'wind_7d_avg_ms':1}
        a=evaluate(rainy); b=evaluate(dry)
        self.assertEqual(len(a),4)
        self.assertEqual(len(b),4)
        self.assertEqual(_l('Tahlil gerek'),'Soil test needed')

    def test_no_cloud_credentials(self):
        self.assertFalse((HERE/'cloud_translation.py').exists())
        self.assertFalse((HERE/'GOOGLE_TRANSLATION_SETUP.txt').exists())

    def test_all_python_sources_parse(self):
        for path in HERE.glob('*.py'):
            with self.subTest(path=path.name):
                ast.parse(path.read_text(encoding='utf-8'))

    def test_deleted_blocks_not_in_app(self):
        app = (HERE/'app.py').read_text(encoding='utf-8')
        self.assertNotIn("render_multi_season_panel(",app)
        self.assertNotIn("render_water_exposure_panel(",app)
        self.assertNotIn('Compare crop rotation scenarios',app)
        self.assertIn('get_nasa_conditions', (HERE/'dashboard_ui.py').read_text())

if __name__ == '__main__':
    unittest.main()
