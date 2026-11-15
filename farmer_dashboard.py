"""Farmer-first, simple overview; existing scientific charts remain below."""
from datetime import date
import pandas as pd
import streamlit as st
from i18n import t, local_date
from display_localization import localize_table, FORECAST_STATUSES
from farmer_forecast import (get_16_day_forecast, screening_months,
                             crop_cycle_window, forecast_monitoring_table)
from community_farms import (save_planting, my_plantings, nearby_crop_totals,
                             update_share, delete_record)

KNOWN_CROPS = ['Beans', 'Maize', 'Wheat', 'Sorghum']


@st.cache_data(ttl=3 * 3600, show_spinner=False)
def cached_forecast(lat, lon):
    return get_16_day_forecast(lat, lon)


def render_farmer_dashboard(load_climate_data):
    """Place immediately below title, before the existing map and long charts."""
    st.subheader(t('Your farm at a glance'))
    st.caption(t('A simple plan first. Detailed NASA research charts are farther down.'))
    result = st.session_state.get('analysis_result')
    location = st.session_state.get('selected_location')
    previous = result.get('previous_crop') if result else None
    if 'dashboard_crop' not in st.session_state:
        st.session_state.dashboard_crop = 'Beans'
    with st.container(border=True):
        a, b = st.columns([2, 1])
        with a:
            crop = st.selectbox(t('Crop to plan'), KNOWN_CROPS,
                                key='dashboard_crop', format_func=t)
        with b:
            sowing = st.date_input(t('Your planned or actual sowing date'),
                                   value=date.today(), key='dashboard_sowing')
        if not location:
            st.info(t('First select your farm on the map below and run Analyze farm scenarios.'))
            return
        st.caption(f"{t('Selected farm')}: {location[0]:.3f}, {location[1]:.3f}")
        current = date.today()
        if result and result.get('location') == location:
            try:
                daily, _, _ = load_climate_data(*location)
                windows = screening_months(daily, crop, from_date=current)
            except Exception:
                windows = []
        else:
            windows = []
        cycle = crop_cycle_window(crop, sowing)
        pcol, icol, hcol = st.columns(3)
        with pcol:
            st.markdown('#### 🌱 ' + t('Planting'))
            st.write(', '.join(f"{t(__import__('calendar').month_name[x['month']])} {x['year']}" for x in windows[:3]) if windows else t('Analyze this farm to see candidate months.'))
            st.caption(t('Historical temperature screening only; NOT a 2026/2027 planting forecast. Soil, variety and local advice still matter.'))
        with icol:
            st.markdown('#### 💧 ' + t('Irrigation'))
            st.write(t('See the 16-day rain outlook below.'))
            st.caption(t('Check actual soil moisture before watering; no exact watering dates or amounts are calculated.'))
        with hcol:
            st.markdown('#### 🌾 ' + t('Harvest'))
            if cycle:
                st.write(f"{local_date(cycle['earliest'])} – {local_date(cycle['latest'])}")
            st.caption(t('Broad FAO crop-cycle range based on your sowing date; NOT a harvest prediction.'))
        if st.button(t('Show 16-day weather outlook'), key='load_farmer_forecast'):
            try:
                with st.spinner(t('Loading short-range weather forecast...')):
                    st.session_state['farmer_forecast'] = cached_forecast(*location)
                    st.session_state['farmer_forecast_coords'] = location
            except Exception as ex:
                st.session_state.pop('farmer_forecast', None)
                st.warning(t('Forecast temporarily unavailable. Historical data is not substituted for a forecast.'))
        forecast = st.session_state.get('farmer_forecast')
        if forecast is not None and st.session_state.get('farmer_forecast_coords') == location:
            st.markdown('#### ' + t('Next 16 days — weather forecast'))
            st.caption(t('The forecast is not an irrigation prescription.'))
            chart = forecast.set_index('Date')[['Rain (mm)', 'Reference ET0 (mm)']]
            st.line_chart(chart)
            view = forecast_monitoring_table(forecast)
            st.dataframe(localize_table(view[['Date','Rain (mm)','Rain chance (%)','Reference ET0 (mm)','Field check']], known_statuses=FORECAST_STATUSES),
                         hide_index=True, use_container_width=True)
            st.caption(t('ET0 is reference evapotranspiration, not crop-specific water demand.'))

    st.divider()
    st.subheader(t('Your crop journal & nearby planting trends'))
    st.caption(t('Your entries are private unless you explicitly share crop information. Nearby results are aggregate only.'))
    email = st.session_state.get('user_email') if st.session_state.get('access_mode') == 'account' else None
    if location:
        with st.expander(t('Add a planting or field activity'), expanded=False):
            if not email:
                st.info(t('Sign in with a demo account to save your field journal. Guest entries are not saved.'))
            with st.form('farmer_journal_form'):
                custom_crop = st.text_input(t('Crop name (you can enter any crop)'), value=crop,
                                            max_chars=80)
                planted = st.date_input(t('Sowing date'), value=sowing)
                harvested = st.date_input(t('Expected/actual harvest date (optional)'), value=None)
                watered = st.date_input(t('Last irrigation date (optional)'), value=None)
                method = st.selectbox(t('Irrigation method'), ['Unknown','Drip','Sprinkler / overhead','Other'], format_func=t)
                notes = st.text_area(t('Private field notes'), max_chars=500)
                share = st.checkbox(t('Allow anonymous crop statistics to be shown to other farmers'), value=False)
                submitted = st.form_submit_button(t('Save my farm activity'), disabled=not bool(email))
            if submitted and email:
                try:
                    save_planting(email, custom_crop, planted, *location,
                                  harvest_date=harvested, irrigation_date=watered,
                                  irrigation_method=method, farmer_notes=notes,
                                  share_crop=share)
                    st.success(t('Saved. You can change sharing or delete this record below.'))
                except Exception as ex:
                    st.error(str(ex))
    else:
        st.info(t('Select the farm location on the map to record activities.'))
    if email:
        records = my_plantings(email)
        if records:
            with st.expander(t('My saved activities'), expanded=False):
                st.dataframe(localize_table(pd.DataFrame(records)), hide_index=True, use_container_width=True)
                record = st.selectbox(t('Record to manage'), [r['id'] for r in records])
                c1,c2,c3 = st.columns(3)
                if c1.button(t('Share crop only'), key='share_record'):
                    update_share(email, record, True)
                    st.rerun()
                if c2.button(t('Keep private'), key='private_record'):
                    update_share(email, record, False)
                    st.rerun()
                if c3.button(t('Delete'), key='delete_record'):
                    delete_record(email, record)
                    st.rerun()
    if location:
        st.markdown('#### ' + t('What crops are grown nearby?'))
        counts = nearby_crop_totals(*location)
        if counts:
            st.dataframe(localize_table(pd.DataFrame(counts)), hide_index=True, use_container_width=True)
        else:
            st.info(t('No anonymous totals available yet. At least 3 different consenting farms growing the same crop are needed within approximately 5 km.'))
        st.caption(t('No farmer name, exact farm coordinates or private notes are shown. Local demo database: records are shared only among users on the SAME running app/server.'))
