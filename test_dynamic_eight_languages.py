"""Offline checks of previously English crop cells and Section 3 labels."""
import sys
import types
import unittest
from datetime import date

if 'streamlit' not in sys.modules:
    st = types.ModuleType('streamlit')
    st.session_state = {}
    st.cache_data = lambda *a, **k: lambda fn: fn
    sys.modules['streamlit'] = st
else:
    st = sys.modules['streamlit']
from i18n import t, local_date
from ui_translate import ui_text, ui_html
from input_guidance_panel import _l

LANGUAGES = ('tr', 'ja', 'fr', 'de', 'es', 'pt', 'zh', 'ar')
CROP_TERMS = (
    'Lower water need*', 'Moderate water need*', 'Higher water need*',
    'Not estimable — no temperature-screened sowing month',
    'Not established', 'Harvest dates are estimates based on historical sowing months and FAO crop cycles; they are not forecasts.',
    'Crop water categories and rankings are illustrative; check local conditions before planting.',
)
OTHER_TERMS = (
    'Crop name (you can enter any crop)', 'Expected/actual harvest date (optional)',
    'SoilGrids provides model estimates, not field measurements.',
    'Month to monitor most closely:', 'Time-of-day guidance',
    'NASA POWER gridded climate data for your location.',
    'SECTION 3: SMART FARM INPUTS & FIELD CHECKS',
    'Check for pests before treating. Ask an agronomist if needed.',
    'Soil test needed', 'Data sources', 'Method and limits'
)

class DynamicLanguageTest(unittest.TestCase):
    def test_eight_languages_have_real_offline_text(self):
        for lang in LANGUAGES:
            st.session_state['ui_language'] = lang
            for phrase in CROP_TERMS + OTHER_TERMS:
                with self.subTest(language=lang, text=phrase):
                    self.assertNotEqual(ui_text(phrase), phrase)
            self.assertNotEqual(local_date(date(2027,3,10)), '10 March 2027')
            self.assertEqual('26.7°C', ui_html('<span>26.7°C</span>')[6:-7])
    def test_section_three_uses_current_language_not_previous(self):
        source = 'Önce tarlada böcek var mı kontrol et. Gerekirse uzmana sor.'
        outputs = []
        for lang in LANGUAGES:
            st.session_state['ui_language'] = lang
            outputs.append(_l(source))
        self.assertEqual(len(set(outputs)), len(LANGUAGES))
    def test_english_restored(self):
        st.session_state['ui_language'] = 'ja'
        self.assertNotEqual(t('Moderate water need*'),'Moderate water need*')
        st.session_state['ui_language'] = 'en'
        self.assertEqual(t('Moderate water need*'),'Moderate water need*')

if __name__ == '__main__':
    unittest.main()
