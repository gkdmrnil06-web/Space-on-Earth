"""Country to default UI language; country choice is not used as farm location."""
import streamlit as st
import pycountry
from babel.languages import get_official_languages

# GoogleTranslator supports most of these languages; unsupported codes use English.
SUPPORTED = {
    "af", "sq", "am", "ar", "hy", "az", "eu", "be", "bn", "bs", "bg", "ca",
    "zh", "hr", "cs", "da", "nl", "en", "et", "fi", "fr", "gl", "ka", "de",
    "el", "gu", "ht", "he", "hi", "hu", "is", "id", "ga", "it", "ja", "kn",
    "kk", "km", "ko", "ku", "ky", "lo", "lv", "lt", "mk", "ms", "ml", "mt",
    "mr", "mn", "my", "ne", "no", "fa", "pl", "pt", "pa", "ro", "ru", "sr",
    "si", "sk", "sl", "so", "es", "sw", "sv", "ta", "te", "th", "tr", "uk",
    "ur", "uz", "vi", "cy", "yi", "zu", "fil", "ps", "sd", "tg", "tk", "ug"
}

ALIASES = {
    "zh_Hans": "zh", "zh_Hant": "zh", "nb": "no", "nn": "no",
    "iw": "he", "in": "id", "tl": "fil", "mo": "ro", "sh": "sr",
    "yue": "zh", "zho": "zh", "cmn": "zh"
}

COUNTRIES = {country.alpha_2: country.name for country in pycountry.countries}
COUNTRIES["TR"] = "Türkiye"
COUNTRIES["CN"] = "China / 中国"
COUNTRIES["US"] = "United States"
COUNTRIES["IN"] = "India / भारत"


def default_language(country_code):
    overrides = {"TR": "tr", "CN": "zh", "TW": "zh", "HK": "zh",
                 "IN": "hi", "BR": "pt", "MX": "es", "US": "en",
                 "GB": "en", "CA": "en", "CH": "de", "BE": "nl"}
    if country_code in overrides:
        return overrides[country_code]
    for value in get_official_languages(country_code, de_facto=True):
        value = ALIASES.get(value, value.split("_")[0])
        if value in SUPPORTED:
            return value
    return "en"


def render_country_selector():
    from i18n import t, translation_backend_status

    codes = sorted(COUNTRIES, key=lambda code: COUNTRIES[code].casefold())
    if "ui_country" not in st.session_state:
        st.session_state["ui_country"] = "TR" if st.session_state.get("ui_language") == "tr" else "US"
    if "ui_override" not in st.session_state or st.session_state["ui_override"] not in (["auto"] + sorted(SUPPORTED)):
        st.session_state["ui_override"] = "auto"

    def synchronize_language():
        selected = st.session_state["ui_country"]
        choice = st.session_state["ui_override"]
        st.session_state["ui_language"] = default_language(selected) if choice == "auto" else choice
        st.session_state.pop("translation_error", None)

    def on_country_change():
        # A new country means the country default should be applied immediately.
        # The farmer can select a manual override again afterward.
        st.session_state['ui_override'] = 'auto'
        synchronize_language()

    # Resolve before rendering ANY translated text, including the sidebar title.
    synchronize_language()
    with st.sidebar:
        st.markdown("### 🌐 " + t("Country & language"))
        st.selectbox(t("Country"), codes, format_func=lambda code: COUNTRIES[code],
                     key="ui_country", on_change=on_country_change)
        st.selectbox(t("Language override (optional)"), ["auto"] + sorted(SUPPORTED),
                     key="ui_override",
                     format_func=lambda code: "Auto (" + default_language(st.session_state["ui_country"]) + ")" if code == "auto" else code,
                     on_change=synchronize_language)
        st.caption(t("Language:") + " " + st.session_state["ui_language"] + " · " +
                   t("Farm location is chosen separately on the map."))
        language = st.session_state["ui_language"]
        if language != "en":
            status = translation_backend_status()
            if status.get('online_cooldown'):
                st.caption(t('Online translation is temporarily unavailable. Saved translations remain active.'))
            # Install an optional offline model only when the farmer requests it.
            with st.expander('📥 ' + t('Offline language model (optional)'), expanded=False):
                st.caption(t('No account or payment is required. Model availability varies by language.'))
                if st.button(t('Download model for selected language'), key='download_offline_model'):
                    from free_translation import install_offline_model
                    with st.spinner('Downloading a free language model...'):
                        success, message = install_offline_model(language)
                    if success:
                        st.success(message)
                    else:
                        st.warning(message)
