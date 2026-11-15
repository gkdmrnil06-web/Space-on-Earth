"""References footer for Space on Earth. URLs verified against providers in Nov 2026.

No external data is fetched by this module; hyperlinks are informational.
"""
import streamlit as st
from i18n import get_language, t

LABELS = {'en': {'header': 'References & Data Sources', 'nasa': 'NASA DATA', 'other': 'OTHER DATA & TOOLS', 'ai': 'ARTIFICIAL INTELLIGENCE (AI) USE', 'method': 'METHOD & LIMITATIONS', 'nasa_daily': 'Historical daily temperature, precipitation, humidity and wind at the selected coordinates.', 'nasa_params': 'Official meanings and units of the NASA POWER data parameters.', 'nasa_soil': 'Surface soil moisture (SFMC) and relative soil wetness (GWETTOP) are different measurements.', 'fao': 'Crop environmental reference ranges; project values are kept in a local CSV, not fetched live from FAO.', 'isric': 'Modeled soil properties and pH estimates; not a laboratory soil test.', 'meteo': 'Optional 16-day weather forecasts; these are not NASA observations.', 'osm': 'OpenStreetMap base-map data and contributor attribution.', 'esri': 'Optional Esri World Imagery satellite-map tiles and attribution.', 'leaflet': 'Interactive map display software.', 'ai_statement': 'OpenAI ChatGPT assisted with project brainstorming, code drafting, interface text, translation and review. Some logo concepts were AI-generated. The team is responsible for checking outputs and the final submission.', 'limits1': 'NASA POWER provides gridded historical data, not direct field-sensor measurements or guaranteed forecasts.', 'limits2': 'Crop rankings, sowing/harvest windows and field-check alerts are exploratory calculations made by Space on Earth, not official NASA or FAO recommendations.', 'limits3': 'Missing readings are not replaced with invented values. Confirm soil, pests, product labels and local requirements before taking field action.', 'local_note': 'Crop thresholds and model assumptions require further validation against primary agricultural records.'}, 'tr': {'header': 'Kaynakça ve Veri Kaynakları', 'nasa': 'NASA VERİLERİ', 'other': 'DİĞER VERİLER VE ARAÇLAR', 'ai': 'YAPAY ZEKÂ (AI) KULLANIMI', 'method': 'YÖNTEM VE SINIRLAMALAR', 'nasa_daily': 'Seçilen koordinatın geçmiş günlük sıcaklık, yağış, nem ve rüzgâr verileri.', 'nasa_params': 'NASA POWER parametrelerinin resmî anlamları ve birimleri.', 'nasa_soil': 'Yüzey toprağı nemi (SFMC) ile göreli toprak ıslaklığı (GWETTOP) farklı ölçümlerdir.', 'fao': 'Ürünlerin çevresel referans aralıkları; uygulamadaki değerler FAO’dan canlı alınmaz, yerel CSV dosyasındadır.', 'isric': 'Modellenmiş toprak özellikleri ve pH tahminleri; laboratuvar toprak testi değildir.', 'meteo': 'İsteğe bağlı 16 günlük hava tahmini; NASA gözlemi değildir.', 'osm': 'OpenStreetMap altlık harita verileri ve katkıda bulunanların atıfları.', 'esri': 'İsteğe bağlı Esri World Imagery uydu görüntüsü katmanı ve kaynak atfı.', 'leaflet': 'Etkileşimli harita görüntüleme yazılımı.', 'ai_statement': 'OpenAI ChatGPT; proje fikri, kod taslağı, arayüz metinleri, çeviri ve gözden geçirme aşamalarında yardımcı oldu. Bazı logo taslakları AI ile üretildi. Çıktıların ve nihai teslimin doğruluğundan ekip sorumludur.', 'limits1': 'NASA POWER doğrudan tarla sensörü ölçümü veya garantili tahmin değil, geçmiş grid tabanlı veriler sağlar.', 'limits2': 'Ürün sıralamaları, ekim/hasat aralıkları ve saha uyarıları Space on Earth’ün deneysel hesaplamalarıdır; resmî NASA veya FAO önerileri değildir.', 'limits3': 'Eksik ölçümler uydurulmaz. Uygulama öncesinde toprak, zararlı, ürün etiketleri ve yerel şartlar doğrulanmalıdır.', 'local_note': 'Ürün eşikleri ve model varsayımlarının birincil tarımsal kayıtlarla ayrıca doğrulanması gerekir.'}, 'ja': {'header': '参考資料とデータソース', 'nasa': 'NASAデータ', 'other': 'その他のデータとツール', 'ai': '人工知能（AI）の利用', 'method': '手法と限界', 'nasa_daily': '選択地点の過去の日別気温、降水量、湿度、風速データ。', 'nasa_params': 'NASA POWERのデータ項目の公式な定義と単位。', 'nasa_soil': '表層土壌水分（SFMC）と相対的な土壌湿潤度（GWETTOP）は異なる指標です。', 'fao': '作物の環境条件の参考範囲。アプリの値はFAOからリアルタイム取得せず、ローカルCSVに保存しています。', 'isric': '推定された土壌特性とpH。現地の土壌検査結果ではありません。', 'meteo': '任意の16日間天気予報。NASAの観測値ではありません。', 'osm': 'OpenStreetMapの背景地図データと貢献者表示。', 'esri': '任意で表示するEsri World Imagery衛星画像と出典表記。', 'leaflet': 'インタラクティブな地図表示ソフトウェア。', 'ai_statement': 'OpenAI ChatGPTをアイデア出し、コード草案、画面文言、翻訳、レビューに利用しました。一部のロゴ案はAIで生成しました。内容の確認と最終提出についてはチームが責任を負います。', 'limits1': 'NASA POWERは格子状の過去データであり、農地センサーの実測値や確実な予報ではありません。', 'limits2': '作物の順位、播種・収穫期間、現地確認の注意喚起はSpace on Earth独自の試験的計算であり、NASAやFAOの公式推奨ではありません。', 'limits3': '欠損データを捏造しません。現場で作業する前に土壌、害虫、製品ラベル、地域の要件を確認してください。', 'local_note': '作物の閾値とモデルの仮定は、一次資料との追加照合が必要です。'}, 'fr': {'header': 'Références et sources de données', 'nasa': 'DONNÉES NASA', 'other': 'AUTRES DONNÉES ET OUTILS', 'ai': 'UTILISATION DE L’INTELLIGENCE ARTIFICIELLE (IA)', 'method': 'MÉTHODE ET LIMITES', 'nasa_daily': 'Données quotidiennes historiques de température, précipitations, humidité et vent aux coordonnées choisies.', 'nasa_params': 'Définitions officielles et unités des paramètres NASA POWER.', 'nasa_soil': 'L’humidité volumique de surface (SFMC) et l’indice relatif d’humidité du sol (GWETTOP) sont différents.', 'fao': 'Plages de référence environnementales des cultures ; les valeurs du projet sont conservées dans un CSV local, sans requête FAO en direct.', 'isric': 'Estimations modélisées des propriétés du sol et du pH ; pas des analyses de laboratoire.', 'meteo': 'Prévisions météo facultatives sur 16 jours ; ce ne sont pas des observations NASA.', 'osm': 'Fond de carte OpenStreetMap et mention des contributeurs.', 'esri': 'Imagerie satellite Esri World Imagery facultative et attribution.', 'leaflet': 'Logiciel d’affichage de carte interactive.', 'ai_statement': 'OpenAI ChatGPT a aidé à concevoir le projet, rédiger du code, écrire l’interface, traduire et relire. Certaines propositions de logo ont été générées par IA. L’équipe reste responsable des vérifications et de la soumission finale.', 'limits1': 'NASA POWER fournit des données historiques maillées, et non des mesures directes sur la parcelle ni des prévisions garanties.', 'limits2': 'Classements des cultures, périodes de semis/récolte et alertes de terrain sont des calculs exploratoires de Space on Earth, non des recommandations officielles NASA ou FAO.', 'limits3': 'Aucune donnée manquante n’est inventée. Vérifiez le sol, les ravageurs, les étiquettes et les exigences locales avant toute intervention.', 'local_note': 'Les seuils des cultures et les hypothèses du modèle nécessitent une vérification supplémentaire auprès de sources agricoles primaires.'}, 'de': {'header': 'Quellen und Datengrundlagen', 'nasa': 'NASA-DATEN', 'other': 'WEITERE DATEN UND WERKZEUGE', 'ai': 'EINSATZ KÜNSTLICHER INTELLIGENZ (KI)', 'method': 'METHODIK UND GRENZEN', 'nasa_daily': 'Historische Tagesdaten zu Temperatur, Niederschlag, Luftfeuchtigkeit und Wind am gewählten Ort.', 'nasa_params': 'Offizielle Definitionen und Einheiten der NASA-POWER-Parameter.', 'nasa_soil': 'Oberflächenbodenfeuchte (SFMC) und relative Bodennässe (GWETTOP) sind unterschiedliche Größen.', 'fao': 'Umweltbezogene Referenzbereiche für Kulturpflanzen; die Werte liegen lokal als CSV vor und werden nicht live von FAO abgerufen.', 'isric': 'Modellierte Bodeneigenschaften und pH-Schätzungen; keine Labor-Bodenanalyse.', 'meteo': 'Optionale 16-Tage-Wettervorhersage; keine NASA-Beobachtungen.', 'osm': 'OpenStreetMap-Kartendaten mit Quellenangabe.', 'esri': 'Optionale Satellitenbild-Kacheln von Esri World Imagery mit Quellenangabe.', 'leaflet': 'Software zur interaktiven Kartendarstellung.', 'ai_statement': 'OpenAI ChatGPT unterstützte Ideenfindung, Codeentwürfe, UI-Texte, Übersetzung und Überprüfung. Einige Logoentwürfe wurden mit KI erstellt. Für Prüfung und Endfassung ist das Team verantwortlich.', 'limits1': 'NASA POWER liefert historische Rasterdaten, keine direkten Feldsensormessungen oder garantierten Prognosen.', 'limits2': 'Pflanzenranglisten, Aussaat-/Erntefenster und Feldhinweise sind experimentelle Berechnungen von Space on Earth, keine offiziellen Empfehlungen von NASA oder FAO.', 'limits3': 'Fehlende Messwerte werden nicht erfunden. Vor Maßnahmen Boden, Schädlinge, Produktetiketten und lokale Vorschriften prüfen.', 'local_note': 'Grenzwerte für Kulturen und Modellannahmen müssen zusätzlich anhand landwirtschaftlicher Primärquellen geprüft werden.'}, 'es': {'header': 'Referencias y fuentes de datos', 'nasa': 'DATOS DE LA NASA', 'other': 'OTROS DATOS Y HERRAMIENTAS', 'ai': 'USO DE INTELIGENCIA ARTIFICIAL (IA)', 'method': 'MÉTODO Y LIMITACIONES', 'nasa_daily': 'Datos históricos diarios de temperatura, precipitación, humedad y viento para las coordenadas elegidas.', 'nasa_params': 'Definiciones y unidades oficiales de los parámetros de NASA POWER.', 'nasa_soil': 'La humedad superficial (SFMC) y la humedad relativa del suelo (GWETTOP) son medidas distintas.', 'fao': 'Rangos ambientales de referencia para cultivos; los valores se guardan en un CSV local, sin consultas en directo a FAO.', 'isric': 'Estimaciones modeladas de propiedades y pH del suelo; no son análisis de laboratorio.', 'meteo': 'Pronóstico meteorológico opcional de 16 días; no son observaciones de la NASA.', 'osm': 'Mapa base de OpenStreetMap y atribución a sus colaboradores.', 'esri': 'Imágenes satelitales opcionales de Esri World Imagery con atribución.', 'leaflet': 'Software de mapas interactivos.', 'ai_statement': 'OpenAI ChatGPT ayudó con ideas, borradores de código, textos de interfaz, traducciones y revisión. Algunos conceptos de logotipo se generaron con IA. El equipo es responsable de verificar el contenido y de la entrega final.', 'limits1': 'NASA POWER proporciona datos históricos en cuadrícula, no mediciones directas de sensores agrícolas ni pronósticos garantizados.', 'limits2': 'Las clasificaciones de cultivos, ventanas de siembra/cosecha y avisos de campo son cálculos experimentales de Space on Earth, no recomendaciones oficiales de NASA o FAO.', 'limits3': 'No se inventan datos faltantes. Verifica el suelo, las plagas, las etiquetas y los requisitos locales antes de intervenir.', 'local_note': 'Los umbrales de cultivos y los supuestos del modelo requieren validación adicional con fuentes agrícolas primarias.'}, 'pt': {'header': 'Referências e fontes de dados', 'nasa': 'DADOS DA NASA', 'other': 'OUTROS DADOS E FERRAMENTAS', 'ai': 'USO DE INTELIGÊNCIA ARTIFICIAL (IA)', 'method': 'MÉTODO E LIMITAÇÕES', 'nasa_daily': 'Dados diários históricos de temperatura, precipitação, humidade e vento nas coordenadas escolhidas.', 'nasa_params': 'Definições e unidades oficiais dos parâmetros NASA POWER.', 'nasa_soil': 'A humidade volumétrica superficial (SFMC) e a humidade relativa do solo (GWETTOP) são medidas diferentes.', 'fao': 'Intervalos ambientais de referência das culturas; os valores ficam num CSV local e não são obtidos da FAO em tempo real.', 'isric': 'Estimativas modeladas de propriedades do solo e pH; não são análises laboratoriais.', 'meteo': 'Previsão meteorológica opcional de 16 dias; não são observações da NASA.', 'osm': 'Mapa base do OpenStreetMap com atribuição aos colaboradores.', 'esri': 'Imagens de satélite opcionais do Esri World Imagery com atribuição.', 'leaflet': 'Software de visualização de mapas interativos.', 'ai_statement': 'O OpenAI ChatGPT apoiou a conceção do projeto, rascunhos de código, textos da interface, traduções e revisão. Alguns conceitos de logótipo foram gerados por IA. A equipa é responsável pela verificação e entrega final.', 'limits1': 'A NASA POWER fornece dados históricos em grelha, não medições diretas de sensores agrícolas nem previsões garantidas.', 'limits2': 'Classificações de culturas, períodos de sementeira/colheita e alertas de campo são cálculos exploratórios do Space on Earth, não recomendações oficiais da NASA ou da FAO.', 'limits3': 'Os dados em falta não são inventados. Verifique solo, pragas, rótulos dos produtos e regras locais antes de agir.', 'local_note': 'Os limites das culturas e os pressupostos do modelo precisam de validação adicional em fontes agrícolas primárias.'}, 'zh': {'header': '参考资料与数据来源', 'nasa': 'NASA 数据', 'other': '其他数据与工具', 'ai': '人工智能（AI）使用说明', 'method': '方法与局限', 'nasa_daily': '所选坐标的历史每日气温、降水、湿度和风速数据。', 'nasa_params': 'NASA POWER 数据参数的官方定义与单位。', 'nasa_soil': '表层土壤含水量（SFMC）与相对土壤湿润度（GWETTOP）是不同的指标。', 'fao': '作物环境条件参考范围；项目数值保存在本地 CSV 中，并非实时从 FAO 获取。', 'isric': '土壤属性与 pH 的模型估计，不是实验室检测结果。', 'meteo': '可选的 16 天天气预报；并非 NASA 观测值。', 'osm': 'OpenStreetMap 底图数据和贡献者署名。', 'esri': '可选的 Esri World Imagery 卫星影像与来源署名。', 'leaflet': '交互式地图展示软件。', 'ai_statement': '项目使用 OpenAI ChatGPT 辅助构思、代码草稿、界面文案、翻译及审查。部分标志方案由 AI 生成。团队负责核查输出和最终提交。', 'limits1': 'NASA POWER 提供网格化历史数据，并非田间传感器实测值，也不能保证未来预报。', 'limits2': '作物排序、播种与收获时段、田间提醒均为 Space on Earth 的探索性计算，不是 NASA 或 FAO 的官方建议。', 'limits3': '不会编造缺失的数据。实际操作前请核查土壤、病虫害、产品标签及当地要求。', 'local_note': '作物阈值和模型假设仍需与原始农业资料进一步核对。'}, 'ar': {'header': 'المراجع ومصادر البيانات', 'nasa': 'بيانات ناسا', 'other': 'البيانات والأدوات الأخرى', 'ai': 'استخدام الذكاء الاصطناعي', 'method': 'المنهجية والقيود', 'nasa_daily': 'بيانات تاريخية يومية لدرجة الحرارة والهطول والرطوبة والرياح عند الإحداثيات المختارة.', 'nasa_params': 'التعريفات والوحدات الرسمية لمتغيرات NASA POWER.', 'nasa_soil': 'رطوبة التربة السطحية (SFMC) ودرجة ابتلال التربة النسبية (GWETTOP) مؤشران مختلفان.', 'fao': 'نطاقات مرجعية للظروف البيئية للمحاصيل؛ القيم مخزنة في ملف CSV محلي ولا تُجلب مباشرة من الفاو.', 'isric': 'تقديرات نموذجية لخصائص التربة ودرجة الحموضة، وليست نتائج فحص مخبري.', 'meteo': 'توقعات جوية اختيارية لمدة 16 يوماً؛ ليست قياسات من ناسا.', 'osm': 'بيانات الخريطة الأساسية من OpenStreetMap مع نسب الفضل للمساهمين.', 'esri': 'صور أقمار صناعية اختيارية من Esri World Imagery مع ذكر المصدر.', 'leaflet': 'برنامج لعرض الخرائط التفاعلية.', 'ai_statement': 'استُخدم OpenAI ChatGPT للمساعدة في الأفكار ومسودات البرمجة ونصوص الواجهة والترجمة والمراجعة. أُنتجت بعض أفكار الشعار بالذكاء الاصطناعي. يتحمل الفريق مسؤولية التحقق والتسليم النهائي.', 'limits1': 'توفر NASA POWER بيانات تاريخية شبكية، وليست قياسات مباشرة من حساسات الحقل أو توقعات مضمونة.', 'limits2': 'تصنيفات المحاصيل وفترات الزراعة والحصاد والتنبيهات الميدانية حسابات تجريبية من Space on Earth وليست توصيات رسمية من ناسا أو الفاو.', 'limits3': 'لا تُختلق القيم المفقودة. تحقّق من التربة والآفات وملصقات المنتجات والمتطلبات المحلية قبل أي إجراء.', 'local_note': 'تحتاج حدود المحاصيل وافتراضات النموذج إلى تحقق إضافي من المصادر الزراعية الأصلية.'}}


# Only providers and libraries used by the project are listed below.
# NASA FIRMS and standalone SMAP endpoints are not active integrations.
GROUPS = (
    ('nasa', (
        ('NASA POWER — Daily API', 'nasa_daily', 'https://power.larc.nasa.gov/docs/services/api/temporal/daily/'),
        ('NASA POWER — Parameter Dictionary', 'nasa_params', 'https://power.larc.nasa.gov/parameters/'),
        ('NASA POWER — Hydrology Sources', 'nasa_soil', 'https://power.larc.nasa.gov/docs/methodology/data/sources_hydrology/'),
    )),
    ('agriculture', (
        ('FAO ECOCROP', 'fao', 'https://www.fao.org/land-water/resources/tools/databases/ecocrop/en'),
        ('OpenCLIM — EcoCrop_DB.csv', 'openclim', 'https://github.com/OpenCLIM/ecocrop/blob/main/EcoCrop_DB.csv'),
        ('ISRIC SoilGrids', 'isric', 'https://docs.isric.org/globaldata/soilgrids/'),
    )),
    ('geography', (
        ('OpenStreetMap — Attribution', 'osm', 'https://www.openstreetmap.org/copyright'),
        ('Nominatim — Reverse Geocoding', 'nominatim', 'https://nominatim.org/release-docs/5.0/api/Reverse/'),
        ('Natural Earth — 1:110m Land', 'naturalearth', 'https://www.naturalearthdata.com/downloads/110m-physical-vectors/'),
        ('NOAA / University of Hawaiʻi — GSHHG', 'gshhg', 'https://www.ngdc.noaa.gov/mgg/shorelines/shorelines.html'),
        ('Esri World Imagery', 'esri', 'https://doc.arcgis.com/en/data-appliance/2025/maps/world-imagery.htm'),
    )),
    ('forecast', (
        ('Open-Meteo — Forecast API', 'meteo', 'https://open-meteo.com/en/docs'),
    )),
    ('software', (
        ('Streamlit', 'streamlit', 'https://docs.streamlit.io/'),
        ('Folium', 'folium', 'https://python-visualization.github.io/folium/latest/'),
        ('Leaflet', 'leaflet', 'https://leafletjs.com/'),
        ('Plotly', 'plotly', 'https://plotly.com/python/'),
        ('Shapely', 'shapely', 'https://shapely.readthedocs.io/'),
    )),
)

# Additional descriptions are authored offline in all eight built-in UI languages.
# All providers' proper names and link destinations are unchanged by translation.
EXTRA = {
'en': {'agriculture':'AGRICULTURAL & SOIL DATA','geography':'MAPS, LOCATION & WATER BOUNDARIES','forecast':'WEATHER FORECAST','software':'SOFTWARE & VISUALIZATION',
'openclim':'Published FAO ECOCROP database copy referenced by the project’s local crop CSV; individual crop values are not independently validated.',
'nominatim':'Uses OpenStreetMap data for address searches and approximate reverse-location checks; not proof that a point is farmland.',
'naturalearth':'Coarse offline land polygons used to screen out open seas and oceans.',
'gshhg':'Locally bundled lake-water polygons used to detect selected inland waters; small lakes may be missing.',
'streamlit':'Web app interface framework.','folium':'Python map rendering toolkit built on Leaflet.','plotly':'Interactive climate charts.','shapely':'Geometric checks for land and water boundaries.',
'footnote':'Some links document software rather than supply measurements. NASA POWER soil wetness is not an on-site sensor. Esri imagery is not NASA imagery.',
'scope':'Sources reflect the features actually used in this version. NASA FIRMS, a standalone SMAP API, official certification and financial-profit forecasts are not active features.'},
'tr': {'agriculture':'TARIMSAL VE TOPRAK VERİLERİ','geography':'HARİTA, KONUM VE SU SINIRLARI','forecast':'HAVA TAHMİNİ','software':'YAZILIM VE GÖRSELLEŞTİRME',
'openclim':'Projenin yerel ürün CSV dosyasında referans verilen FAO ECOCROP veri kopyası; her ürün değeri ayrıca doğrulanmış değildir.',
'nominatim':'Adres araması ve yaklaşık konum kontrolü için OpenStreetMap verisini kullanır; noktanın tarla olduğunu kanıtlamaz.',
'naturalearth':'Açık deniz ve okyanusları ayırmak için kullanılan çevrimdışı genel kara sınırları.',
'gshhg':'Bazı göllerin su alanlarını ayırmak için yerel olarak eklenen poligonlar; küçük göller eksik olabilir.',
'streamlit':'Web uygulamasının arayüz altyapısı.','folium':'Leaflet tabanlı Python harita aracı.','plotly':'Etkileşimli iklim grafikleri.','shapely':'Kara ve su sınırlarının geometrik kontrolü.',
'footnote':'Bazı bağlantılar veri değil yazılım kaynağıdır. NASA POWER toprak ıslaklığı tarla sensörü değildir. Esri görüntüleri NASA uydusu olarak sunulmaz.',
'scope':'Kaynaklar bu sürümde gerçekten kullanılan özellikleri kapsar. NASA FIRMS, bağımsız SMAP API, resmî sertifika ve gerçek kâr tahmini aktif değildir.'},
'ja': {'agriculture':'農業・土壌データ','geography':'地図・位置・水域境界','forecast':'天気予報','software':'ソフトウェアと可視化',
'openclim':'ローカル作物CSVの根拠となるFAO ECOCROPの公開コピー。個々の作物値はすべて独立検証済みではありません。',
'nominatim':'OpenStreetMapによる住所検索・周辺位置の確認。農地であることの証明ではありません。',
'naturalearth':'海や大洋を判別するオフラインの概略陸地境界。',
'gshhg':'一部の湖を判別するローカルの水域ポリゴン。小さな湖は含まれない場合があります。',
'streamlit':'ウェブアプリの画面基盤。','folium':'Leafletを利用したPython地図ツール。','plotly':'操作可能な気候グラフ。','shapely':'陸地と水域の幾何学的判定。',
'footnote':'一部のリンクは観測データではなくソフトウェアの出典です。NASA POWERの土壌湿潤度は現地センサーの測定値ではありません。Esri画像はNASA画像ではありません。',
'scope':'この版で実際に利用する出典のみ記載。NASA FIRMS、独立したSMAP API、公式認証、実利益予測は稼働していません。'},
'fr': {'agriculture':'DONNÉES AGRICOLES ET DES SOLS','geography':'CARTES, LOCALISATION ET EAUX','forecast':'PRÉVISIONS MÉTÉO','software':'LOGICIELS ET VISUALISATION',
'openclim':'Copie publique FAO ECOCROP utilisée comme référence du CSV local; chaque valeur n’a pas été vérifiée indépendamment.',
'nominatim':'Recherche d’adresse et vérification approximative via OpenStreetMap; ne prouve pas qu’un lieu est agricole.',
'naturalearth':'Polygones terrestres généraux hors ligne pour distinguer mers et océans.',
'gshhg':'Polygones locaux de lacs pour détecter certaines eaux intérieures; de petits lacs peuvent manquer.',
'streamlit':'Framework de l’interface web.','folium':'Outil Python de cartes fondé sur Leaflet.','plotly':'Graphiques climatiques interactifs.','shapely':'Vérification géométrique des terres et eaux.',
'footnote':'Certains liens documentent des logiciels et non des mesures. L’humidité NASA POWER n’est pas un capteur sur place. Les images Esri ne sont pas des images NASA.',
'scope':'Seules les sources effectivement utilisées sont listées. NASA FIRMS, API SMAP indépendante, certification officielle et prévisions de profit ne sont pas actives.'},
'de': {'agriculture':'LANDWIRTSCHAFTS- UND BODENDATEN','geography':'KARTEN, STANDORT UND WASSERGRENZEN','forecast':'WETTERVORHERSAGE','software':'SOFTWARE UND VISUALISIERUNG',
'openclim':'Öffentliche FAO-ECOCROP-Kopie als Quelle der lokalen Kulturpflanzen-CSV; einzelne Werte sind nicht unabhängig validiert.',
'nominatim':'Adresssuche und ungefähre Standortprüfung über OpenStreetMap; kein Nachweis für Ackerland.',
'naturalearth':'Offline-Landpolygone zur groben Unterscheidung von Land und offenem Meer.',
'gshhg':'Lokal gespeicherte Seepolygone zur Erkennung einiger Binnengewässer; kleine Seen können fehlen.',
'streamlit':'Framework für die Weboberfläche.','folium':'Python-Kartenwerkzeug auf Leaflet-Basis.','plotly':'Interaktive Klimadiagramme.','shapely':'Geometrische Land-Wasser-Prüfung.',
'footnote':'Manche Links dokumentieren Software statt Messdaten. NASA-POWER-Bodenfeuchte ist keine Feldsensormessung. Esri-Bilder sind keine NASA-Aufnahmen.',
'scope':'Nur tatsächlich eingesetzte Quellen sind aufgeführt. NASA FIRMS, eine eigenständige SMAP-API, amtliche Zertifizierung und Gewinnprognosen sind nicht aktiv.'},
'es': {'agriculture':'DATOS AGRÍCOLAS Y DEL SUELO','geography':'MAPAS, UBICACIÓN Y LÍMITES DE AGUA','forecast':'PRONÓSTICO DEL TIEMPO','software':'SOFTWARE Y VISUALIZACIÓN',
'openclim':'Copia pública de FAO ECOCROP utilizada para el CSV local; no se ha verificado cada valor por separado.',
'nominatim':'Búsqueda de direcciones y comprobación aproximada con OpenStreetMap; no prueba que haya tierras agrícolas.',
'naturalearth':'Polígonos terrestres generales sin conexión para distinguir mares y océanos.',
'gshhg':'Polígonos locales de lagos para detectar ciertas aguas interiores; pueden faltar lagos pequeños.',
'streamlit':'Plataforma de interfaz web.','folium':'Herramienta de mapas Python basada en Leaflet.','plotly':'Gráficos climáticos interactivos.','shapely':'Comprobación geométrica de límites terrestres y acuáticos.',
'footnote':'Algunos enlaces son de software y no de datos. La humedad de NASA POWER no procede de un sensor de campo. Las imágenes Esri no son imágenes NASA.',
'scope':'Se citan fuentes usadas en esta versión. NASA FIRMS, API SMAP independiente, certificación oficial y predicción de beneficios no están activas.'},
'pt': {'agriculture':'DADOS AGRÍCOLAS E DO SOLO','geography':'MAPAS, LOCALIZAÇÃO E ÁGUAS','forecast':'PREVISÃO DO TEMPO','software':'SOFTWARE E VISUALIZAÇÃO',
'openclim':'Cópia publicada da FAO ECOCROP usada como referência do CSV local; os valores não foram todos validados individualmente.',
'nominatim':'Pesquisa de endereços e verificação aproximada via OpenStreetMap; não comprova terreno agrícola.',
'naturalearth':'Polígonos terrestres gerais offline para distinguir mares e oceanos.',
'gshhg':'Polígonos locais de lagos para identificar algumas águas interiores; pequenos lagos podem faltar.',
'streamlit':'Estrutura da interface web.','folium':'Ferramenta de mapas Python baseada em Leaflet.','plotly':'Gráficos climáticos interativos.','shapely':'Verificação geométrica dos limites de terra e água.',
'footnote':'Alguns links documentam software, não medições. A humidade NASA POWER não é um sensor no campo. Imagens Esri não são imagens NASA.',
'scope':'Apenas fontes usadas nesta versão. NASA FIRMS, API SMAP autónoma, certificação oficial e previsões de lucro não estão ativas.'},
'zh': {'agriculture':'农业和土壤数据','geography':'地图、位置与水域边界','forecast':'天气预报','software':'软件与可视化',
'openclim':'本地作物CSV所参考的FAO ECOCROP公开副本；各作物参数尚未全部独立核实。',
'nominatim':'借助OpenStreetMap搜索地址并大致核对位置；不能证明该处是农田。',
'naturalearth':'用于区分陆地和外海的离线粗略陆地边界。',
'gshhg':'检测部分内陆湖泊的本地水域多边形；可能缺少小湖泊。',
'streamlit':'网页应用界面框架。','folium':'基于Leaflet的Python地图工具。','plotly':'交互式气候图表。','shapely':'陆地和水域边界的几何检查。',
'footnote':'部分链接属于软件而非观测数据。NASA POWER土壤湿润度不是田间传感器测量。Esri影像不属于NASA影像。',
'scope':'仅列出本版本实际使用的来源。NASA FIRMS、独立SMAP API、官方认证及利润预测并未启用。'},
'ar': {'agriculture':'بيانات الزراعة والتربة','geography':'الخرائط والمواقع وحدود المياه','forecast':'توقعات الطقس','software':'البرمجيات والرسوم التفاعلية',
'openclim':'نسخة منشورة من بيانات FAO ECOCROP يُستند إليها في ملف المحاصيل المحلي؛ لم تُراجع كل قيمة بصورة مستقلة.',
'nominatim':'بحث العناوين والتحقق التقريبي باستخدام OpenStreetMap؛ لا يثبت أن الموقع أرض زراعية.',
'naturalearth':'حدود برية عامة محفوظة محلياً للتمييز بين اليابسة والبحار المفتوحة.',
'gshhg':'مضلعات بحيرات محلية لتحديد بعض المياه الداخلية؛ قد تغيب البحيرات الصغيرة.',
'streamlit':'إطار عمل واجهة الويب.','folium':'أداة خرائط بايثون مبنية على Leaflet.','plotly':'رسوم مناخية تفاعلية.','shapely':'فحص هندسي لحدود البر والمياه.',
'footnote':'بعض الروابط توثق البرمجيات لا القياسات. رطوبة NASA POWER ليست قياس مستشعر حقلياً. صور Esri ليست صور ناسا.',
'scope':'القائمة تخص مصادر هذه النسخة فقط. NASA FIRMS وواجهة SMAP المستقلة والشهادات الرسمية وتوقعات الأرباح ليست ميزات مفعلة.'},
}

def _label(key):
    lang = get_language()
    if key in LABELS.get(lang, {}):
        return LABELS[lang][key]
    if key in EXTRA.get(lang, {}):
        return EXTRA[lang][key]
    # For languages without a built-in dictionary, preserve best-effort translation.
    return t(LABELS['en'].get(key, EXTRA['en'].get(key, key)))

def render_references_footer():
    st.divider()
    with st.expander('📚 ' + _label('header'), expanded=False):
        for section, entries in GROUPS:
            st.markdown('#### ' + _label(section))
            for title, key, url in entries:
                st.markdown(f'- **[{title}]({url})** — {_label(key)}')
        st.markdown('#### ' + _label('method'))
        for key in ('limits1', 'limits2', 'limits3', 'local_note', 'footnote', 'scope'):
            st.write(_label(key))
