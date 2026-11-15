"""Space on Earth: NASA climate context and exploratory crop rotation scenarios."""
from i18n import t, get_language
from ui_translate import ui_text, ui_markdown
import folium
import pandas as pd
import plotly.express as px
import streamlit as st
from section_numbering import numbered_section
from streamlit_folium import st_folium
from streamlit_geolocation import streamlit_geolocation
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderServiceError, GeocoderTimedOut
from auth import require_access
from nasa_data import get_historical_data, annual_statistics, climate_comparison, seasonal_comparison
from crop_rotation import CROPS, SOIL_OPTIONS, recent_annual_rainfall
from land_water_guard import classify_location
st.set_page_config(page_title='Space on Earth', page_icon='🌍', layout='wide')
st.markdown("""
<style>
/* Move the login hero down */
div[data-testid="stMainBlockContainer"] {
    padding-top: 4.5rem !important;
}

/* Hide decorative star in the login hero */
.login-hero::before,
.login-hero::after,
.hero-star,
.hero-sparkle {
    display: none !important;
}

/* Keep the top of the hero visible */
.login-hero {
    margin-top: 1.5rem !important;
}
</style>
""", unsafe_allow_html=True)

from country_language import render_country_selector
render_country_selector()
# Present a visual welcome screen only to signed-out users.
if st.session_state.get('access_mode') is None:
    from login_visual import render_login_visual
    render_login_visual()
require_access()
# Main title and concise farmer-first content are rendered by dashboard_ui.
if 'selected_location' not in st.session_state:
    st.session_state.selected_location = None
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'last_map_click' not in st.session_state:
    st.session_state.last_map_click = None

from farmer_dashboard import render_farmer_dashboard
from dashboard_ui import render_dashboard

def water_status_message(status, reason):
    """Return the English message key; translate only when drawing the warning.

    A language change must never leave an old translated message in session state.
    """
    if status == 'water':
        return 'This point appears to be in a sea, lake, or other water body. Please select a land location for your farm.'
    if reason == 'coastline_uncertain':
        return 'This point is too close to a coastline to verify. Please choose a clearer inland point.'
    return 'We could not verify whether this point is on land. Check your connection and try another point.'


def select_location(latitude, longitude):
    """Check each chosen coordinate before saving it as a farm location."""
    latitude, longitude = float(latitude), float(longitude)
    status, reason = classify_location(latitude, longitude)
    if status != 'land':
        st.session_state['land_guard_message'] = water_status_message(status, reason)
        # Never continue with an old farm analysis after a new invalid click.
        st.session_state.selected_location = None
        st.session_state.analysis_result = None
        return False
    st.session_state.pop('land_guard_message', None)
    candidate = (round(latitude, 3), round(longitude, 3))
    st.session_state['land_guard_validated'] = candidate
    if candidate != st.session_state.selected_location:
        st.session_state.selected_location = candidate
        st.session_state.analysis_result = None
    return True

@st.cache_data(ttl=86400, show_spinner=False)
def geocode_location(query):
    """Resolve a place name on explicit request; no automatic search queries."""
    geocoder = Nominatim(user_agent='terrashift-nasa-farming-prototype/1.0', timeout=10)
    place = geocoder.geocode(query, exactly_one=True, language='en')
    if place is None:
        return None
    return (place.latitude, place.longitude, place.address)

@st.cache_data(ttl=86400, show_spinner=False)
def load_climate_data(latitude, longitude):
    """Fetch NASA climate records once per selected coordinate (until cache expiry)."""
    daily = get_historical_data(latitude, longitude)
    annual = annual_statistics(daily)
    comparison = climate_comparison(annual)
    return (daily, annual, comparison)

# Use the same translation engine for every country and language.
# It prioritizes the bundled offline translations, then optional free providers.
def setup_t(message):
    return t(message)

# Validate a previously saved location from an older application session.
_previous_location = st.session_state.get('selected_location')
if _previous_location and st.session_state.get('land_guard_validated') != _previous_location:
    _status, _reason = classify_location(*_previous_location)
    if _status != 'land':
        st.session_state['land_guard_message'] = water_status_message(_status, _reason)
        st.session_state.selected_location = None
        st.session_state.analysis_result = None
    else:
        st.session_state['land_guard_validated'] = _previous_location

# Display a complete dashboard only for the current analyzed farm.
_current = st.session_state.get('analysis_result')
_ready = bool(_current and _current.get('location') == st.session_state.get('selected_location'))
if _ready:
    if st.button('📍 ' + t('Change farm location / Edit farm details'), type='primary', key='change_farm_location'):
        st.session_state.analysis_result = None
        st.rerun()
    render_dashboard(load_climate_data)
    st.divider()
# Display farm setup first when there is no valid analysis.
if not _ready:
    st.markdown('''<style>
.stApp {background:radial-gradient(circle at 83% 8%,rgba(10,83,86,.20),transparent 33%),#081425;}
.soe-onboarding {border-radius:20px;padding:25px 28px;margin-bottom:16px;
  background:linear-gradient(110deg,#103b37,#113253 70%,#182344);
  border:1px solid #2f9b8d;box-shadow:0 12px 35px rgba(0,0,0,.22);}
.soe-onboarding h1 {color:#eafff4;font-size:2rem;margin:0 0 7px;}
.soe-onboarding p {color:#c7ecdf;margin:0;}
</style><div class="soe-onboarding"><h1>🌍 Space on Earth</h1>
<p>SETUP_DESCRIPTION_TOKEN</p>
</div>'''.replace('SETUP_DESCRIPTION_TOKEN', setup_t('Select your farm on the map and enter a few details to unlock your personalized dashboard.')),unsafe_allow_html=True)
    st.subheader(setup_t('1. Select a location and describe your farm'))
    location_method = st.radio(setup_t('How would you like to find your farm?'), ['Use my location', 'Search city or address', 'Select on map'], horizontal=True, index=2, format_func=setup_t)
    if location_method == 'Use my location':
        st.caption(setup_t('Use the location button below and allow location access in your browser.'))
        browser_location = streamlit_geolocation()
        if isinstance(browser_location, dict):
            lat = browser_location.get('latitude')
            lon = browser_location.get('longitude')
            if lat is not None and lon is not None:
                select_location(lat, lon)
                accuracy = browser_location.get('accuracy')
                if isinstance(accuracy, (float, int)):
                    st.caption(setup_t('Approximate location accuracy: {accuracy} m. Confirm this is your farm location.').format(accuracy=f'{accuracy:.0f}'))
        st.info(setup_t('Your current position may be different from your farm. Confirm the marker before analyzing.'))
    elif location_method == 'Search city or address':
        with st.form('location_search_form'):
            search_text = st.text_input(setup_t('Enter a city, region, or address'), placeholder='Nairobi, Kenya')
            search_submitted = st.form_submit_button(setup_t('Find location'))
        if search_submitted:
            if not search_text.strip():
                st.warning(setup_t('Enter a location to search for.'))
            else:
                try:
                    found = geocode_location(search_text.strip())
                    if found is None:
                        st.warning(setup_t('Location not found. Try a more specific place name.'))
                    else:
                        if select_location(found[0], found[1]):
                            st.success(setup_t('Location found: {location}').format(location=found[2]))
                except (GeocoderServiceError, GeocoderTimedOut) as error:
                    st.error(setup_t('Location search is temporarily unavailable. Please try again.'))
        st.caption(setup_t('Place search: © OpenStreetMap contributors (Nominatim). Search only when requested.'))
    else:
        st.caption(setup_t('Click the map to select your farm location.'))
    map_column, form_column = st.columns([3, 2], gap='large')
    with map_column:
        selected = st.session_state.selected_location
        map_center = list(selected) if selected is not None else [15, 0]
        map_zoom = 6 if selected is not None else 2
        world_map = folium.Map(location=map_center, zoom_start=map_zoom, min_zoom=2, max_zoom=12, tiles=None, control_scale=True, max_bounds=True)
        folium.TileLayer('OpenStreetMap', no_wrap=True).add_to(world_map)
        if st.session_state.selected_location is not None:
            folium.Marker(location=list(st.session_state.selected_location), tooltip='Selected farm location').add_to(world_map)
        map_result = st_folium(world_map, height=480, width=None, returned_objects=['last_clicked'], key=f'terrashift_world_map_{st.session_state.selected_location}')
        clicked = map_result.get('last_clicked') if map_result else None
        if clicked and location_method == 'Select on map':
            candidate = (round(clicked['lat'], 3), round(clicked['lng'], 3))
            if candidate != st.session_state.last_map_click:
                st.session_state.last_map_click = candidate
                select_location(*candidate)
        location = st.session_state.selected_location
        if st.session_state.get('land_guard_message'):
            st.warning(setup_t(st.session_state['land_guard_message']))
        if location is None:
            st.info(setup_t('Click anywhere on the world map to select a location.'))
        else:
            st.success(setup_t('Selected location: {lat}, {lon}').format(lat=f'{location[0]:.3f}', lon=f'{location[1]:.3f}'))
    with form_column:
        st.markdown('#### ' + setup_t('Farmer information'))
        has_soil_ph = st.checkbox(setup_t('I have a measured soil pH value'), key='has_soil_ph')
        soil_ph = None
        if has_soil_ph:
            soil_ph = st.number_input(setup_t('Soil pH (from a soil test)'), min_value=0.0, max_value=14.0, value=6.5, step=0.1, key='measured_soil_ph', help=setup_t('Enter your measured soil pH.'))
        with st.form('farmer_inputs'):
            previous_crop = st.selectbox(setup_t('What did you grow last season?'), list(CROPS.keys()), format_func=setup_t)
            soil_type = st.selectbox(setup_t('What is your soil type?'), SOIL_OPTIONS, format_func=setup_t)
            season_month = st.selectbox(setup_t('When does the growing season start?'), list(range(1, 13)), index=2, format_func=lambda m: setup_t(__import__('calendar').month_name[m]))
            season_length = st.selectbox(setup_t('How many months does the season last?'), [3, 4, 5, 6], format_func=setup_t)
            priority = st.radio(setup_t('What is your priority?'), ['Water conservation', 'Soil health'], format_func=setup_t)
            submitted = st.form_submit_button(setup_t('Analyze farm scenarios'), type='primary', use_container_width=True)
        st.caption(setup_t('Soil texture is farmer-reported, not measured by NASA POWER. USDA texture classes are available; choose Unknown / Not tested if unsure. New texture classes receive a neutral prototype soil score until crop-specific evidence is available.'))
    if submitted:
        if location is None:
            st.warning(t('Select a location on the map before analyzing scenarios.'))
        else:
            _status, _reason = classify_location(*location)
            if _status != 'land':
                st.session_state['land_guard_message'] = water_status_message(_status, _reason)
                st.session_state.selected_location = None
                st.session_state.analysis_result = None
                st.warning(setup_t(st.session_state['land_guard_message']))
                st.stop()
            try:
                with st.spinner(t('Retrieving and checking NASA POWER climate records...')):
                    daily, annual, comparison = load_climate_data(*location)
                    seasonal = seasonal_comparison(daily, season_month, season_length)
                st.session_state.analysis_result = {'location': location, 'annual': annual, 'seasonal': seasonal, 'season_month': season_month, 'season_length': season_length, 'comparison': comparison, 'previous_crop': previous_crop, 'soil_type': soil_type, 'soil_ph': float(soil_ph) if has_soil_ph else None, 'priority': priority}
                st.rerun()  # Show the fresh farmer summary at the top immediately.
            except Exception as error:
                st.session_state.analysis_result = None
                st.error(setup_t('Climate analysis failed. Please try again.'))
result = st.session_state.analysis_result
if result is None:
    st.info(setup_t('Select a location, enter farm information, and choose Analyze farm scenarios.'))
    st.stop()
if result['location'] != st.session_state.selected_location:
    st.warning(setup_t('The location has changed. Analyze again to update the results.'))
    st.stop()
# The dashboard is rendered at the top on the next rerun after analysis.
st.divider()
with st.expander('🗂️ ' + t('Farm journal and planting planner'), expanded=False):
    render_farmer_dashboard(load_climate_data)
st.divider()
with st.expander(t('Advanced analysis — NASA, soil, crop rotation and irrigation'), expanded=False):
    annual = result['annual']
    comparison = result['comparison']
    st.divider()
    st.subheader(numbered_section(1, t('2. Historical climate comparison')))
    st.caption(t('Historical mean temperature and rainfall are not forecasts.') + ' · 2001–2020 / 2021–2025')
    metric_left, metric_right = st.columns(2)
    metric_left.metric(t('Mean temperature difference'), f"{comparison['temperature_difference']:+.2f} °C")
    metric_right.metric(t('Annual precipitation difference'), f"{comparison['precipitation_difference_pct']:+.1f}%")
    chart_data = annual.reset_index().copy()
    chart_data['Sequence'] = range(1, len(chart_data) + 1)
    st.caption(t('Chart order: 1, 2, 3... Hover to see each year.'))
    temp_column, rain_column = st.columns(2, gap='large')
    with temp_column:
        st.markdown(t('**Annual mean temperature**'))
        temperature_chart = px.line(
            chart_data,
            x='Sequence',
            y='Temperature',
            markers=True,
            labels={'Sequence': t('Order'), 'Temperature': t('Temperature (°C)')},
            custom_data=['Year']
        )
        temperature_chart.update_traces(hovertemplate=f"{t('Order')} %{{x}}<br>{t('Year')} %{{customdata[0]}}<br>{t('Temperature')} %{{y:.2f}} °C<extra></extra>")
        temperature_chart.update_xaxes(tickmode='linear', tick0=1, dtick=1)
        temperature_chart.update_layout(margin=dict(l=5, r=5, t=15, b=5))
        st.plotly_chart(temperature_chart, use_container_width=True)
    with rain_column:
        st.markdown(t('**Annual total precipitation**'))
        precipitation_chart = px.bar(
            chart_data,
            x='Sequence',
            y='Precipitation',
            labels={'Sequence': t('Order'), 'Precipitation': t('Precipitation (mm)')},
            custom_data=['Year']
        )
        precipitation_chart.update_traces(hovertemplate=f"{t('Order')} %{{x}}<br>{t('Year')} %{{customdata[0]}}<br>{t('Precipitation')} %{{y:.0f}} mm<extra></extra>")
        precipitation_chart.update_xaxes(tickmode='linear', tick0=1, dtick=1)
        precipitation_chart.update_layout(margin=dict(l=5, r=5, t=15, b=5))
        st.plotly_chart(precipitation_chart, use_container_width=True)
    st.subheader(numbered_section(2, t('3. Growing season climate context')))
    seasonal = result['seasonal']
    st.caption(f"{t('Selected calendar window:')} {t('month')} {result['season_month']}, {t('duration')} {result['season_length']} {t('months')}. {t('Historical observations, not a seasonal forecast.')}")
    season_left, season_right = st.columns(2)
    season_left.metric(t('Recent seasonal mean temperature'), f"{seasonal['recent_temperature']:.1f} °C", delta=f"{seasonal['recent_temperature'] - seasonal['baseline_temperature']:+.1f} °C {t('vs reference')}")
    season_right.metric(t('Recent seasonal precipitation'), f"{seasonal['recent_precipitation']:.0f} mm", delta=f"{seasonal['recent_precipitation'] - seasonal['baseline_precipitation']:+.0f} mm {t('vs reference')}")
    from soil_panel import render_soil_panel
    render_soil_panel(st.session_state.get('selected_location'))
    from irrigation_timing_panel import render_irrigation_timing_panel
    render_irrigation_timing_panel(st.session_state.analysis_result, load_climate_data)

# References are shown after all analysis panels in the selected UI language.
from references_footer import render_references_footer
render_references_footer()
