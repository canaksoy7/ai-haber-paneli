import feedparser
import urllib.parse
import ssl
import google.generativeai as genai
import json

def get_news(api_key):
    # API key kesin olarak gelmektedir, app.py'de kontrol ediliyor
    genai.configure(api_key=api_key)

    # SSL doğrulamasını atlamak için gerekli olabilir (bazı ortamlarda feedparser hata verebilir)
    if hasattr(ssl, '_create_unverified_context'):
        ssl._create_default_https_context = ssl._create_unverified_context

    query = '(LLM OR Generative AI OR OpenAI OR Anthropic) language:tr'
    encoded_query = urllib.parse.quote_plus(query)
    url = f"https://news.google.com/rss/search?q={encoded_query}"
    
    feed = feedparser.parse(url)
    news_items = []
    
    if not hasattr(feed, 'entries'):
        return news_items

    # Çeviri işleminin çok uzun sürmemesi için ilk 15 haberi alıyoruz.
    entries_to_process = feed.entries[:15]

    for entry in entries_to_process:
        news_items.append({
            'title': entry.title,
            'link': entry.link,
            'published': entry.get('published', 'Tarih Yok'),
            'summary': entry.get('summary', '')
        })

    # Toplu Çeviri İşlemi - Gemini ile
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Başlıkları indeksleriyle bir sözlükte toplayalım
        titles_to_translate = {str(i): item['title'] for i, item in enumerate(news_items)}
        
        prompt = (
            "Aşağıda bir JSON nesnesi formatında haber başlıkları verilmiştir. "
            "Bu başlıklardan İngilizce olanları Türkçe'ye çevir. Zaten Türkçe olanlara dokunma. "
            "Sadece ve sadece aynı JSON formatında indeks numaralarıyla ve tamamen Türkçe olan başlıklarla yanıt ver. "
            "Başka hiçbir ekstra metin ekleme:\n"
            f"{json.dumps(titles_to_translate, ensure_ascii=False)}"
        )
        
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Gelen yanıtta ```json formatlaması varsa temizleyelim
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
            
        translated_titles = json.loads(response_text.strip())
        
        for i, item in enumerate(news_items):
            item['title'] = translated_titles.get(str(i), item['title'])
            
    except Exception as e:
        print(f"Çeviri sırasında bir hata oluştu: {e}")
        
    return news_items
