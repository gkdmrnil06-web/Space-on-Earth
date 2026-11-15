"""Streamlit view for historical seasonal precipitation exposure."""
from i18n import t
import streamlit as st
from water_exposure import calculate_water_exposure

def render_water_exposure_panel(analysis_result, load_climate_data):
    """Display same-location two-season rainfall context; leave crop scores intact."""
    st.divider()
    st.subheader(t('7. Seasonal Water Exposure Indicator'))
    st.caption(t('NASA POWER historical precipitation, comparing the same calendar windows in 2021–2025 with 2001–2020. This is a relative rainfall indicator, not a crop water requirement or a drought forecast.'))
    if analysis_result is None:
        st.info(t('Analyze a farm scenario first.'))
        return
    location = analysis_result['location']
    start_month = analysis_result['season_month']
    duration = analysis_result['season_length']
    signature = (location, start_month, duration)
    if st.button(t('Compare historical rainfall exposure'), key='run_water_exposure'):
        try:
            with st.spinner('Comparing complete historical rainfall windows...'):
                daily, _, _ = load_climate_data(*location)
                rows = calculate_water_exposure(daily, start_month, duration)
            st.session_state['water_exposure_output'] = rows
            st.session_state['water_exposure_signature'] = signature
        except Exception as error:
            st.session_state.pop('water_exposure_output', None)
            st.session_state.pop('water_exposure_signature', None)
            st.error(f'Historical rainfall comparison could not be completed: {error}')
            return
    if st.session_state.get('water_exposure_signature') != signature:
        st.info(t('Click Compare historical rainfall exposure to see these two growing windows.'))
        return
    output = st.session_state.get('water_exposure_output')
    if not output:
        st.info(t('No rainfall comparison available.'))
        return
    for item in output:
        with st.container(border=True):
            st.markdown(f"**Season {item['season_number']} — {'–'.join(item['month_names'])}**")
            a, b, c = st.columns(3)
            a.metric('2001–2020 mean rainfall', f"{item['baseline_mean_mm']:.0f} mm")
            b.metric('2021–2025 mean rainfall', f"{item['recent_mean_mm']:.0f} mm", delta=f"{item['difference_pct']:+.1f}% vs reference", delta_color='off')
            c.metric('Relative rainfall index', f"{item['relative_index']:.2f}×")
            st.write(f"**{item['label']}**")
            st.caption(f"Complete windows: {item['baseline_years']} reference years and {item['recent_years']} recent years. Labels use illustrative thresholds: below 0.80×, 0.80–1.20×, above 1.20×.")
            with st.expander(t('View annual seasonal precipitation totals')):
                st.bar_chart(item['series'].set_index('Year')[['Precipitation']])
    st.warning(t('Less rainfall does not by itself establish crop water stress, groundwater availability, soil moisture, crop-specific water demand or irrigation needs. The index does not affect crop-rotation scores. No future rainfall is predicted.'))
