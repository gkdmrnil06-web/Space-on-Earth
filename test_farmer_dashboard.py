"""Offline tests. No real weather or farm records are fabricated."""
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import pandas as pd
from community_farms import save_planting, nearby_crop_totals, my_plantings, update_share, delete_record
from farmer_forecast import crop_cycle_window, screening_months, get_16_day_forecast, forecast_monitoring_table


def test_journal():
    with TemporaryDirectory() as root:
        db = Path(root) / 'test.db'
        for i in range(3):
            save_planting(f'farmer{i}@example.com','Beans',date(2026,4,1),38.466,27.221,
                          farmer_notes=f'SECRET-{i}',share_crop=(i != 2),db_path=db)
        assert nearby_crop_totals(38.466,27.221,db_path=db) == []
        assert 'SECRET-0' in str(my_plantings('farmer0@example.com',db))
        assert 'SECRET-0' not in str(my_plantings('farmer1@example.com',db))
        rid = my_plantings('farmer2@example.com',db)[0]['id']
        update_share('farmer2@example.com',rid,True,db)
        assert nearby_crop_totals(38.466,27.221,db_path=db)==[{'Crop':'Beans','Sharing farms':3}]
        assert nearby_crop_totals(42,27,db_path=db)==[]
        delete_record('farmer2@example.com',rid,db)
        assert nearby_crop_totals(38.466,27.221,db_path=db)==[]


def test_plans():
    cycle = crop_cycle_window('Beans',date(2026,4,1))
    assert cycle['earliest'] == date(2026,5,21)
    assert cycle['latest'] == date(2026,12,27)
    dates = pd.date_range('2021-01-01','2025-12-31',freq='D')
    daily = pd.DataFrame({'Temperature':[20.0]*len(dates)},index=dates)
    periods = screening_months(daily,'Beans',date(2026,11,7))
    assert periods[0]['year']==2026 and periods[0]['month']==11


def test_forecast():
    from unittest.mock import MagicMock
    keys = ['time','precipitation_sum','precipitation_probability_max',
            'temperature_2m_max','temperature_2m_min','et0_fao_evapotranspiration']
    body = {'daily':dict(zip(keys,[['2026-11-08'],[5.0],[70],[23],[12],[2.4]]))}
    reply=MagicMock()
    reply.json.return_value=body
    with patch('farmer_forecast.requests.get',return_value=reply) as get:
        out=get_16_day_forecast(38.466,27.221)
        assert len(out)==1
        assert 'Check' in forecast_monitoring_table(out)['Field check'].iloc[0].capitalize() or 'Rain' in forecast_monitoring_table(out)['Field check'].iloc[0]
        assert get.call_args.kwargs['params']['forecast_days']==16


if __name__=='__main__':
    test_journal(); test_plans(); test_forecast()
    print('Farmer dashboard: offline tests passed (no live weather tested).')
