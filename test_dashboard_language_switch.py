"""Offline dashboard localization regression tests (no API or internet needed)."""
import sys, types, unittest
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
try:
    import streamlit as st
except ImportError:
    st = types.ModuleType('streamlit')
    st.session_state = {}
    st.cache_data = lambda *args,**kwargs: lambda f: f
    sys.modules['streamlit'] = st
from ui_translate import ui_html, ui_text
from i18n import t

class DashboardLanguageSwitchTests(unittest.TestCase):
    def test_bundled_dashboard_five_languages(self):
        expected = {
            'tr': ('Çiftlik Özeti', 'Ürün', 'Koordinatlar'),
            'fr': ('Résumé de la ferme', 'Culture', 'Coordonnées'),
            'ja': ('農場の概要', '作物', '座標'),
            'de': ('Hofübersicht', 'Kulturpflanze', 'Koordinaten'),
            'es': ('Resumen de la finca', 'Cultivo', 'Coordenadas'),
        }
        for lang, (farm, crop, coords) in expected.items():
            st.session_state['ui_language'] = lang
            self.assertIn(farm, ui_html('#### 🌿 Farm Summary'))
            self.assertIn(crop, ui_html('<div><span>Crop</span><span>Demo score</span></div>'))
            self.assertIn(coords, ui_text('📍 Coordinates'))

    def test_interpolated_weather_keeps_nasa_measurements(self):
        st.session_state['ui_language'] = 'tr'
        result = ui_html('<div>Temp 26.1°C (3.0/4); Annual rain 530mm (2.5/4)</div>')
        self.assertIn('Sıcaklık', result)
        self.assertIn('Yıllık yağış', result)
        self.assertIn('26.1°C', result)
        self.assertIn('530mm', result)

    def test_html_markup_preserved_and_css_untouched(self):
        st.session_state['ui_language'] = 'fr'
        source = '<style>.Crop{color:red}</style><div class="Crop"><span>Farm Summary</span></div>'
        result=ui_html(source)
        self.assertIn('<style>.Crop{color:red}</style>', result)
        self.assertIn('class="Crop"', result)
        self.assertIn('Résumé de la ferme', result)

    def test_switch_back_to_english(self):
        st.session_state['ui_language'] = 'ja'
        self.assertIn('農場の概要', ui_text('Farm Summary'))
        st.session_state['ui_language'] = 'en'
        self.assertEqual(ui_text('Farm Summary'),'Farm Summary')

if __name__=='__main__': unittest.main()
