"""Conservative, location-specific farmer decision panels.

NASA POWER is the climate source in the original application. FIRMS is an
optional live hotspot lookup requiring a free MAP_KEY. SMAP CMR search here
is metadata discovery ONLY, not soil moisture measurement. No real-world
alert dispatch, yield/profit calculation, pesticide decision or certificate.
"""
from __future__ import annotations

import csv
import io
import math
import os
from datetime import date
from html import escape

import requests
import streamlit as st

from crop_rotation import CROPS, compare_strategies, recent_annual_rainfall
from i18n import get_language

_FIRMS_URL = 'https://firms.modaps.eosdis.nasa.gov/api/area/csv'
_CMR_URL = 'https://cmr.earthdata.nasa.gov/search/granules.json'

# Short, plain-language static UI copy in the same nine core languages as the app.
L = {
 'en': ['Project architecture & data flow', 'Data sources', 'Analysis', 'Farmer actions',
        'NASA POWER: climate', 'NASA FIRMS: satellite hotspots (optional)', 'NASA SMAP: source discovery only',
        'FAO ECOCROP: crop reference ranges', 'Farm coordinates & exploratory screening',
        'Simple crop, fire and sustainability panels',
        '1. Crop suggestions for this farm', 'Crop', 'Water need', 'Climate/rotation score', 'Assessment',
        'Low', 'Medium', 'High', 'Closer match', 'Review locally',
        'This is a 1–5 screening score, NOT a profit estimate. Profit requires local prices, yields and expenses.',
        '2. Satellite fire hotspot monitoring', 'Search FIRMS for this location', 'FIRMS connection not configured',
        'No satellite detections returned nearby', 'Satellite hotspots nearby — check official warnings',
        'Hotspots detected within 25 km', 'Nearest detection', 'Source date',
        'No detections does not prove safety. Satellite detection is not a fire forecast or emergency dispatch.',
        'Satellite query failed; risk is unknown', '3. Sustainability progress', 'Preparation checklist — not a certificate',
        'Record your water use', 'Keep pesticide and fertilizer records', 'Get a soil test',
        'Check local organic certification requirements', 'Completed checks', 'Not certified',
        'ESA-Cert is NOT an authorized certification. No grants, supply-chain priority or insurance discounts are confirmed.',
        'SMAP source metadata', 'Check NASA SMAP data catalog', 'SMAP product found in catalog',
        'SMAP observation is NOT connected as a farm soil-moisture reading.',
        'Source and usage notes', 'FIRMS requires a free NASA MAP_KEY in Streamlit secrets or an environment variable.',
        'No automatic messages are sent to emergency services.', 'Model outputs are exploratory, not official NASA/FAO decisions.',
        'Analysis unavailable for this farm.', 'No map key: live hotspot status unknown.', 'Not connected', 'Detected nearby', 'No detection in query',
        'Recordkeeping only — no official score or certificate is issued.' ],
 'tr': ['Proje mimarisi ve veri akışı','Veri kaynakları','Analiz','Çiftçi için sonuçlar',
        'NASA POWER: iklim','NASA FIRMS: uydu sıcak noktaları (isteğe bağlı)','NASA SMAP: yalnızca veri arama',
        'FAO ECOCROP: ürün referans aralıkları','Tarla koordinatları ve ön değerlendirme',
        'Sade ürün, yangın ve sürdürülebilirlik panelleri',
        '1. Bu tarlaya uygun ürünler','Ürün','Su ihtiyacı','İklim/rotasyon puanı','Değerlendirme',
        'Düşük','Orta','Yüksek','Daha uygun görünüyor','Yerelde kontrol et',
        'Bu 1–5 arası ön değerlendirme puanıdır, kâr tahmini DEĞİLDİR. Kâr için yerel fiyat, verim ve maliyet gerekir.',
        '2. Uydu yangın noktası takibi','Bu konumda FIRMS sorgula','FIRMS bağlantısı henüz kurulmamış',
        'Yakında uydu tespiti bulunmadı','Yakında uydu sıcak noktası var — resmî uyarıları kontrol et',
        '25 km içinde tespit','En yakın tespit','Veri tarihi',
        'Tespit olmaması güvenli demek değildir. Uydu tespiti yangın tahmini veya acil ihbar değildir.',
        'Uydu sorgusu başarısız; risk bilinmiyor','3. Sürdürülebilirlik takibi','Hazırlık listesi — sertifika değildir',
        'Su kullanımını kaydet','İlaç ve gübre kayıtlarını tut','Toprak tahlili yaptır',
        'Yerel organik sertifika şartlarını kontrol et','Tamamlanan adımlar','Sertifika verilmedi',
        'ESA-Cert yetkili bir sertifika değildir. Hibe, tedarik önceliği veya sigorta indirimi doğrulanmış değildir.',
        'SMAP veri kataloğu','NASA SMAP kataloğunu kontrol et','Katalogda SMAP ürünü bulundu',
        'SMAP verisi tarlaya ait ölçüm olarak bağlı değildir.',
        'Kaynaklar ve kullanım notları','FIRMS için ücretsiz NASA MAP_KEY gerekir; Streamlit secrets veya ortam değişkenine eklenir.',
        'Acil durum ekiplerine otomatik mesaj gönderilmez.','Sonuçlar ön değerlendirmedir; resmî NASA/FAO kararı değildir.',
        'Bu tarla için analiz bulunmuyor.','MAP_KEY yok: canlı yangın durumu bilinmiyor.','Bağlı değil','Yakında tespit','Sorguda tespit yok',
        'Yalnızca kayıt takibi — resmî puan veya sertifika verilmez.'],
 'ja': ['プロジェクト構成とデータの流れ','データソース','分析','農家向けの結果',
        'NASA POWER：気候','NASA FIRMS：衛星の熱源検出（任意）','NASA SMAP：データ検索のみ',
        'FAO ECOCROP：作物の参考範囲','農場の座標と試験的評価','作物・火災・持続可能性の簡単なパネル',
        '1. この農場の作物候補','作物','水需要','気候・輪作スコア','評価',
        '低','中','高','比較的適合','現地確認が必要',
        '1〜5の試験的な適合スコアであり、利益予測ではありません。利益には価格、収量、費用が必要です。',
        '2. 衛星火災熱源の確認','この地点のFIRMSを確認','FIRMSが未設定です',
        '近くの衛星検出なし','近くで熱源を検出 — 公式警報を確認',
        '25 km以内の検出数','最寄りの検出','データ日付',
        '検出がなくても安全とは限りません。衛星検出は火災予報や緊急通報ではありません。',
        '衛星照会に失敗、危険度は不明','3. 持続可能性の記録','準備チェックリスト（認証ではありません）',
        '水使用量を記録','農薬・肥料の記録を保存','土壌検査を実施',
        '地域の有機認証条件を確認','完了した項目','認証されていません',
        'ESA-Certは公認認証ではありません。補助金、取引優先、保険割引は確認されていません。',
        'SMAPデータの情報','NASA SMAPデータ一覧を確認','SMAP製品が一覧にあります',
        'SMAPの農場土壌水分測定は接続されていません。',
        '出典と注意事項','FIRMSには無料のNASA MAP_KEYが必要です（secretsまたは環境変数）。',
        '緊急機関への自動通報は行いません。','結果は試験的で、NASA/FAOの公式判断ではありません。',
        'この農場の分析結果はありません。','MAP_KEYなし：現在の熱源状況は不明です。','未接続','近くで検出','照会範囲で検出なし',
        '記録のみです。公式スコアや認証は発行しません。'],
 'de': ['Projektarchitektur und Datenfluss','Datenquellen','Analyse','Hinweise für Landwirte',
        'NASA POWER: Klima','NASA FIRMS: Satelliten-Hotspots (optional)','NASA SMAP: nur Datenkatalog',
        'FAO ECOCROP: Pflanzen-Referenzbereiche','Standort und vorläufige Bewertung','Einfache Panels zu Pflanzen, Feuer und Nachhaltigkeit',
        '1. Pflanzen für diesen Standort','Pflanze','Wasserbedarf','Klima-/Fruchtfolge-Wert','Bewertung',
        'Gering','Mittel','Hoch','Bessere Übereinstimmung','Lokal prüfen',
        'Dieser Wert von 1–5 ist KEINE Gewinnprognose. Dafür braucht es Preise, Erträge und Kosten.',
        '2. Satellitengestützte Hotspot-Prüfung','FIRMS für diesen Standort prüfen','FIRMS nicht eingerichtet',
        'Keine Satellitenerkennung in der Nähe','Hotspots in der Nähe — offizielle Warnungen prüfen',
        'Erkennungen im Umkreis von 25 km','Nächste Erkennung','Datumsangabe',
        'Keine Erkennung bedeutet nicht Sicherheit. Dies ist keine Brandvorhersage oder Notfallmeldung.',
        'Satellitenabfrage fehlgeschlagen; Risiko unbekannt','3. Nachhaltigkeit dokumentieren','Checkliste — kein Zertifikat',
        'Wasserverbrauch erfassen','Pflanzenschutz- und Düngerdaten erfassen','Bodenanalyse durchführen',
        'Lokale Bio-Zertifizierungsregeln prüfen','Erledigte Punkte','Nicht zertifiziert',
        'ESA-Cert ist kein anerkanntes Zertifikat. Förderungen, Lieferpriorität oder Versicherungsrabatte sind nicht bestätigt.',
        'SMAP-Datenkatalog','NASA-SMAP-Katalog prüfen','SMAP-Produkt im Katalog gefunden',
        'SMAP ist nicht als Messwert für den Feldboden angebunden.',
        'Quellen und Hinweise','FIRMS benötigt einen kostenlosen NASA MAP_KEY in secrets oder Umgebungsvariablen.',
        'Es werden keine automatischen Notrufe versendet.','Die Auswertung ist vorläufig und keine offizielle NASA/FAO-Entscheidung.',
        'Keine Analyse für diesen Standort.','Kein MAP_KEY: Hotspot-Status unbekannt.','Nicht verbunden','In der Nähe erkannt','Keine Erkennung','Nur Dokumentation — kein offizieller Wert oder Zertifikat.'],
 'fr': ['Architecture et circulation des données','Sources de données','Analyse','Actions pour les agriculteurs',
        'NASA POWER : climat','NASA FIRMS : points chauds satellitaires (facultatif)','NASA SMAP : recherche de données uniquement',
        'FAO ECOCROP : plages de référence des cultures','Coordonnées et évaluation exploratoire','Tableaux simples : cultures, incendies, durabilité',
        '1. Cultures possibles sur cette parcelle','Culture','Besoin en eau','Score climat/rotation','Évaluation',
        'Faible','Moyen','Élevé','Plus favorable','À vérifier sur place',
        'Ce score de 1 à 5 n’est PAS une estimation du bénéfice. Il faut prix, rendements et coûts.',
        '2. Surveillance des points chauds','Consulter FIRMS pour ce lieu','FIRMS non configuré',
        'Aucun point détecté à proximité','Points chauds proches — consultez les alertes officielles',
        'Détections dans 25 km','Détection la plus proche','Date des données',
        'Aucune détection ne garantit la sécurité. Il ne s’agit ni d’une prévision ni d’une alerte envoyée.',
        'Échec de la requête ; risque inconnu','3. Suivi de la durabilité','Liste de préparation — pas un certificat',
        'Enregistrer l’eau utilisée','Conserver les relevés de pesticides et d’engrais','Faire analyser le sol',
        'Vérifier les règles locales de certification biologique','Étapes accomplies','Non certifié',
        'ESA-Cert n’est pas une certification agréée. Les aides, priorités et réductions d’assurance ne sont pas garanties.',
        'Catalogue SMAP','Vérifier le catalogue NASA SMAP','Produit SMAP trouvé',
        'Les mesures SMAP ne sont pas reliées à votre parcelle.',
        'Sources et limites','FIRMS nécessite une clé NASA MAP_KEY gratuite dans secrets ou une variable d’environnement.',
        'Aucun message automatique n’est envoyé aux secours.','Les résultats sont exploratoires et non officiels NASA/FAO.',
        'Aucune analyse disponible pour cette parcelle.','Pas de MAP_KEY : état des points chauds inconnu.','Non connecté','Détection proche','Aucune détection','Simple suivi — aucun score ou certificat officiel.'],
 'es': ['Arquitectura y flujo de datos','Fuentes de datos','Análisis','Acciones para agricultores',
        'NASA POWER: clima','NASA FIRMS: focos satelitales (opcional)','NASA SMAP: solo búsqueda de datos',
        'FAO ECOCROP: rangos de referencia','Coordenadas y evaluación exploratoria','Paneles sencillos de cultivos, incendios y sostenibilidad',
        '1. Cultivos sugeridos para esta parcela','Cultivo','Necesidad de agua','Puntuación clima/rotación','Evaluación',
        'Baja','Media','Alta','Más favorable','Verificar localmente',
        'La puntuación 1–5 NO estima ganancias. Se necesitan precios, rendimientos y costos.',
        '2. Seguimiento de focos satelitales','Consultar FIRMS para este lugar','FIRMS no configurado',
        'Sin detecciones cercanas','Focos cercanos — consulte avisos oficiales',
        'Detecciones en 25 km','Detección más cercana','Fecha de datos',
        'Sin detección no significa seguridad. No es un pronóstico ni una notificación de emergencia.',
        'Falló la consulta; riesgo desconocido','3. Seguimiento de sostenibilidad','Lista de preparación — no es certificado',
        'Registrar uso del agua','Guardar registros de pesticidas y fertilizantes','Hacer análisis de suelo',
        'Comprobar normas locales de certificación orgánica','Pasos completados','Sin certificación',
        'ESA-Cert no es una certificación autorizada. No se confirman ayudas, prioridades ni descuentos de seguros.',
        'Catálogo SMAP','Consultar catálogo NASA SMAP','Producto SMAP encontrado',
        'SMAP no está conectado como medición de la parcela.',
        'Fuentes y notas','FIRMS necesita una MAP_KEY gratuita de NASA en secrets o variable de entorno.',
        'No se envían mensajes automáticos a emergencias.','Los resultados son exploratorios, no decisiones oficiales NASA/FAO.',
        'No hay análisis para esta parcela.','Sin MAP_KEY: estado del foco desconocido.','Sin conexión','Detección cercana','Sin detección','Solo registro — sin puntuación ni certificado oficial.'],
 'pt': ['Arquitetura e fluxo de dados','Fontes de dados','Análise','Orientação ao agricultor',
        'NASA POWER: clima','NASA FIRMS: focos de satélite (opcional)','NASA SMAP: apenas pesquisa de dados',
        'FAO ECOCROP: intervalos de referência','Coordenadas e avaliação exploratória','Painéis simples de culturas, incêndios e sustentabilidade',
        '1. Culturas para esta propriedade','Cultura','Necessidade de água','Pontuação clima/rotação','Avaliação',
        'Baixa','Média','Alta','Mais favorável','Verificar localmente',
        'A pontuação 1–5 NÃO estima lucro. São necessários preços, produção e custos.',
        '2. Monitoramento de focos por satélite','Consultar FIRMS nesta área','FIRMS não configurado',
        'Nenhuma detecção próxima','Focos próximos — confira os alertas oficiais',
        'Detecções em 25 km','Detecção mais próxima','Data dos dados',
        'Ausência de detecção não garante segurança. Não é previsão nem aviso de emergência.',
        'Falha na consulta; risco desconhecido','3. Acompanhamento da sustentabilidade','Lista de preparação — não é certificado',
        'Registrar uso de água','Guardar registros de pesticidas e adubos','Fazer análise do solo',
        'Verificar regras locais de certificação orgânica','Etapas concluídas','Não certificado',
        'ESA-Cert não é certificação oficial. Subsídios, prioridade e descontos de seguro não são confirmados.',
        'Catálogo SMAP','Consultar catálogo SMAP da NASA','Produto SMAP encontrado',
        'SMAP não está ligado a medições de umidade da fazenda.',
        'Fontes e notas','FIRMS exige MAP_KEY gratuita da NASA em secrets ou variável de ambiente.',
        'Nenhuma mensagem automática é enviada às emergências.','Resultados exploratórios, não decisões oficiais NASA/FAO.',
        'Sem análise para esta área.','Sem MAP_KEY: situação dos focos desconhecida.','Não conectado','Detecção próxima','Sem detecção','Apenas registros — sem pontuação ou certificado oficial.'],
 'zh': ['项目架构与数据流程','数据来源','分析','农户行动建议',
        'NASA POWER：气候','NASA FIRMS：卫星热点（可选）','NASA SMAP：仅查询数据目录',
        'FAO ECOCROP：作物参考范围','农田坐标及试验性评估','简洁的作物、火情和可持续性面板',
        '1. 该地块的作物建议','作物','需水程度','气候/轮作评分','评估',
        '低','中','高','更匹配','需实地核实',
        '1–5分是试验性匹配评分，不代表利润预测。计算利润还需价格、产量与成本。',
        '2. 卫星热点监测','查询本地 FIRMS','FIRMS 尚未配置',
        '附近未返回卫星热点','附近发现热点——请查看官方预警',
        '25公里内热点数','最近的热点','数据日期',
        '未探测到热点不代表安全。卫星热点不是火灾预测或紧急报警。',
        '卫星查询失败；风险未知','3. 可持续性记录','准备清单——并非证书',
        '记录用水量','保留农药与肥料使用记录','进行土壤检测',
        '检查当地有机认证要求','完成的项目','未获认证',
        'ESA-Cert不是获授权的认证；补贴、供应优先和保险折扣均未得到确认。',
        'SMAP数据目录','查询NASA SMAP目录','目录内找到SMAP产品',
        '未连接SMAP农田土壤湿度实测值。',
        '来源和限制','FIRMS需要免费的NASA MAP_KEY（secrets或环境变量）。',
        '不会自动向应急机构发送消息。','结果仅为试验性评估，并非NASA/FAO官方决定。',
        '该地块没有分析结果。','无MAP_KEY：热点状态未知。','未连接','附近有检测','未检出','仅用于记录，不颁发官方评分或证书。'],
 'ar': ['هيكل المشروع وتدفق البيانات','مصادر البيانات','التحليل','إرشادات المزارع',
        'NASA POWER: المناخ','NASA FIRMS: نقاط الحرارة الفضائية (اختياري)','NASA SMAP: البحث في الفهرس فقط',
        'FAO ECOCROP: نطاقات المحاصيل','إحداثيات المزرعة والتقييم الأولي','لوحات مبسطة للمحاصيل والحرائق والاستدامة',
        '١. محاصيل مقترحة للمزرعة','المحصول','احتياج المياه','نقاط المناخ/التناوب','التقييم',
        'منخفض','متوسط','مرتفع','مطابقة أفضل','تحقق ميدانيًا',
        'هذه نقاط تقييم أولي من ١ إلى ٥ وليست تقديرًا للربح؛ يلزم معرفة الأسعار والإنتاج والتكاليف.',
        '٢. رصد النقاط الساخنة بالأقمار الصناعية','فحص FIRMS لهذه المنطقة','FIRMS غير مُعد',
        'لم تُرصد نقاط ساخنة قريبة','نقاط ساخنة قريبة — راجع التحذيرات الرسمية',
        'رصد ضمن ٢٥ كم','أقرب رصد','تاريخ البيانات',
        'عدم الرصد لا يعني الأمان، وليس هذا توقعًا للحريق أو بلاغًا للطوارئ.',
        'فشل الاستعلام؛ مستوى الخطر غير معروف','٣. متابعة الاستدامة','قائمة استعداد وليست شهادة',
        'سجّل استخدام المياه','احتفظ بسجلات المبيدات والأسمدة','أجر تحليل التربة',
        'تحقق من قواعد الاعتماد العضوي المحلية','الخطوات المكتملة','غير معتمد',
        'ESA-Cert ليست شهادة معتمدة، ولا توجد منح أو أولوية توريد أو خصومات تأمين مؤكدة.',
        'فهرس بيانات SMAP','تحقق من فهرس NASA SMAP','عُثر على منتج SMAP في الفهرس',
        'لم تُربط قياسات رطوبة تربة SMAP بالمزرعة.',
        'المصادر والتنبيهات','يتطلب FIRMS مفتاح NASA مجانيًا MAP_KEY في secrets أو متغير البيئة.',
        'لا يتم إرسال رسائل تلقائية إلى فرق الطوارئ.','هذه النتائج أولية وليست قرارات رسمية من NASA/FAO.',
        'لا يوجد تحليل لهذه المزرعة.','لا يوجد MAP_KEY: حالة النقاط الساخنة غير معروفة.','غير متصل','رصد قريب','لا يوجد رصد','سجل متابعة فقط دون نقاط أو شهادة رسمية.'],
}


def tr(index):
    lang = get_language()
    return L.get(lang, L['en'])[index]


def _key():
    value = os.environ.get('NASA_FIRMS_MAP_KEY', '').strip()
    if value:
        return value
    try:
        return str(st.secrets.get('NASA_FIRMS_MAP_KEY', '')).strip()
    except (FileNotFoundError, RuntimeError, KeyError):
        return ''


def _distance_km(a, b, c, d):
    a, b, c, d = map(math.radians, (a, b, c, d))
    h = math.sin((a-c)/2)**2 + math.cos(a)*math.cos(c)*math.sin((b-d)/2)**2
    return 6371.0088 * 2 * math.asin(min(1, math.sqrt(h)))


def _bbox(lat, lon, radius_km=28):
    dlat = radius_km / 111.0
    dlon = min(30, radius_km / (111.0 * max(0.1, math.cos(math.radians(lat)))))
    return (max(-180, lon-dlon), max(-90, lat-dlat), min(180, lon+dlon), min(90, lat+dlat))


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_firms(lat, lon, map_key):
    """Get *actual* VIIRS detections near point. Never interpret lack as safety."""
    west, south, east, north = _bbox(lat, lon)
    bbox = f'{west:.4f},{south:.4f},{east:.4f},{north:.4f}'
    url = f'{_FIRMS_URL}/{map_key}/VIIRS_SNPP_NRT/{bbox}/2'
    response = requests.get(url, timeout=20)
    response.raise_for_status()
    raw = response.text.strip()
    if raw and ('error' in raw[:150].lower() or 'invalid map_key' in raw[:150].lower()):
        raise ValueError('FIRMS returned an API error')
    rows = []
    for record in csv.DictReader(io.StringIO(raw)):
        try:
            hlat, hlon = float(record['latitude']), float(record['longitude'])
            dist = _distance_km(lat, lon, hlat, hlon)
            if dist <= 25:
                rows.append({'latitude': hlat, 'longitude': hlon, 'distance_km': dist,
                             'date': str(record.get('acq_date', '')), 'satellite': 'VIIRS S-NPP'})
        except (KeyError, TypeError, ValueError):
            continue
    rows.sort(key=lambda x: x['distance_km'])
    return rows


@st.cache_data(ttl=86400, show_spinner=False)
def discover_smap(lat, lon):
    """CMR metadata discovery only. This does NOT download/read pixel moisture."""
    west, south, east, north = _bbox(lat, lon, 30)
    response = requests.get(_CMR_URL, params={
        'short_name': 'SPL3SMP_E', 'bounding_box': f'{west:.3f},{south:.3f},{east:.3f},{north:.3f}',
        'page_size': 1, 'sort_key': '-start_date',
    }, timeout=18)
    response.raise_for_status()
    return bool(response.json().get('feed', {}).get('entry', []))


def render_decision_panels(result, location):
    if not result or not location:
        st.info(tr(47))
        return
    lat, lon = map(float, location)
    st.markdown('''<style>
      .soe-flow{display:flex;gap:10px;align-items:stretch;flex-wrap:wrap;margin:10px 0 12px}
      .soe-flow-box{background:#122c41;border:1px solid #31596c;border-radius:13px;
        padding:15px 17px;color:#e5f7ff;flex:1;min-width:190px}
      .soe-flow-box small{color:#a5cad1;display:block;margin-top:7px;line-height:1.55}
      .soe-flow-arrow{align-self:center;font-size:23px;color:#57d3ca}
      @media(max-width:680px){.soe-flow-arrow{display:none}}
      .soe-p-title{color:#efffff;font-weight:750}
      .soe-pill{border-radius:99px;display:inline-block;padding:5px 9px;font-weight:700;font-size:.82rem}
      .soe-good{background:#12553c;color:#b5ffe1}.soe-mid{background:#5a481c;color:#ffecaf}
      .soe-muted{background:#243849;color:#d5e8f2}.soe-risk{background:#682e37;color:#ffdade}
      </style>''', unsafe_allow_html=True)
    st.subheader('🛰️ ' + tr(0))
    panels = ((tr(1), (tr(4), tr(5), tr(6))),
              (tr(2), (tr(7), tr(8))), (tr(3), (tr(9),)))
    contents = []
    for label, descriptions in panels:
        contents.append(f'<div class="soe-flow-box"><div class="soe-p-title">{escape(label)}</div>' +
                        ''.join('<small>• ' + escape(d) + '</small>' for d in descriptions) + '</div>')
    st.markdown('<div class="soe-flow">' + '<span class="soe-flow-arrow">→</span>'.join(contents) + '</div>', unsafe_allow_html=True)

    st.markdown('### 🌱 ' + tr(10))
    rows = compare_strategies(result['previous_crop'], result['soil_type'], result['seasonal'],
                              soil_ph=result.get('soil_ph'), annual_rainfall_mm=recent_annual_rainfall(result.get('annual')))[result['priority']]
    valid_scores = [r['score'] for r in rows if math.isfinite(float(r['score']))]
    low, high = min(valid_scores), max(valid_scores)
    table = []
    for row in rows:
        name = row['crop']
        score = 3 if high <= low else 1 + 4 * (row['score'] - low) / (high - low)
        score = round(score, 1)
        cls = 'soe-good' if score >= 4 else 'soe-mid' if score >= 2.6 else 'soe-muted'
        water = {'low': tr(15), 'medium': tr(16), 'high': tr(17)}[CROPS[name]['water']]
        state = tr(18) if score >= 4 else tr(19)
        # Crop names are existing internal keys; only UI displays localized names.
        from i18n import t
        table.append((t(name), water, score, state, cls))
    heads = [tr(11), tr(12), tr(13), tr(14)]
    html = '<div style="overflow-x:auto"><table style="width:100%;border-collapse:separate;border-spacing:0 5px">'
    html += '<thead><tr>' + ''.join(f'<th style="padding:10px;text-align:left;background:#10263d;color:#bee5f6">{escape(h)}</th>' for h in heads) + '</tr></thead><tbody>'
    for name, water, score, state, cls in table:
        html += (f'<tr style="background:#16334a;color:#f4fbff"><td style="padding:10px">{escape(name)}</td>'
                 f'<td>{escape(water)}</td><td><span class="soe-pill {cls}">{score:.1f}/5</span></td>'
                 f'<td>{escape(state)}</td></tr>')
    st.markdown(html + '</tbody></table></div>', unsafe_allow_html=True)
    st.caption(tr(20))

    st.markdown('### 🔥 ' + tr(21))
    key = _key()
    if not key:
        st.info(tr(48) + ' ' + tr(22))
    else:
        if st.button(tr(22), key='soe_firms_check'):
            try:
                hits = fetch_firms(lat, lon, key)
                st.session_state['soe_firms_result'] = {'location': location, 'hits': hits, 'error': None}
            except (requests.RequestException, ValueError) as error:
                st.session_state['soe_firms_result'] = {'location': location, 'hits': [], 'error': type(error).__name__}
        state = st.session_state.get('soe_firms_result', {})
        if state.get('location') == location:
            if state.get('error'):
                st.warning(tr(29))
            elif state.get('hits'):
                st.warning(tr(24))
                hits = state['hits']
                a, b, c = st.columns(3)
                a.metric(tr(25), len(hits))
                b.metric(tr(26), f"{hits[0]['distance_km']:.1f} km")
                c.metric(tr(27), hits[0]['date'])
                st.caption(f"{hits[0]['latitude']:.4f}, {hits[0]['longitude']:.4f} · VIIRS S-NPP")
            else:
                st.info(tr(23))
    st.caption(tr(28))

    st.markdown('### 🌿 ' + tr(30))
    st.caption(tr(31))
    checks = [st.checkbox(tr(i), key=f'soe_sustainability_{i}') for i in (32,33,34,35)]
    a,b = st.columns(2)
    a.metric(tr(36), f'{sum(checks)} / {len(checks)}')
    b.metric(tr(37), '—')
    st.caption(tr(38))
    st.caption(tr(50))
    with st.expander('🛰️ ' + tr(39), expanded=False):
        if st.button(tr(40), key='soe_smap_discovery'):
            try:
                has_product = discover_smap(lat, lon)
                if has_product:
                    st.success(tr(41))
                else:
                    st.info(tr(42))
            except (requests.RequestException, ValueError):
                st.warning(tr(49))
        st.caption(tr(42))
    with st.expander('📚 ' + tr(43), expanded=False):
        st.caption(tr(44))
        st.caption(tr(45))
        st.caption(tr(46))
        st.markdown('[NASA FIRMS API](https://firms.modaps.eosdis.nasa.gov/api/area) · '
                    '[NASA SMAP](https://nsidc.org/data/smap/data) · '
                    '[NASA POWER](https://power.larc.nasa.gov/) · '
                    '[FAO ECOCROP](https://www.fao.org/land-water/resources/tools/databases/ecocrop/en)')
