"""Space on Earth / Section 3. Location-specific climate and input awareness UI.

Never present NASA climate as a pesticide dose, diagnosis, or organic certificate.
The requested three-column layout is preserved; statuses are demo screening cues.
"""
from html import escape
import streamlit as st
from input_guidance_logic import evaluate, finite
from i18n import t, get_language


# Only visible strings are localized. Weather and risk calculations are unchanged.
_EN = {
    'Veri yok': 'No data',
    'Veri eksik': 'Data missing',
    'Bu konum için yeterli NASA verisi yok.': 'Not enough NASA data for this farm.',
    'Zararlıyı kontrol et': 'Check for pests',
    'Sıcak ve kurak hava görüldü. Yapraklara bak.': 'Warm and dry conditions: inspect the leaves.',
    'İklim riski düşük': 'Low climate warning',
    'Yine de tarlanı kontrol et.': 'Still check your field.',
    'Mantar riskini kontrol et': 'Check for fungal signs',
    'Nem ve yağış arttı. Yapraklara bak.': 'Humid or wet conditions: inspect the leaves.',
    'Hastalık olmadığını garanti etmez.': 'This does not rule out disease.',
    'Tahlil gerek': 'Soil test needed',
    'Yağıştan sonra toprağı kontrol et ve tahlil yaptır.': 'Check the soil after rain and request a soil test.',
    'Gübre miktarı için toprak tahlili yaptır.': 'Get a soil test before choosing fertilizer amounts.',
    'Kontrol gerek': 'Field check needed',
    'Tarladaki koşulları kontrol et.': 'Check conditions in the field.',
    'Haşere İlacı / Zararlı Yönetimi': 'Pest management',
    'Fungisit / Mantar İzleme': 'Fungal disease monitoring',
    'Organik Gübre / Besin Yönetimi': 'Organic fertilizer / soil nutrients',
    'Önce tarlada böcek var mı kontrol et. Gerekirse uzmana sor.': 'Check for pests before treating. Ask an agronomist if needed.',
    'Yapraklarda leke veya çürüme var mı kontrol et.': 'Check leaves for spots or rot.',
    'Toprak tahlili yaptır; gübre miktarını sonuca göre seç.': 'Test your soil and select fertilizer amounts from the results.',
    'Sıcaklık veya yağış verisi yok': 'Temperature or rainfall data missing',
    'Nem veya yağış verisi yok': 'Humidity or rainfall data missing',
    'Yağış verisi yok · toprak tahlili gerekli': 'Rain data missing · soil test needed',
    'Veri tarihi bilinmiyor': 'Date unavailable',
    'NASA POWER iklim verisi bu konum için alınamadı. Eşik ve saha değerlendirmeleri eksik veri olarak gösteriliyor.': 'NASA POWER weather data could not be retrieved for this farm. Missing measurements are not estimated.',
    'BÖLÜM 3: AKILLI İLAÇ & GİRDİ ÖNERİLERİ VE EŞİK DEĞERLERİ': 'SECTION 3: SMART FARM INPUTS & FIELD CHECKS',
    'Seçilen çiftlik:': 'Selected farm:',
    'NASA POWER veri tarihi:': 'NASA POWER data date:',
    'Bu bölüm hava koşullarına göre neyi kontrol etmen gerektiğini söyler. İlaç veya gübre miktarı vermez.': 'Local weather data help you decide what to check in the field; no pesticide or fertilizer doses are given.',
    'Geçmiş sıcaklık değişimi': 'Historical temperature change',
    'Son 7 gün ort. Tmax': 'Last 7 days avg. high temp',
    'Son 7 gün bağıl nem': 'Last 7 days relative humidity',
    'Son 7 gün toplam yağış': 'Last 7 days total rainfall',
    'Son 7 gün ort. rüzgâr': 'Last 7 days average wind',
    'Girdi / İlaç Türü': 'Farm input / concern',
    'Ne Yapmalısın?': 'What to do',
    'Durum': 'Status',
    'Rüzgâr:': 'Wind:',
    'İlaç uygulamadan önce tarladaki o anki rüzgârı ölç ve ürün etiketini kontrol et.': 'Before spraying, check wind in your field and read the product label.',
    'Bu haftalık ortalama, uygulamanın güvenli olduğunu göstermez.': 'The weekly average does not establish spray safety.',
    'Akıllı Tavsiye': 'Smart tip',
    'Böcek ya da hastalık belirtisi görürsen önce tarlanı kontrol et; hemen ilaç kullanma.': 'Check your field before applying chemicals; pest and disease signs need confirmation.',
    'Hangi yöntemin uygun olduğunu ziraat uzmanına sor. Gübre için toprak tahlili yaptır.': 'Ask an agronomist which method is suitable. Test the soil before fertilizing.',
    'İlaç ve gübre kullanımını kaydet. Organik tarım desteği için yetkili kuruma danış.': 'Keep a record of inputs. Ask an authorized body about organic certification.',
    'Bu göstergeler NASA’nın geçmiş iklim verileriyle hazırlanan örnek uyarılardır;': 'These are example weather-based checks using NASA POWER data;',
    'tarlada hastalık veya zararlı olduğunu kanıtlamaz. İlaç miktarı, gübre miktarı veya sertifika onayı vermez.': 'they do not diagnose disease or determine pesticide dosage, fertilizer amounts or certification.',
    'ilaç gerekmez': 'no pesticide is needed',
    'Organik tarım hazırlık kayıtları': 'Organic farming record checklist',
    'Çiftçi tarafından bildirilen hazırlık listesi; sertifika veya hibe uygunluğu sonucu değildir.': 'Your own checklist; not a certification or grant decision.',
    'Kayıt hazırlık kontrol listesi': 'Record preparation checklist',
    'İlaç, gübre ve saha işlemlerinin tarihli kayıtları var': 'Dated records of treatments, fertilizers and farm activities',
    'Güncel laboratuvar toprak besin analizi var': 'Recent soil nutrient lab analysis available',
    'Kullanılan girdilerin yerel organik üretim mevzuatı uygunluğu kontrol edildi': 'Inputs reviewed against local organic farming requirements',
    'Yetkili yerel organik kontrol / sertifikasyon kuruluşu ile görüşüldü': 'Contacted an authorized organic certifier',
    'Hazırlık kaydı:': 'Records prepared:',
    'kullanıcı beyanı': 'self-reported',
    'Organik sertifika veya hibe hakkı NASA iklim verisinden belirlenemez. Resmî süreç için yerel yetkili kuruluşa başvurun.': 'NASA climate data cannot determine organic certification or grant eligibility. Contact the authorized local body.',
}


def _l(tr):
    if get_language() == 'tr':
        return tr
    en = _EN.get(tr, tr)
    return t(en) if en != tr else t(en)


def _line(en, tr, **values):
    return (tr if get_language() == 'tr' else t(en)).format(**values)

def _safe(value):
    return escape(str(value), quote=True)


def _metric(value, unit, digits=1):
    number = finite(value)
    return f"{number:.{digits}f}{unit}" if number is not None else _l("Veri yok")


def _display_status(row, kind):
    """Short farmer-facing labels; weather does not establish pesticide need."""
    if row.status == "Data missing":
        return "Veri eksik", "neutral", "Bu konum için yeterli NASA verisi yok."
    if kind == "pest":
        if row.tone == "yellow":
            return "Zararlıyı kontrol et", "yellow", "Sıcak ve kurak hava görüldü. Yapraklara bak."
        return "İklim riski düşük", "green", "Yine de tarlanı kontrol et."
    if kind == "fungus":
        if row.tone == "yellow":
            return "Mantar riskini kontrol et", "yellow", "Nem ve yağış arttı. Yapraklara bak."
        return "İklim riski düşük", "green", "Hastalık olmadığını garanti etmez."
    if kind == "nutrient":
        return "Tahlil gerek", "neutral", (
            "Yağıştan sonra toprağı kontrol et ve tahlil yaptır."
            if row.tone == "yellow" else "Gübre miktarı için toprak tahlili yaptır."
        )
    return "Kontrol gerek", "neutral", "Tarladaki koşulları kontrol et."


def render_input_guidance_panel(result, nasa_conditions, location):
    if not isinstance(result, dict) or not location or result.get("location") != location:
        return
    conditions = nasa_conditions if isinstance(nasa_conditions, dict) else {}
    weather = conditions.get("input_weather") or {}
    comparison = result.get("comparison") or {}
    change = finite(comparison.get("temperature_difference"))
    anomaly = f"{change:+.2f}°C" if change is not None else _l("Veri yok")
    rows = evaluate(weather)
    pests, fungi, nutrients, wind = rows
    rain = finite(weather.get("rainfall_7d_mm"))
    rh = finite(weather.get("humidity_7d_avg_pct"))
    temp = finite(weather.get("temperature_max_7d_avg_c"))

    # No universal pesticide/fertilizer dose can be inferred from rainfall and humidity.
    # Thresholds displayed below are requirements for making a site decision, NOT chemical rates.
    table_rows = [
        {
            "icon": "🐛", "name": "Haşere İlacı / Zararlı Yönetimi", "kind": "pest", "logic": pests,
            "threshold": "Önce tarlada böcek var mı kontrol et. Gerekirse uzmana sor.",
            "climate": (
                f"{t('Last 7 days avg. high temp')}: {temp:.1f} °C · {t('Last 7 days total rainfall')}: {rain:.1f} mm"
                if temp is not None and rain is not None else _l("Sıcaklık veya yağış verisi yok")
            ),
        },
        {
            "icon": "🍄", "name": "Fungisit / Mantar İzleme", "kind": "fungus", "logic": fungi,
            "threshold": "Yapraklarda leke veya çürüme var mı kontrol et.",
            "climate": (
                f"{t('Last 7 days relative humidity')}: {rh:.0f}% · {t('Last 7 days total rainfall')}: {rain:.1f} mm"
                if rh is not None and rain is not None else _l("Nem veya yağış verisi yok")
            ),
        },
        {
            "icon": "🌱", "name": "Organik Gübre / Besin Yönetimi", "kind": "nutrient", "logic": nutrients,
            "threshold": "Toprak tahlili yaptır; gübre miktarını sonuca göre seç.",
            "climate": (
                f"{t('Last 7 days total rainfall')}: {rain:.1f} mm · {t('Soil test needed')}"
                if rain is not None else _l("Yağış verisi yok · toprak tahlili gerekli")
            ),
        },
    ]

    st.markdown("""<style>
    .soe-input-card{background:linear-gradient(145deg,#0a192b 0%,#0c2538 55%,#092a33 100%);
      border:1px solid rgba(100,187,216,.23);box-shadow:0 16px 38px rgba(0,0,0,.16);
      border-radius:20px;padding:clamp(16px,2.4vw,28px);margin:16px 0;color:#edf9ff;}
    .soe-input-eyebrow{font-size:.7rem;color:#70d2bc;font-weight:750;letter-spacing:.15em;text-transform:uppercase;margin:0 0 7px;}
    .soe-input-title{font-size:clamp(1.05rem,2vw,1.4rem);color:#f3fbff;font-weight:850;line-height:1.35;margin:0 0 10px;}
    .soe-input-sub{font-size:.83rem;color:#a8c6d4;margin:0 0 17px;line-height:1.55;}
    .soe-input-metrics{display:grid;grid-template-columns:repeat(auto-fit,minmax(145px,1fr));gap:9px;margin-bottom:18px;}
    .soe-input-metric{background:rgba(20,53,69,.84);border:1px solid rgba(99,161,188,.24);
      border-radius:12px;padding:11px 13px;font-size:.75rem;color:#a6cddd;line-height:1.35;}
    .soe-input-metric strong{display:block;color:#f3fbff;font-size:1.12rem;margin-top:6px;font-weight:800;}
    .soe-input-table-wrap{overflow-x:auto;max-width:100%;}
    .soe-input-table{width:100%;min-width:640px;table-layout:fixed;border-collapse:separate;border-spacing:0 9px;}
    .soe-input-table th{text-align:left;color:#a9d1e1;padding:0 13px 6px;font-size:.78rem;font-weight:750;}
    .soe-input-table th:nth-child(1){width:27%;}.soe-input-table th:nth-child(2){width:45%;}.soe-input-table th:nth-child(3){width:28%;}
    .soe-input-table td{background:#112d42;padding:16px 13px;color:#ecf8ff;font-size:.83rem;vertical-align:middle;line-height:1.55;
      border-top:1px solid rgba(105,167,194,.18);border-bottom:1px solid rgba(105,167,194,.18);overflow-wrap:anywhere;}
    .soe-input-table td:first-child{border-left:4px solid #4cbda8;border-radius:12px 0 0 12px;font-weight:750;}
    .soe-input-table td:last-child{border-right:1px solid rgba(105,167,194,.18);border-radius:0 12px 12px 0;}
    .soe-input-muted{color:#9fc0d1;font-size:.75rem;margin-top:5px;font-weight:450;}
    .soe-input-status{display:inline-flex;align-items:center;gap:6px;border-radius:99px;padding:6px 10px;
      font-size:.73rem;line-height:1.2;font-weight:800;border:1px solid transparent;}
    .soe-input-green{color:#9cf6c3;background:rgba(25,132,88,.23);border-color:rgba(104,236,170,.34);}
    .soe-input-yellow{color:#ffe29a;background:rgba(160,121,13,.21);border-color:rgba(255,210,98,.34);}
    .soe-input-red{color:#ffaaa6;background:rgba(179,51,63,.23);border-color:rgba(247,103,111,.39);}
    .soe-input-neutral{color:#d0d9e3;background:rgba(123,146,166,.16);border-color:rgba(155,179,201,.26);}
    .soe-input-tip{margin-top:14px;background:linear-gradient(110deg,rgba(17,85,79,.35),rgba(14,57,74,.55));
      border:1px solid rgba(93,212,176,.32);border-left:4px solid #53d6ad;border-radius:12px;padding:15px 16px;
      color:#ddf7ee;font-size:.85rem;line-height:1.62;}
    .soe-input-banner{border-radius:11px;background:rgba(60,90,114,.22);border:1px solid rgba(132,173,193,.22);
      padding:11px 13px;margin-top:12px;color:#c1d8e4;font-size:.8rem;line-height:1.6;}
    .soe-input-footnote{color:#8dacbe;font-size:.74rem;margin:13px 0 0;line-height:1.55;}
    </style>""", unsafe_allow_html=True)

    table_html = []
    for row in table_rows:
        status, tone, detail = _display_status(row["logic"], row["kind"])
        status, detail = _l(status), _l(detail)
        if tone == "red":
            symbol = "🔴"
        elif tone == "yellow":
            symbol = "🟡"
        elif tone == "green":
            symbol = "🟢"
        else:
            symbol = "⚪"
        table_html.append(
            "<tr>"
            f"<td><div>{row['icon']} {_safe(_l(row['name']))}</div></td>"
            f"<td><div>{_safe(_l(row['threshold']))}</div><div class='soe-input-muted'>"
            f"{_safe(row['climate'])}</div></td>"
            f"<td><span class='soe-input-status soe-input-{tone}'>{symbol} {_safe(status)}</span>"
            f"<div class='soe-input-muted'>{_safe(detail)}</div></td>"
            "</tr>"
        )
    date_text = weather.get("date") or _l("Veri tarihi bilinmiyor")
    if not weather:
        st.info(_l("NASA POWER iklim verisi bu konum için alınamadı. Eşik ve saha değerlendirmeleri eksik veri olarak gösteriliyor."))

    # No code paths involve pesticide application rate or certification assertions.
    st.markdown(f"""<section class='soe-input-card'>
       <div class='soe-input-eyebrow'>SPACE ON EARTH · NASA POWER · SECTION 3</div>
       <h3 class='soe-input-title'>💊 {_safe(_l('BÖLÜM 3: AKILLI İLAÇ & GİRDİ ÖNERİLERİ VE EŞİK DEĞERLERİ'))}</h3>
       <p class='soe-input-sub'>📍 {_safe(_l('Seçilen çiftlik:'))} {_safe(f'{location[0]:.3f}, {location[1]:.3f}')} · {_safe(_l('NASA POWER veri tarihi:'))} {_safe(date_text)}<br>
       {_safe(_l('Bu bölüm hava koşullarına göre neyi kontrol etmen gerektiğini söyler. İlaç veya gübre miktarı vermez.'))}</p>
       <div class='soe-input-metrics'>
         <div class='soe-input-metric'>🌡️ {_safe(_l('Geçmiş sıcaklık değişimi'))}<strong>{_safe(anomaly)}</strong></div>
         <div class='soe-input-metric'>🌡️ {_safe(_l('Son 7 gün ort. Tmax'))}<strong>{_safe(_metric(temp,'°C'))}</strong></div>
         <div class='soe-input-metric'>💧 {_safe(_l('Son 7 gün bağıl nem'))}<strong>{_safe(_metric(rh,'%',0))}</strong></div>
         <div class='soe-input-metric'>🌧️ {_safe(_l('Son 7 gün toplam yağış'))}<strong>{_safe(_metric(rain,' mm'))}</strong></div>
         <div class='soe-input-metric'>🌬️ {_safe(_l('Son 7 gün ort. rüzgâr'))}<strong>{_safe(_metric(weather.get('wind_7d_avg_ms'),' m/s'))}</strong></div>
       </div>
       <div class='soe-input-table-wrap'><table class='soe-input-table'>
         <thead><tr><th>{_safe(_l('Girdi / İlaç Türü'))}</th><th>{_safe(_l('Ne Yapmalısın?'))}</th><th>{_safe(_l('Durum'))}</th></tr></thead>
         <tbody>{''.join(table_html)}</tbody>
       </table></div>
       <div class='soe-input-banner'>🌬️ <b>{_safe(_l('Rüzgâr:'))}</b> {_safe(t('Last 7 days average wind'))} {_safe(_metric(weather.get('wind_7d_avg_ms'), ' m/s'))}.<br>
          {_safe(_l('İlaç uygulamadan önce tarladaki o anki rüzgârı ölç ve ürün etiketini kontrol et.'))}
          {_safe(_l('Bu haftalık ortalama, uygulamanın güvenli olduğunu göstermez.'))}</div>
       <div class='soe-input-tip'><b>💡 {_safe(_l('Akıllı Tavsiye'))}</b><br>
         {_safe(_l('Böcek ya da hastalık belirtisi görürsen önce tarlanı kontrol et; hemen ilaç kullanma.'))}
         {_safe(_l('Hangi yöntemin uygun olduğunu ziraat uzmanına sor. Gübre için toprak tahlili yaptır.'))}
         {_safe(_l('İlaç ve gübre kullanımını kaydet. Organik tarım desteği için yetkili kuruma danış.'))}</div>
       <p class='soe-input-footnote'>{_safe(t('NASA weather data cannot confirm pests, disease, fertilizer dose or organic certification.'))}</p>
       </section>""", unsafe_allow_html=True)

    st.markdown('#### 📋 ' + _l('Organik tarım hazırlık kayıtları'))
    st.caption(_l("Çiftçi tarafından bildirilen hazırlık listesi; sertifika veya hibe uygunluğu sonucu değildir."))
    farm_key = f"{location[0]:.3f}_{location[1]:.3f}"
    with st.expander(_l('Kayıt hazırlık kontrol listesi'), expanded=False):
        entries = [
            ("field_log", "İlaç, gübre ve saha işlemlerinin tarihli kayıtları var"),
            ("soil_lab", "Güncel laboratuvar toprak besin analizi var"),
            ("input_docs", "Kullanılan girdilerin yerel organik üretim mevzuatı uygunluğu kontrol edildi"),
            ("certifier", "Yetkili yerel organik kontrol / sertifikasyon kuruluşu ile görüşüldü"),
        ]
        checked = [st.checkbox(_l(label), key=f"soe_organic_{farm_key}_{code}") for code, label in entries]
        st.caption(_line('Records prepared: {done}/{total} (self-reported).', 'Hazırlık kaydı: {done}/{total} (kullanıcı beyanı).', done=sum(checked), total=len(checked)))
        st.info(_l("Organik sertifika veya hibe hakkı NASA iklim verisinden belirlenemez. Resmî süreç için yerel yetkili kuruluşa başvurun."))
