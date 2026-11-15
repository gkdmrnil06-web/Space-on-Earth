"""Space on Earth farmer dashboard presentation.

All numeric indicators come from user inputs or named data sources. Missing
soil moisture, fire risk, yield, and profitability are never fabricated.
"""
from datetime import date
from html import escape

import folium
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from streamlit_folium import st_folium

from crop_rotation import CROPS, compare_strategies, recent_annual_rainfall
from farmer_forecast import crop_cycle_window, candidate_harvest_window, screening_months, get_16_day_forecast, forecast_monitoring_table
from community_farms import nearby_crop_totals
from i18n import t, local_date
from ui_translate import (ui_markdown, ui_caption, ui_info, ui_warning, ui_toggle, ui_button, ui_metric, ui_expander, ui_spinner, ui_text)
from nasa_conditions import get_nasa_conditions
from input_guidance_panel import render_input_guidance_panel
from display_localization import localize_table, FORECAST_STATUSES


def _style():
    ui_markdown('''<style>
    .stApp {background:radial-gradient(circle at 80% 0%,#10354a 0%,#081425 43%);color:#e9f3ff;}
    [data-testid="stSidebar"] {background:linear-gradient(180deg,#102c42 0%,#091a2c 70%,#081425 100%);}
    [data-testid="stSidebar"] button {border-radius:10px;}
    .soe-head {box-shadow:0 14px 35px rgba(0,0,0,.24),inset 0 3px 0 #31ce96;}
    .soe-label,.soe-header {letter-spacing:.2px;}
    div[data-testid="stVerticalBlockBorderWrapper"] > div {box-shadow:0 6px 22px rgba(0,0,0,.12);}
    .soe-stat {border-left:3px solid #41b6ef!important;}
    .soe-row {transition:filter .18s, transform .18s;}
    .soe-row:hover {filter:brightness(1.16);transform:translateY(-1px);}
    .soe-alert {box-shadow:0 0 22px rgba(234,63,69,.17),inset 5px 0 #fa6e6e;}
    div[data-testid="stVerticalBlockBorderWrapper"] > div {border-radius: 15px;}
    .soe-head {margin: 0 0 12px; padding: 22px 24px; border: 1px solid #3a93a9;
      border-radius: 15px; background:linear-gradient(120deg,#113e50,#142b48 70%,#1b2b4c);}
    .soe-head h1 {font-size:2rem;margin:0;color:#f2f7ff;}
    .soe-head p {margin:5px 0 0;color:#a6c0ce;}
    .soe-label {font-size:1.14rem;font-weight:750;margin:0 0 11px;}
    .soe-summary {background:linear-gradient(125deg,#145536,#103b31);
      border:1px solid #2a8759; border-radius:14px;padding:16px 18px;min-height:155px;}
    .soe-summary p {margin:8px 0;font-size:.92rem;}
    .soe-stat {background:#102337;border:1px solid #26445f;border-radius:12px;
      padding:11px 13px;margin:7px 0;font-size:.92rem;}
    .soe-stat strong {float:right;}
    .soe-row {display:grid; grid-template-columns: 1.0fr .8fr .9fr .9fr 1.1fr 1.1fr 1.4fr;
      gap:10px;align-items:center;padding:13px 14px;margin:5px 0;
      border-radius:11px;font-size:.82rem;font-weight:550;}
    .soe-row.rank-1 {background:#087F4B;border:1px solid #087F4B;box-shadow:inset 4px 0 rgba(255,255,255,.25);color:#fff;font-weight:650;min-height:49px;}
    .soe-row.rank-2 {background:#329344;border:1px solid #329344;box-shadow:inset 4px 0 rgba(255,255,255,.25);color:#fff;font-weight:650;min-height:49px;}
    .soe-row.rank-3 {background:#67A338;border:1px solid #67A338;box-shadow:inset 4px 0 rgba(255,255,255,.25);color:#fff;font-weight:650;min-height:49px;}
    .soe-row.rank-4 {background:#9BAC2B;border:1px solid #9BAC2B;box-shadow:inset 4px 0 rgba(255,255,255,.25);color:#fff;font-weight:650;min-height:49px;}
    .soe-row.rank-5 {background:#B5A51F;border:1px solid #B5A51F;box-shadow:inset 4px 0 rgba(255,255,255,.25);color:#fff;font-weight:650;min-height:49px;}
    .soe-row.rank-6 {background:#C39A18;border:1px solid #C39A18;box-shadow:inset 4px 0 rgba(255,255,255,.25);color:#fff;font-weight:650;min-height:49px;}
    .soe-row.rank-7 {background:#CD8A17;border:1px solid #CD8A17;box-shadow:inset 4px 0 rgba(255,255,255,.25);color:#fff;font-weight:650;min-height:49px;}
    .soe-row.rank-8 {background:#D57819;border:1px solid #D57819;box-shadow:inset 4px 0 rgba(255,255,255,.25);color:#fff;font-weight:650;min-height:49px;}
    .soe-row.rank-9 {background:#D3681C;border:1px solid #D3681C;box-shadow:inset 4px 0 rgba(255,255,255,.25);color:#fff;font-weight:650;min-height:49px;}
    .soe-row.rank-10 {background:#C95321;border:1px solid #C95321;box-shadow:inset 4px 0 rgba(255,255,255,.25);color:#fff;font-weight:650;min-height:49px;}
    .soe-row.rank-11 {background:#BC4028;border:1px solid #BC4028;box-shadow:inset 4px 0 rgba(255,255,255,.25);color:#fff;font-weight:650;min-height:49px;}
    .soe-row.rank-12 {background:#AE3034;border:1px solid #AE3034;box-shadow:inset 4px 0 rgba(255,255,255,.25);color:#fff;font-weight:650;min-height:49px;}
    .soe-row.rank-13 {background:#97253B;border:1px solid #97253B;box-shadow:inset 4px 0 rgba(255,255,255,.25);color:#fff;font-weight:650;min-height:49px;}
    .soe-row[class*="rank-"] span {color:#fff;}
    .soe-preview-label {color:#9cb6cb;font-size:.80rem;margin:0 0 8px;}
    .soe-summary {box-shadow:inset 5px 0 #27d27d;}
    .soe-header {color:#a8c4d9;font-size:.77rem;background:#102238;font-weight:700;}
    .soe-alert {padding:17px 20px;border-radius:13px;
      border:1px solid #ba5157;background:linear-gradient(90deg,#4a1926,#291b2b);}
    .soe-neutral {border:1px solid #36546b;background:#13283c;padding:15px 18px;border-radius:13px;}
    @media(max-width:700px){.soe-row {grid-template-columns: 1fr 1fr;font-size:.8rem;}}
    </style>''', unsafe_allow_html=True)


def _priority_benefit(crop_name, previous_crop, priority):
    """Qualitative, non-measured rotation/water labels; not an outcome estimate."""
    crop = CROPS[crop_name]
    if priority == 'Water conservation':
        return ui_text({'low': 'Lower water need*', 'medium': 'Moderate water need*',
                'high': 'Higher water need*'}[crop['water']])
    if crop['family'] == 'perennial':
        return ui_text('Perennial orchard; assess separately*')
    previous_family = CROPS[previous_crop]['family']
    if crop_name == previous_crop:
        return ui_text('Repeat crop; rotation caution')
    if crop['family'] == 'legume':
        return ui_text('Nitrogen fixation potential*' if previous_family != 'legume' else 'Legume after legume; assess rotation')
    if crop['family'] != previous_family:
        return ui_text('Crop-family diversity potential*')
    return ui_text('Same crop family; limited rotation*')


def _safe(value):
    return escape(str(value), quote=True)


def _crop_rows(result):
    if not result:
        return []
    ranked = compare_strategies(
        result['previous_crop'], result['soil_type'], result['seasonal'],
        soil_ph=result.get('soil_ph'), annual_rainfall_mm=recent_annual_rainfall(result.get('annual')))[result['priority']]
    return ranked


def _plot_annual(annual):
    data = annual.reset_index()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['Year'], y=data['Temperature'], mode='lines+markers',
                             line=dict(color='#61b7fa', width=2), name=t('Annual mean temperature')))
    fig.update_layout(template='plotly_dark', height=235, margin=dict(l=4,r=4,t=8,b=3),
                      paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',
                      xaxis_title=None,yaxis_title=t('Temperature (°C)'),showlegend=False)
    return fig


def _forecast_plot(frame):
    fig = go.Figure()
    fig.add_trace(go.Bar(x=frame['Date'], y=frame['Rain (mm)'], name=t('Forecast rainfall (mm)'),
                         marker_color='#51a8f3'))
    fig.update_layout(template='plotly_dark',height=230,margin=dict(l=4,r=4,t=8,b=3),
                      paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',
                      yaxis_title='mm')
    return fig


@st.cache_data(ttl=10800, show_spinner=False)
def _get_weather(lat, lon):
    return get_16_day_forecast(lat, lon)


def render_dashboard(load_climate_data):
    _style()
    ui_markdown('<div class="soe-head"><h1>🌍 Space on Earth · Farm Dashboard</h1>'
                '<p>NASA-powered climate context · A simple overview before detailed analysis</p></div>',
                unsafe_allow_html=True)
    location = st.session_state.get('selected_location')
    result = st.session_state.get('analysis_result')
    if result and result.get('location') != location:
        result = None
    if location:
        ui_caption(f"📍 {_safe(location[0])}, {_safe(location[1])} · Farm position selected on the map")
    else:
        ui_info('Select your farm location in the Farm setup section below, then analyze it.')

    if result:
        change = result['comparison'].get('temperature_difference')
        if pd.notna(change) and change >= 1.0:
            ui_markdown('<div class="soe-neutral">ℹ️ <b>Climate context:</b> Historical mean temperature '
                        f'rose {_safe(f"{change:+.2f}")} °C relative to 2001–2020. '
                        'Review crop and irrigation plans. This is NOT a current fire warning. '
                        'No verified live alert is connected.</div>',
                        unsafe_allow_html=True)
        else:
            ui_markdown('<div class="soe-neutral">ℹ️ <b>Alerts:</b> No verified live fire, flood or '
                        'extreme-weather alert is connected. Check official local warnings.</div>',
                        unsafe_allow_html=True)
    else:
        ui_markdown('<div class="soe-neutral">ℹ️ <b>Alerts:</b> No farm-specific alert has been '
                    'evaluated. Do not interpret this as an all-clear.</div>', unsafe_allow_html=True)

    map_col, facts_col, action_col = st.columns([1.5, 1.05, 1.05], gap='medium')
    with map_col:
        with st.container(border=True):
            ui_markdown('#### 🗺️ Farm Map')
            satellite = ui_toggle('Satellite imagery', value=False, key='dashboard_satellite')
            selected = location or (15, 0)
            farm_map = folium.Map(location=list(selected), zoom_start=10 if location else 2,
                                  tiles=None, control_scale=True)
            if satellite:
                folium.TileLayer(
                    tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                    attr='Tiles © Esri and contributors', name='Satellite imagery').add_to(farm_map)
            else:
                folium.TileLayer('OpenStreetMap').add_to(farm_map)
            if location:
                folium.Marker(list(location), tooltip='Selected location (not a verified farm boundary)').add_to(farm_map)
            st_folium(farm_map, height=290, width=None, returned_objects=[], key='soe_overview_map')
            ui_caption(t('Marker only · Farm boundaries have not been verified.'))
    # Only fetch conditions after an analysis for the selected location.
    nasa_conditions = None
    if result and location:
        with ui_spinner('Loading NASA soil and weather conditions...'):
            nasa_conditions = get_nasa_conditions(*location)
    moisture = nasa_conditions.get('moisture') if nasa_conditions else None
    fire = nasa_conditions.get('fire') if nasa_conditions else None
    wetness = nasa_conditions.get('soil_wetness') if nasa_conditions else None
    if moisture:
        moisture_label = (f"{moisture['volumetric_pct']:.1f}% (volume)" +
                          (" · historical" if moisture.get('is_historical') else ""))
    elif wetness:
        # NASA GWETTOP is relative surface wetness, NOT volumetric soil moisture.
        moisture_label = f"{t('Soil wetness')} {wetness['fraction']:.2f} (0–1)" + (" · historical" if wetness.get('is_historical') else "")
    else:
        moisture_label = {
            "network_error": "NASA soil endpoint unreachable",
            "missing": "No valid NASA soil reading",
        }.get(nasa_conditions.get("moisture_status") if nasa_conditions else None,
              "Soil reading unavailable")

    fire_label = (f"{fire['level']} (screening)" if fire else 'NASA data unavailable')

    with facts_col:
        with st.container(border=True):
            ui_markdown('#### 🌿 Farm Summary')
            facts = [
                ('📍 Coordinates', f'{location[0]:.3f}, {location[1]:.3f}' if location else 'Not selected'),
                ('💧 Soil moisture', moisture_label),
                ('🔥 Fire risk', fire_label),
                ('🌡️ Seasonal mean temp', f"{result['seasonal']['recent_temperature']:.1f} °C" if result else 'Run analysis'),
                ('🌧️ Seasonal rainfall', f"{result['seasonal']['recent_precipitation']:.0f} mm" if result else 'Run analysis'),
                ('🧪 Soil pH', f"{result['soil_ph']:.1f} (farmer-reported)" if result and result.get('soil_ph') is not None else 'Not provided'),
            ]
            for name, val in facts:
                ui_markdown(f'<div class="soe-stat">{_safe(ui_text(name))}<strong>{_safe(ui_text(val))}</strong></div>', unsafe_allow_html=True)
            if moisture:
                ui_caption(f"Soil moisture: NASA POWER SFMC (0–5 cm), measured/modelled date "
                           f"{moisture['date']} ({moisture['age_days']} days ago). "
                           "This is gridded volumetric water content, NOT percent saturation "
                           "or a live field sensor reading.")
            elif wetness:
                ui_caption(f"NASA POWER GWETTOP surface wetness fraction {wetness['fraction']:.2f} (unitless 0–1) "
                           f"on {wetness['date']} ({wetness['age_days']} days ago). "
                           "This is NOT SFMC volumetric moisture, soil saturation, or a field sensor reading.")
            elif nasa_conditions:
                ui_caption('NASA soil observation unavailable: ' +
                           str(nasa_conditions.get('moisture_detail', 'No usable reading returned.')) +
                           ' Other climate data can still work. No value was invented.')
            if fire:
                ui_caption(f"Fire-weather screening: NASA POWER data dated {fire['date']}; "
                           f"Tmax {fire['temperature_max_c']:.1f} °C, RH {fire['relative_humidity_pct']:.0f}%, "
                           f"wind {fire['wind_speed_ms']:.1f} m/s, 7-day rain {fire['rainfall_7d_mm']:.1f} mm.")
                ui_caption(t('Fire risk is an exploratory weather screening, not an official warning.'))
            if nasa_conditions and nasa_conditions['errors']:
                with ui_expander('NASA data availability details'):
                    for message in nasa_conditions['errors']:
                        st.write(message)
            ui_caption(t('NASA gridded products are not live field sensors.'))
    with action_col:
        with st.container(border=True):
            ui_markdown('#### ✅ Action Summary')
            if result:
                rows = _crop_rows(result)
                best = next((row['crop'] for row in rows if CROPS[row['crop']]['family'] != 'perennial'), 'Not available')
                ui_markdown('<div class="soe-summary">'
                            f'<p>🌱 <b>Top screening candidate:</b> {_safe(ui_text(best))}</p>'
                            '<p>📅 <b>Sowing:</b> See crop-specific candidate months below</p>'
                            '<p>💧 <b>Irrigation:</b> Review 16-day forecast and field moisture</p>'
                            '<p>🌾 <b>Harvest:</b> FAO crop-cycle range depends on sowing date</p>'
                            '</div>', unsafe_allow_html=True)
                ui_caption('Exploratory ranking only; no yield, profit or guaranteed planting dates.')
            else:
                ui_markdown('<div class="soe-neutral">Complete Farm setup and choose '
                            '<b>Analyze farm scenarios</b> to populate this summary.</div>',
                            unsafe_allow_html=True)

    ui_markdown('### 🌱 Tailored Crop Recommendations for Your Farm')
    ui_caption('Crop ranges: FAO ECOCROP. NASA selected-location seasonal temperature and complete-year annual rainfall now both affect the exploratory scores. Water categories are crop-level heuristics, not measured irrigation demand.')
    if result:
        rows = _crop_rows(result)
        benefit_heading = 'Soil Health Benefit*' if result['priority'] == 'Soil health' else 'Water preference*'
        ui_markdown('<div class="soe-row soe-header"><span>Crop</span><span>Demo score</span>'
                    f'<span>{_safe(ui_text("Crop water category*"))}</span><span>{_safe(ui_text(benefit_heading))}</span><span>{_safe(ui_text("Sowing period*"))}</span>'
                    '<span>Harvest period*</span><span>Interpretation</span></div>', unsafe_allow_html=True)
        # Rank-based green-to-red gradient; 13 stops span any number of crops.
        color_count = 13
        daily = None
        try:
            daily, _, _ = load_climate_data(*location)
        except Exception:
            pass
        # Crop table defaults to an evidence-linked calendar, not the default
        # date of an unrelated farmer-journal input. Historical screening only.
        for index, item in enumerate(rows):
            crop_name = item['crop']
            water = CROPS[crop_name]['water'].capitalize()
            benefit = _priority_benefit(crop_name, result['previous_crop'], result['priority'])
            score = float(item['score'])
            perennial = CROPS[crop_name]['family'] == 'perennial'
            candidates = screening_months(daily, crop_name, from_date=date.today()) if daily is not None and not perennial else []
            sowing_text = ', '.join(f"{t(__import__('calendar').month_name[candidate['month']])} {candidate['year']} ({candidate['historical_temp_c']:.0f}°C)" for candidate in candidates[:2]) if candidates else 'Not established'
            harvest = candidate_harvest_window(crop_name, candidates, from_date=date.today()) if not perennial else None
            if harvest:
                harvest_text = (f"{local_date(harvest['earliest'])} – "
                                f"{local_date(harvest['latest'])}")
            else:
                harvest_text = ('Orchard establishment varies' if perennial else
                                'Not estimable — no temperature-screened sowing month')
            if perennial:
                sowing_text = 'Orchard establishment' 
            temp_match = float(item['climate_score'])
            rain_match = item.get('rain_score')
            note = (f"{ui_text('Temp')} {item['local_temperature_c']:.1f}°C ({temp_match:.1f}/4); "
                    + (f'{ui_text("Annual rain")} {item["annual_rainfall_mm"]:.0f}mm ({rain_match:.1f}/4)' if rain_match is not None else ui_text('Annual rain unavailable')))
            ui_markdown(f'<div class="soe-row {f"rank-{1 + round(index * (color_count - 1) / max(len(rows) - 1, 1))}"}">'
                        f'<span><b>{_safe(ui_text(crop_name))}</b></span>'
                        f'<span>{score:.1f} {_safe(ui_text("points"))}</span>'
                        f'<span>{_safe(ui_text({"Low":"Lower water need*","Medium":"Moderate water need*","High":"Higher water need*"}[water]))}</span>'
                        f'<span>{_safe(ui_text(benefit))}</span>'
                        f'<span>{_safe(ui_text(sowing_text))}</span>'
                        f'<span>{_safe(ui_text(harvest_text))}</span>'
                        f'<span>{_safe(ui_text(note))}</span></div>',
                        unsafe_allow_html=True)
        ui_caption(ui_text('Harvest dates are estimates based on historical sowing months and FAO crop cycles; they are not forecasts.'))
        ui_caption(ui_text('Crop water categories and rankings are illustrative; check local conditions before planting.'))
        ui_caption(f"{ui_text('Selected farm:')} {location[0]:.3f}, {location[1]:.3f} · "
                   f"{ui_text('Previous crop:')} {t(result['previous_crop'])}")

    else:
        ui_markdown('<div class="soe-preview-label"><b>LAYOUT PREVIEW ONLY</b> — Colors illustrate the ranking design, not actual suitability. Run Analyze farm scenarios for real crop results.</div>', unsafe_allow_html=True)
        ui_markdown('<div class="soe-row soe-header"><span>Crop</span><span>Demo score</span><span>Water need</span><span>Soil / Water benefit*</span><span>Sowing period</span><span>Harvest period</span><span>Interpretation</span></div>', unsafe_allow_html=True)
        for color, rank in zip(('rank-1','rank-2','rank-3','rank-4'),('1st','2nd','3rd','4th')):
            ui_markdown(
                f'<div class="soe-row {color}"><span><b>{rank} candidate</b></span>'
                '<span>Awaiting analysis</span><span>Not assessed</span><span>Choose priority</span>'
                '<span>Not established</span><span>Not established</span><span>Preview only</span></div>',
                unsafe_allow_html=True)

    # NASA measurements were fetched for the selected farm above. Reuse the
    # same result; the new module must not add a second network request.
    if result and location:
        render_input_guidance_panel(result, nasa_conditions, location)

    graph_col, weather_col, neighbor_col = st.columns([1.1, 1.1, .9], gap='medium')
    with graph_col:
        with st.container(border=True):
            ui_markdown('#### 📈 Temperature & Climate Trends')
            if result:
                ui_metric('Temperature change (2021–25 vs 2001–20)',
                          f"{result['comparison']['temperature_difference']:+.2f} °C")
                st.plotly_chart(_plot_annual(result['annual']), use_container_width=True)
                ui_caption('NASA historical annual mean, 2001–2025 · Not a full-year forecast.')
            else:
                ui_info('Historical chart available after farm analysis.')
    with weather_col:
        with st.container(border=True):
            ui_markdown('#### 🌦️ 16-Day Weather & Irrigation')
            if location and ui_button('Get 16-day forecast', key='dashboard_weather_button'):
                try:
                    st.session_state['dashboard_weather_data'] = _get_weather(*location)
                    st.session_state['dashboard_weather_coords'] = location
                except Exception:
                    st.session_state.pop('dashboard_weather_data', None)
                    ui_warning('Forecast unavailable; historical NASA data will not be displayed as a forecast.')
            forecast = st.session_state.get('dashboard_weather_data')
            if location and forecast is not None and st.session_state.get('dashboard_weather_coords') == location:
                st.plotly_chart(_forecast_plot(forecast), use_container_width=True)
                with ui_expander('Daily rainfall and irrigation checks'):
                    st.dataframe(localize_table(forecast_monitoring_table(forecast), known_statuses=FORECAST_STATUSES), hide_index=True, use_container_width=True)
                ui_info('Check actual soil moisture before irrigating. No exact watering schedule is calculated.')
                ui_caption('Source: Open-Meteo short-range forecast (not live NASA field measurements).')
            else:
                ui_info('Request a short-range forecast to view rainfall and daily checks.')
    with neighbor_col:
        with st.container(border=True):
            ui_markdown('#### 👥 Nearby Farm Activity')
            if location:
                try:
                    counts = nearby_crop_totals(*location)
                except Exception:
                    counts = []
                if counts:
                    st.dataframe(localize_table(pd.DataFrame(counts)), hide_index=True, use_container_width=True)
                else:
                    ui_info('No shareable nearby crop totals yet.')
                ui_caption('Only opted-in aggregate crop counts from 3+ accounts; no exact positions or identifiable farm labels.')
            else:
                ui_caption('Select your location to check anonymous nearby crop totals.')

    ui_caption('Illustrative scores are not validated forecasts. No field soil-moisture sensor, yield model, '
               'profit calculation or real-time fire-risk feed has been connected.')
