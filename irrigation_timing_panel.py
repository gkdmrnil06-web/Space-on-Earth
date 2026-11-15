"""Streamlit UI for research-only irrigation timing exploration."""
from i18n import t
from display_localization import localize_table, MONITOR_STATUSES
import pandas as pd
import streamlit as st
from section_numbering import numbered_section
from crop_rotation import CROPS
from irrigation_timing import monthly_irrigation_context

def render_irrigation_timing_panel(analysis_result, load_climate_data):
    st.divider()
    st.subheader(numbered_section(4, t('8. Irrigation Timing Analysis')))
    st.caption(t('Explore months when dry-day frequency suggests closer soil-moisture checks. NASA POWER historical daily rainfall and mean temperature (2021–2025); these are NOT forecasts or an irrigation schedule.'))
    if analysis_result is None:
        st.info(t('Analyze a farm scenario first.'))
        return
    location = analysis_result['location']
    month = analysis_result['season_month']
    duration = analysis_result['season_length']
    previous = analysis_result['previous_crop']
    options = [name for name in CROPS if name != previous]
    crop = st.selectbox(t('Crop to explore for the next growing window'), options, key='irrigation_selected_crop', help=t('Used to label the scenario only. Crop-specific irrigation needs are not estimated.'), format_func=t)
    method = st.selectbox(t('Irrigation method'), ['Unknown', 'Sprinkler / overhead', 'Drip'], key='irrigation_method', format_func=t)
    signature = (tuple(location), month, duration)
    if st.button(t('Analyze irrigation timing context'), key='irrigation_analyze'):
        try:
            with st.spinner(t('Summarizing historical monthly climate data...')):
                daily, _, _ = load_climate_data(*location)
                table = monthly_irrigation_context(daily, month, duration)
            st.session_state['irrigation_timing_output'] = table
            st.session_state['irrigation_timing_signature'] = signature
        except Exception as error:
            st.session_state.pop('irrigation_timing_output', None)
            st.session_state.pop('irrigation_timing_signature', None)
            st.error(t('Irrigation timing analysis unavailable.') + ' ' + str(error))
            return
    if st.session_state.get('irrigation_timing_signature') != signature:
        st.info(t('Click Analyze irrigation timing context to view your selected growing window.'))
        return
    data = st.session_state.get('irrigation_timing_output')
    if not data:
        st.info(t('No complete monthly climate data are available.'))
        return
    st.write(f'**{t("Selected crop scenario:")}** {t(crop)} · **{t("Location:")}** {location[0]:.3f}, {location[1]:.3f}')
    st.caption(t('Dry day means daily precipitation below 1 mm (illustrative threshold). Higher dry-day frequency means a month deserves closer monitoring, NOT that irrigation is automatically necessary.'))
    frame = pd.DataFrame(data)
    chart_frame = frame.set_index('month')
    left, right = st.columns(2)
    with left:
        st.markdown(t('**Historical mean monthly rainfall (mm)**'))
        st.bar_chart(chart_frame[['rainfall_mm']], y_label=t('Precipitation (mm)'))
    with right:
        st.markdown(t('**Historical share of dry days (%)**'))
        st.bar_chart(chart_frame[['dry_day_percent']], y_label=t('Dry days (%)'))
    st.markdown(t('**Monthly monitoring table**'))
    view = frame.rename(columns={'month_full': 'Month', 'rainfall_mm': 'Mean rainfall (mm)', 'temperature_c': 'Mean temperature (°C)', 'dry_day_percent': 'Dry days (%)', 'attention': 'Monitoring context', 'valid_years': 'Years used'})[['Month', 'Mean rainfall (mm)', 'Mean temperature (°C)', 'Dry days (%)', 'Monitoring context', 'Years used']]
    st.dataframe(localize_table(view, known_statuses=MONITOR_STATUSES, localize_months=True), hide_index=True, use_container_width=True)
    watch = max(data, key=lambda item: item['dry_day_percent'])
    st.info(f"**{t('Month to monitor most closely:')}** {t(watch['month_full'])} "
            f"({watch['dry_day_percent']:.1f}%). " + t('Check actual soil moisture before watering. No exact irrigation dates or volumes are calculated.'))
    st.markdown('**' + t('Time-of-day guidance') + '**')
    st.write(t('If you use sprinklers, early morning often works well. For drip irrigation, soil moisture matters more than the hour.'))
    with st.expander(t('Data quality and limitations')):
        st.write(t('Mean rainfall and dry-day frequency are historical indicators, not irrigation instructions.'))
        st.write('NASA POWER · FAO irrigation guidance')
