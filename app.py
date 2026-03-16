import streamlit as st
import google.generativeai as genai
import os
from scraper import get_news

st.set_page_config(page_title="AI Stratejik Haber Paneli", page_icon="🤖", layout="wide")

# API Anahtarı Ayarları
env_api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

with st.sidebar:
    st.header("⚙️ Ayarlar")
    user_api_key = st.text_input(
        "Gemini API Anahtarı", 
        value=env_api_key if env_api_key else "", 
        type="password", 
        help="Analiz ve çeviri özellikleri için Google AI Studio anahtarınızı girin."
    )
    api_key = user_api_key if user_api_key else ""

st.title("🤖 AI Stratejik Haber Paneli")
st.markdown("Bu panel, güncel Yapay Zeka (LLM, Generative AI, OpenAI, vb.) haberlerini derler ve stratejik etkilerini Gemini ile analiz eder.")

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_news_cached(key):
    return get_news(key)

if not api_key:
    st.warning("⚠️ Lütfen soldaki menüden API anahtarınızı girin.")
else:
    # Anahtar girilmişse modeli konfigüre et ve veriyi çek
    genai.configure(api_key=api_key)
    
    with st.spinner("Haber akışı çekilirken ve başlıklar çevrilirken lütfen bekleyin..."):
        try:
            news = fetch_news_cached(api_key)
        except Exception as e:
            st.error(f"Haberler çekilirken bir hata oluştu: {e}")
            news = []

    if not news:
        st.info("Şu an için gösterilecek haber bulunamadı.")
    else:
        for i, item in enumerate(news):
            with st.container():
                st.subheader(item['title'])
                st.write(f"**Tarih:** {item['published']} | [Habere Git]({item['link']})")
                
                button_key = f"analyze_{i}"
                
                if st.button("Yapay Zeka Analizi", key=button_key):
                    with st.spinner("Gemini analiz ediyor..."):
                        try:
                            # Using standard flash model
                            model = genai.GenerativeModel('gemini-2.5-flash')
                            prompt = (
                                "Sen kıdemli bir teknoloji stratejistisin. Aşağıdaki haber başlığını ve "
                                "özetini kullanarak bu gelişmenin teknoloji dünyasına ve endüstriye olan etkisini "
                                "sadece tek, profesyonel ve çarpıcı bir cümlede özetle.\n\n"
                                f"Başlık: {item['title']}\n"
                                f"Özet (varsa): {item['summary']}"
                            )
                            response = model.generate_content(prompt)
                            st.info(f"**💡 Analiz Notu:**\n\n{response.text}")
                        except Exception as e:
                            st.error(f"Analiz sırasında bir hata oluştu: {e}")
                
                st.divider()
