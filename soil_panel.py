"""Read-only SoilGrids soil pH panel for Space on Earth."""
from i18n import t
import streamlit as st
from section_numbering import numbered_section
from soil_wcs import lookup_soil_ph

def get_coordinates(location):
    if isinstance(location, dict):
        latitude = location.get('lat', location.get('latitude'))
        longitude = location.get('lng', location.get('lon', location.get('longitude')))
    elif isinstance(location, (tuple, list)) and len(location) >= 2:
        latitude, longitude = location[:2]
    else:
        return None
    try:
        latitude, longitude = (float(latitude), float(longitude))
    except (TypeError, ValueError):
        return None
    if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
        return None
    return (latitude, longitude)

def render_soil_panel(location):
    st.divider()
    st.header(numbered_section(3, t('5. Location-Specific Soil Analysis')))
    coordinates = get_coordinates(location)
    if coordinates is None:
        st.info(t('Select a location to explore soil information.'))
        return
    latitude, longitude = coordinates
    st.write(f"{t('Selected coordinates:')} {latitude:.4f}, {longitude:.4f}")
    st.caption(t('SoilGrids provides model estimates, not field measurements.'))
    location_key = (round(latitude, 4), round(longitude, 4))
    if st.button(t('Check soil data'), key='check_soil_wcs'):
        with st.spinner(t('Retrieving SoilGrids data...')):
            result = lookup_soil_ph(latitude, longitude)
        st.session_state['soil_lookup_result'] = result
        st.session_state['soil_lookup_location'] = location_key
    result = st.session_state.get('soil_lookup_result')
    saved_location = st.session_state.get('soil_lookup_location')
    if result is None or saved_location != location_key:
        st.info(t('Click Check soil data to request an estimate.'))
        return
    if result['status'] == 'available':
        st.metric(t('Estimated topsoil pH (0-5 cm)'), result['ph'])
        st.caption(t('Source: ISRIC SoilGrids WCS | selected map grid cell'))
        st.warning(result['note'])
    elif result['status'] == 'nearby':
        st.metric(t('Nearby grid-cell estimated pH (0-5 cm)'), result['ph'])
        st.warning(result['note'])
        st.caption(t('Source: ISRIC SoilGrids WCS | nearby, not exact-point data'))
    else:
        st.warning(t('Soil data is unavailable for this location. No soil pH value was assumed.'))
        if result.get('reason'):
            st.caption(result['reason'])
    st.caption(t('These estimates are informational only and do not change crop scores.'))
