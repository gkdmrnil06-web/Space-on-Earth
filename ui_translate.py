from functools import lru_cache
"""Localized presentation text for the dashboard and login hero.
Only visible labels are translated; calculations and data keys remain unchanged.
"""
import re
import streamlit as st
from i18n import t, get_language

TR = {
'Unknown / Not tested': 'Bilinmiyor / Test edilmedi',
'Sand': 'Kum',
'Loamy sand': 'Tınlı kum',
'Sandy loam': 'Kumlu tın',
'Loam': 'Tın',
'Silt loam': 'Siltli tın',
'Silt': 'Silt',
'Sandy clay loam': 'Kumlu killi tın',
'Clay loam': 'Killi tın',
'Silty clay loam': 'Siltli killi tın',
'Sandy clay': 'Kumlu kil',
'Silty clay': 'Siltli kil',
'Clay': 'Kil',
'Soil texture is farmer-reported, not measured by NASA POWER. USDA texture classes are available; choose Unknown / Not tested if unsure. New texture classes receive a neutral prototype soil score until crop-specific evidence is available.': 'Toprak tekstürü çiftçinin beyanıdır; NASA POWER tarafından ölçülmez. USDA sınıflarından seçim yapın; emin değilseniz Bilinmiyor / Test edilmedi seçin. Yeni tekstür sınıfları, ürüne özel kanıt bulunana kadar tarafsız bir prototip puanı alır.',
"Space on Earth · Farm Dashboard":"Space on Earth · Çiftlik Paneli",
"NASA-powered climate context · A simple overview before detailed analysis":"NASA destekli iklim bilgileri · Ayrıntılı analiz öncesi genel bakış",
"Farm position selected on the map":"Çiftlik konumu haritada seçildi",
"Climate context:":"İklim bilgisi:", "Alerts:":"Uyarılar:",
"Historical mean temperature":"Geçmiş ortalama sıcaklık",
"rose":"arttı", "relative to 2001–2020":"2001–2020 dönemine göre",
"Review crop and irrigation plans. This is NOT a current fire warning. No verified live alert is connected.":"Ürün ve sulama planlarını gözden geçirin. Bu güncel bir yangın uyarısı DEĞİLDİR. Doğrulanmış canlı uyarı bağlı değil.",
"No verified live fire, flood or extreme-weather alert is connected. Check official local warnings.":"Doğrulanmış canlı yangın, sel veya aşırı hava olayı uyarısı bağlı değil. Resmi yerel uyarıları kontrol edin.",
"No farm-specific alert has been evaluated. Do not interpret this as an all-clear.":"Çiftliğe özel uyarı değerlendirilmedi. Bunu tehlike yok anlamında yorumlamayın.",
"Farm Map":"Çiftlik Haritası", "Satellite imagery":"Uydu görüntüsü",
"Selected location (not a verified farm boundary)":"Seçili konum (doğrulanmış tarla sınırı değil)",
"Marker only · Farm boundaries have not been verified.":"Yalnızca konum işaretçisi · Tarla sınırları doğrulanmadı.",
"Loading NASA soil and weather conditions...":"NASA toprak ve hava verileri yükleniyor...",
"NASA data unavailable":"NASA verisi mevcut değil", "Low (screening)":"Düşük (ön değerlendirme)",
"Moderate (screening)":"Orta (ön değerlendirme)", "High (screening)":"Yüksek (ön değerlendirme)",
"Low":"Düşük", "Moderate":"Orta", "High":"Yüksek",
"Farm Summary":"Çiftlik Özeti", "Coordinates":"Koordinatlar", "Soil moisture":"Toprak nemi",
"Fire risk":"Yangın riski", "Seasonal mean temp":"Sezonluk ortalama sıcaklık",
"Seasonal rainfall":"Sezonluk yağış", "Soil pH":"Toprak pH",
"Not selected":"Seçilmedi", "Run analysis":"Analiz yapın", "Not provided":"Girilmedi",
"farmer-reported":"çiftçinin bildirdiği", "screening":"ön değerlendirme",
"Soil moisture: NASA POWER SFMC (0–5 cm),":"Toprak nemi: NASA POWER SFMC (0–5 cm),",
"volumetric water content, NOT percent saturation or a field sensor.":"hacimsel su içeriği; doygunluk yüzdesi veya tarla sensörü ölçümü DEĞİLDİR.",
"Fire-weather screening: NASA POWER data dated":"Yangın hava koşulları ön değerlendirmesi: NASA POWER veri tarihi",
"7-day rain":"7 günlük yağış", "wind":"rüzgâr",
"Fire-weather screening is a simple unvalidated 4-factor heuristic, NOT an official fire warning or a prediction of fire occurrence.":"Yangın hava koşulları değerlendirmesi, doğrulanmamış dört faktörlü basit bir yöntemdir; resmi yangın uyarısı veya yangın tahmini DEĞİLDİR.",
"NASA data availability details":"NASA veri erişilebilirliği ayrıntıları",
"NASA gridded products are not live field sensors.":"NASA grid ürünleri canlı tarla sensörleri değildir.",
"Action Summary":"Eylem Özeti", "Top screening candidate:":"En uygun ön değerlendirme adayı:",
"Sowing:":"Ekim:", "Irrigation:":"Sulama:", "Harvest:":"Hasat:",
"See crop-specific candidate months below":"Aşağıdaki ürüne özel olası ayları inceleyin",
"Review 16-day forecast and field moisture":"16 günlük tahmini ve tarla nemini inceleyin",
"FAO crop-cycle range depends on sowing date":"FAO yetişme süresi ekim tarihine bağlıdır",
"Exploratory ranking only; no yield, profit or guaranteed planting dates.":"Yalnızca keşif amaçlı sıralama; verim, kâr veya kesin ekim tarihi tahmini değildir.",
"Tailored Crop Recommendations for Your Farm":"Çiftliğinize Özel Ürün Önerileri",
"Crop requirements: FAO ECOCROP. Colored rows show exploratory ranking. Soil health and water labels are qualitative heuristics, not measured outcomes; crop dates are conditional guides.":"Ürün gereksinimleri: FAO ECOCROP. Renkli satırlar keşif amaçlı sıralamayı gösterir. Toprak sağlığı ve su etiketleri ölçüm değil, nitel değerlendirmedir; tarihler koşullu rehberdir.",
"Crop":"Ürün", "Demo score":"Örnek puan", "Water need*":"Su ihtiyacı*",
"Soil Health Benefit*":"Toprak Sağlığı Faydası*", "Water Conservation*":"Su Tasarrufu*",
"Sowing period*":"Ekim dönemi*", "Harvest period*":"Hasat dönemi*",
"Interpretation":"Yorum", "points":"puan", "Not established":"Belirlenmedi",
"Set sowing date":"Ekim tarihini belirleyin", "Temp match:":"Sıcaklık uyumu:",
"Lower water need*":"Düşük su ihtiyacı*", "Moderate water need*":"Orta su ihtiyacı*",
"Higher water need*":"Yüksek su ihtiyacı*",
"Nitrogen fixation potential*":"Azot bağlama potansiyeli*",
"Crop-family diversity potential*":"Ürün ailesi çeşitliliği potansiyeli*",
"Repeat crop; rotation caution":"Aynı ürün; rotasyon uyarısı",
"Legume after legume; assess rotation":"Baklagil sonrası baklagil; rotasyonu değerlendirin",
"Same crop family; limited rotation*":"Aynı ürün ailesi; sınırlı rotasyon*",
"Temperature & Climate Trends":"Sıcaklık ve İklim Eğilimleri",
"Temperature change (2021–25 vs 2001–20)":"Sıcaklık değişimi (2021–25 / 2001–20)",
"NASA historical annual mean, 2001–2025 · Not a full-year forecast.":"NASA geçmiş yıllık ortalaması, 2001–2025 · Tam yıl tahmini değildir.",
"Historical chart available after farm analysis.":"Geçmiş iklim grafiği çiftlik analizinden sonra gösterilir.",
"16-Day Weather & Irrigation":"16 Günlük Hava Durumu ve Sulama",
"Get 16-day forecast":"16 günlük tahmini getir",
"Forecast unavailable; historical NASA data will not be displayed as a forecast.":"Tahmin mevcut değil; geçmiş NASA verileri tahmin gibi gösterilmeyecek.",
"Daily rainfall and irrigation checks":"Günlük yağış ve sulama kontrolleri",
"Check actual soil moisture before irrigating. No exact watering schedule is calculated.":"Sulamadan önce gerçek toprak nemini kontrol edin. Kesin sulama programı hesaplanmaz.",
"Source: Open-Meteo short-range forecast (not live NASA field measurements).":"Kaynak: Open-Meteo kısa vadeli tahmin (canlı NASA tarla ölçümü değildir).",
"Request a short-range forecast to view rainfall and daily checks.":"Yağış ve günlük kontroller için kısa vadeli tahmini isteyin.",
"Nearby Farm Activity":"Yakındaki Çiftlik Etkinlikleri",
"No shareable nearby crop totals yet.":"Henüz paylaşılabilir yakındaki ürün toplamı yok.",
"Only opted-in aggregate crop counts from 3+ accounts; no exact positions or identifiable farm labels.":"Yalnızca izin veren en az 3 hesaptan toplu ürün sayıları; kesin konum veya tanımlanabilir çiftlik bilgisi yok.",
"Select your location to check anonymous nearby crop totals.":"Anonim yakın çiftlik ürün toplamlarını görmek için konum seçin.",
"Previous crop:":"Önceki ürün:", "alternative next crops screened.":"alternatif sonraki ürün değerlendirildi.",
"Rank may change with priority and measured pH. Planting dates, crop cycle and economics require local validation.":"Sıralama önceliğe ve ölçülen pH'a göre değişebilir. Ekim tarihleri, yetişme süresi ve ekonomik sonuçlar yerel doğrulama gerektirir.",
"Maize":"Mısır", "Wheat":"Buğday", "Beans":"Fasulye", "Sorghum":"Sorgum",
"Rice":"Pirinç", "Potato":"Patates", "Sunflower":"Ayçiçeği", "Tomato":"Domates", "Chickpea":"Nohut", "Barley":"Arpa", "Soybean":"Soya fasulyesi", "Lentil":"Mercimek", "Groundnut":"Yer fıstığı",
"Perennial orchard":"Çok yıllık meyve bahçesi", "Orchard establishment":"Bahçe tesisi", "Preliminary climate screen":"Ön iklim değerlendirmesi", "Perennial orchard; assess separately*":"Çok yıllık bahçe; ayrı değerlendirin*",
"Water conservation":"Su tasarrufu", "Soil health":"Toprak sağlığı",
"Lower":"Daha düşük", "Medium":"Orta", "Higher":"Daha yüksek",
"Grow smarter.":"Daha bilinçli yetiştirin.", "Understand your land.":"Toprağınızı tanıyın.",
"Discover climate trends, explore crop rotation options, and plan your farm with clear, data-informed insights.":"İklim eğilimlerini keşfedin, ürün rotasyonu seçeneklerini inceleyin ve çiftliğinizi verilere dayalı bilgilerle planlayın.",
"Crop planning":"Ürün planlama", "Irrigation context":"Sulama bilgileri",
"NASA climate data":"NASA iklim verileri", "Global locations":"Küresel konumlar",
"NASA-POWERED RESEARCH PROTOTYPE":"NASA DESTEKLİ ARAŞTIRMA PROTOTİPİ",
}
ZH = {
"Tomato":"番茄", "Chickpea":"鹰嘴豆", "Barley":"大麦", "Soybean":"大豆", "Lentil":"扁豆", "Groundnut":"花生", "Perennial orchard":"多年生果园", "Orchard establishment":"果园建设", "Preliminary climate screen":"初步气候筛选",
'Unknown / Not tested': '未知 / 未检测',
'Sand': '砂土',
'Loamy sand': '壤质砂土',
'Sandy loam': '砂壤土',
'Loam': '壤土',
'Silt loam': '粉砂壤土',
'Silt': '粉砂土',
'Sandy clay loam': '砂质黏壤土',
'Clay loam': '黏壤土',
'Silty clay loam': '粉砂质黏壤土',
'Sandy clay': '砂质黏土',
'Silty clay': '粉砂质黏土',
'Clay': '黏土',
"Space on Earth · Farm Dashboard":"Space on Earth · 农场仪表板",
"Farm Map":"农场地图","Farm Summary":"农场概况","Action Summary":"行动摘要",
"Satellite imagery":"卫星影像","Coordinates":"坐标","Soil moisture":"土壤水分",
"Fire risk":"火灾风险","Seasonal mean temp":"季节平均气温","Seasonal rainfall":"季节降水量",
"Soil pH":"土壤 pH","NASA data unavailable":"NASA 数据不可用",
"Tailored Crop Recommendations for Your Farm":"为您的农场定制的作物建议",
"Crop":"作物","Demo score":"示例评分","Water need*":"需水量*",
"Soil Health Benefit*":"土壤健康潜在益处*","Water Conservation*":"节水潜力*",
"Sowing period*":"播种期*","Harvest period*":"收获期*","Interpretation":"说明",
"Temperature & Climate Trends":"温度与气候趋势","16-Day Weather & Irrigation":"16 天天气与灌溉",
"Nearby Farm Activity":"附近农场活动","Get 16-day forecast":"获取16天天气预报",
"Grow smarter.":"科学种植。","Understand your land.":"了解您的土地。",
"Crop planning":"作物规划","Irrigation context":"灌溉信息",
"NASA climate data":"NASA 气候数据","Global locations":"全球地点",
"NASA-POWERED RESEARCH PROTOTYPE":"NASA 支持的研究原型",
}
AR = {
"Space on Earth · Farm Dashboard":"Space on Earth · لوحة معلومات المزرعة",
"NASA-powered climate context · A simple overview before detailed analysis":"معلومات مناخية مدعومة من ناسا · نظرة عامة قبل التحليل التفصيلي",
"Farm position selected on the map":"تم تحديد موقع المزرعة على الخريطة",
"Alerts:":"التنبيهات:",
"No verified live fire, flood or extreme-weather alert is connected. Check official local warnings.":"لا توجد خدمة متصلة لتنبيهات الحرائق أو الفيضانات أو الطقس المتطرف المؤكدة. تحقق من التحذيرات المحلية الرسمية.",
"No farm-specific alert has been evaluated. Do not interpret this as an all-clear.":"لم يتم تقييم تنبيه خاص بالمزرعة. لا تعتبر ذلك تأكيداً على عدم وجود خطر.",
"Farm Map":"خريطة المزرعة", "Satellite imagery":"صور الأقمار الصناعية",
"Marker only · Farm boundaries have not been verified.":"مؤشر الموقع فقط · لم يتم التحقق من حدود المزرعة.",
"Farm Summary":"ملخص المزرعة", "Action Summary":"ملخص الإجراءات",
"Coordinates":"الإحداثيات", "Soil moisture":"رطوبة التربة", "Fire risk":"خطر الحريق",
"Seasonal mean temp":"متوسط حرارة الموسم", "Seasonal rainfall":"أمطار الموسم", "Soil pH":"درجة حموضة التربة",
"NASA data unavailable":"بيانات ناسا غير متاحة", "Low":"منخفض", "Moderate":"متوسط", "High":"مرتفع",
"screening":"تقييم أولي", "farmer-reported":"بحسب المزارع",
"Top screening candidate:":"أفضل محصول مبدئي:", "Sowing:":"الزراعة:",
"Irrigation:":"الري:", "Harvest:":"الحصاد:",
"See crop-specific candidate months below":"راجع أشهر الزراعة المقترحة أدناه",
"Review 16-day forecast and field moisture":"راجع توقعات 16 يوماً ورطوبة الحقل",
"FAO crop-cycle range depends on sowing date":"مدة دورة المحصول حسب الفاو تعتمد على تاريخ الزراعة",
"Tailored Crop Recommendations for Your Farm":"توصيات المحاصيل المناسبة لمزرعتك",
"Crop":"المحصول", "Demo score":"درجة تجريبية", "Water need*":"الاحتياج للماء*",
"Soil Health Benefit*":"فائدة محتملة لصحة التربة*", "Water Conservation*":"توفير المياه*",
"Sowing period*":"فترة الزراعة*", "Harvest period*":"فترة الحصاد*", "Interpretation":"التفسير",
"points":"نقاط", "Not established":"غير محدد", "Set sowing date":"حدد تاريخ الزراعة",
"Lower water need*":"احتياج أقل للماء*", "Moderate water need*":"احتياج متوسط للماء*",
"Higher water need*":"احتياج أعلى للماء*", "Nitrogen fixation potential*":"إمكانية تثبيت النيتروجين*",
"Crop-family diversity potential*":"إمكانية تنوع عائلات المحاصيل*",
"Temperature & Climate Trends":"اتجاهات الحرارة والمناخ",
"16-Day Weather & Irrigation":"الطقس والري لمدة 16 يوماً",
"Nearby Farm Activity":"نشاط المزارع القريبة",
"Get 16-day forecast":"الحصول على توقعات 16 يوماً",
"NASA gridded products are not live field sensors.":"منتجات ناسا الشبكية ليست أجهزة استشعار مباشرة في الحقل.",
"Grow smarter.":"ازرع بذكاء.", "Understand your land.":"افهم أرضك.",
"Discover climate trends, explore crop rotation options, and plan your farm with clear, data-informed insights.":"اكتشف اتجاهات المناخ وخيارات تناوب المحاصيل وخطط لمزرعتك بمعلومات مستندة إلى البيانات.",
"Crop planning":"تخطيط المحاصيل", "Irrigation context":"معلومات الري",
"NASA climate data":"بيانات ناسا المناخية", "Global locations":"مواقع حول العالم",
"NASA-POWERED RESEARCH PROTOTYPE":"نموذج بحثي مدعوم من ناسا",
"Maize":"الذرة", "Wheat":"القمح", "Beans":"الفاصوليا", "Sorghum":"الذرة الرفيعة",
"Rice":"الأرز", "Potato":"البطاطس", "Sunflower":"دوار الشمس", "Tomato":"طماطم", "Chickpea":"حمص", "Barley":"شعير", "Soybean":"فول الصويا", "Lentil":"عدس", "Groundnut":"فول سوداني",
}
# Long messages and dynamic phrases are translated through the existing t()
# function when not covered by the local dictionary.
@lru_cache(maxsize=128)
def _visible_catalog(lang):
    """Merge bundled UI dictionaries; never translate source identifiers or raw HTML."""
    from i18n import TRANSLATIONS, OFFLINE_CORE, _offline_catalog
    from dashboard_translations import EXTRA
    mapping = dict(_offline_catalog(lang))
    if lang == 'tr':
        mapping.update({key: val[0] for key, val in TRANSLATIONS.items()})
        mapping.update({key: val[0] for key, val in OFFLINE_CORE.items()})
        mapping.update({key: val[0] for key, val in EXTRA.items()})
        mapping.update(TR)
    elif lang == 'zh':
        mapping.update({key: val[1] for key, val in TRANSLATIONS.items()})
        mapping.update({key: val[1] for key, val in EXTRA.items()})
        mapping.update(ZH)
    elif lang == 'ja':
        mapping.update({key: val[1] for key, val in OFFLINE_CORE.items()})
    elif lang == 'ar':
        mapping.update(AR)
    mapping.update(_offline_catalog(lang))  # Curated entries take precedence.
    return {key: val for key, val in mapping.items() if isinstance(key, str) and isinstance(val, str)
            and key and val and key != val}


def _replace_static_phrases(value, mapping):
    """Replace known text fragments while leaving numbers, years and units unchanged.

    Boundaries prevent e.g. Crop inside Cropland being changed. Longest labels
    take precedence so that 'Soil moisture' is never split at 'Soil'.
    """
    if not mapping:
        return value
    keys = [k for k in mapping if len(k) >= 4 and '\n' not in k and
            not k.startswith(('http://','https://','<')) and
            not any(x in k for x in ('{', '}'))]
    keys.sort(key=len, reverse=True)
    if not keys:
        return value
    # Per-value matching avoids replacing source strings inside already translated text.
    matcher = re.compile('|'.join(r'(?<![\w])' + re.escape(key) + r'(?![\w])' for key in keys))
    return matcher.sub(lambda match: mapping[match.group(0)], value)


def ui_text(value):
    if not isinstance(value, str):
        return value
    lang = get_language()
    if lang == 'en' or not value.strip():
        return value
    mapping = _visible_catalog(lang)
    if value in mapping:
        return mapping[value]
    translated = t(value)
    if translated != value:
        return translated
    # Interpolated strings and emoji-prefixed headings are not exact dictionary
    # keys: localize their known pieces without touching numerical measurements.
    return _replace_static_phrases(value, mapping)

_TAGS = re.compile(r"(<[^>]+>)")
def ui_html(value):
    if not isinstance(value, str):
        return value
    if "<" not in value:
        return ui_text(value)
    # Preserve CSS, JavaScript, and HTML attributes. Translate only text nodes.
    chunks = _TAGS.split(value)
    output = []
    in_raw = False
    for part in chunks:
        if part.startswith("<") and part.endswith(">"):
            lower = part.lower().strip()
            if lower.startswith(("<style", "<script")):
                in_raw = True
            elif lower.startswith(("</style", "</script")):
                in_raw = False
            output.append(part)
        elif in_raw or not part.strip():
            output.append(part)
        else:
            # Keep leading/trailing spaces around the translated content.
            lead = len(part) - len(part.lstrip())
            tail = len(part) - len(part.rstrip())
            middle = part[lead:len(part)-tail if tail else len(part)]
            output.append(part[:lead] + ui_text(middle) + (part[-tail:] if tail else ""))
    return "".join(output)

def ui_markdown(body, **kwargs):
    return st.markdown(ui_html(body), **kwargs)

def ui_caption(body, **kwargs):
    return st.caption(ui_text(body), **kwargs)

def ui_info(body, **kwargs):
    return st.info(ui_text(body), **kwargs)

def ui_warning(body, **kwargs):
    return st.warning(ui_text(body), **kwargs)

def ui_toggle(label, **kwargs):
    return st.toggle(ui_text(label), **kwargs)

def ui_button(label, **kwargs):
    return st.button(ui_text(label), **kwargs)

def ui_metric(label, *args, **kwargs):
    return st.metric(ui_text(label), *args, **kwargs)

def ui_expander(label, **kwargs):
    return st.expander(ui_text(label), **kwargs)

def ui_spinner(label, **kwargs):
    return st.spinner(ui_text(label), **kwargs)
