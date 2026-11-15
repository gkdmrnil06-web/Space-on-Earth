"""Optional two-season historical crop-rotation panel for Space on Earth.

The results are exploratory screenings, never planting forecasts or advice.
"""
from i18n import t
import calendar
import streamlit as st
from multi_season_rotation import compare_two_seasons

def _season_label(season):
    months = '–'.join(season['month_names'])
    return f"{months} ({season['duration_months']} months)"

def render_multi_season_panel(analysis_result, load_climate_data):
    """Render two consecutive historical season comparisons for the submitted farm."""
    st.divider()
    st.subheader(t('6. Multi-Season Crop Rotation Planner'))
    st.caption(t('Two consecutive growing windows, using historical NASA POWER data (2021–2025) and FAO ECOCROP reference ranges. These are scenario rankings, not future-weather or yield predictions.'))
    if analysis_result is None:
        st.info(t('Analyze a farm scenario first to use the multi-season planner.'))
        return
    location = analysis_result['location']
    previous = analysis_result['previous_crop']
    start_month = analysis_result['season_month']
    duration = analysis_result['season_length']
    measured_ph = analysis_result.get('soil_ph')
    signature = (location, previous, start_month, duration, measured_ph)
    st.write(f'**Selected farm:** {location[0]:.3f}, {location[1]:.3f}  |  **Previous crop:** {previous}')
    st.write(f'**First growing window:** {calendar.month_name[start_month]}, {duration} months  |  **Second growing window:** the following {duration} months')
    if measured_ph is None:
        st.caption(t('No measured soil pH supplied; pH is excluded from these scores.'))
    else:
        st.caption(f'Farmer-supplied measured soil pH: {measured_ph:.1f}.')
    st.info(t('This planner uses historical climate patterns only. SoilGrids nearby-cell estimates are NOT used as measured soil pH.'))
    if st.button(t('Generate two-season plans'), type='primary', key='run_multi_season'):
        try:
            with st.spinner('Analyzing historical seasons at the selected coordinates...'):
                daily, _, _ = load_climate_data(*location)
                output = compare_two_seasons(previous_crop=previous, start_month=start_month, months_per_season=duration, daily_data=daily, soil_ph=measured_ph, number_of_plans=3)
            st.session_state['multi_season_output'] = output
            st.session_state['multi_season_signature'] = signature
        except Exception as error:
            st.session_state.pop('multi_season_output', None)
            st.session_state.pop('multi_season_signature', None)
            st.error(f'Multi-season analysis could not be completed: {error}')
            return
    if st.session_state.get('multi_season_signature') != signature:
        st.info(t('Select Generate two-season plans to view results for this farm scenario.'))
        return
    output = st.session_state.get('multi_season_output')
    if not output:
        st.info(t('No two-season results are available yet.'))
        return
    first = output['first_season_climate']
    second = output['second_season_climate']
    left, right = st.columns(2, gap='large')
    for column, index, climate in ((left, 1, first), (right, 2, second)):
        with column:
            with st.container(border=True):
                st.markdown(f'**Season {index}: {_season_label(climate)}**')
                st.metric(t('Historical mean temperature'), f"{climate['temperature_c']:.1f} °C")
                st.metric(t('Historical mean seasonal rain'), f"{climate['precipitation_mm']:.0f} mm")
                st.caption('Complete historical windows: ' + ', '.join((str(y) for y in climate['years_used'])))
    st.markdown(t('#### Ranked two-season sequences'))
    for rank, plan in enumerate(output['plans'], start=1):
        sequence = ' → '.join(plan['sequence'])
        with st.container(border=True):
            st.markdown(f'**#{rank} — {sequence}**')
            st.write(f"**Illustrative total score: {plan['total_score']:.1f} / 24**")
            st.caption(t('A demonstration score, not a planting-success probability.'))
            for season_number in (1, 2):
                item = plan[f'season_{season_number}']
                with st.expander(f"Season {season_number}: {item['crop']} — score {item['score']:.1f}"):
                    st.write(f"Temperature contribution: {item['temperature_score']:.1f} / 8")
                    st.write(f"Rotation contribution: {item['rotation_score']:.1f} / 2")
                    if item['ph_score'] is None:
                        st.write(t('pH contribution: not evaluated'))
                    else:
                        st.write(f"Measured-pH contribution: {item['ph_score']:.1f} / 2")
                    for note in item['notes']:
                        st.write(f'• {note}')
    with st.expander(t('Multi-season data quality and limitations')):
        st.write(output['limitations'])
        st.write(t('The displayed 24-point maximum includes an optional measured-pH component. When pH is missing, the attainable total is lower. Comparisons are intended within the same input scenario.'))
        st.write(t('Growing windows are consecutive calendar periods, but the prototype does not verify crop-specific maturity, planting dates, or whether a chosen crop can finish within the window.'))
