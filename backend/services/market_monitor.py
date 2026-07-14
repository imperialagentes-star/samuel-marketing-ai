import feedparser
from datetime import datetime
from .groq_agent import analyze

RSS_FEEDS = [
    ("Social Media Examiner", "https://www.socialmediaexaminer.com/feed/"),
    ("HubSpot Marketing", "https://blog.hubspot.com/marketing/rss.xml"),
    ("Neil Patel", "https://neilpatel.com/feed/"),
    ("Marketing Land", "https://martech.org/feed/"),
]


def fetch_rss_headlines(max_per_feed: int = 4) -> list:
    headlines = []
    for source, url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:max_per_feed]:
                title = entry.get("title", "").strip()
                summary = entry.get("summary", "").strip()[:200]
                if title:
                    headlines.append({"source": source, "title": title, "summary": summary})
        except Exception:
            continue
    return headlines


def fetch_google_trends(keywords: list) -> dict:
    try:
        from pytrends.request import TrendReq
        pytrends = TrendReq(hl="es-419", tz=300)
        kw_list = keywords[:5]
        pytrends.build_payload(kw_list, timeframe="now 1-d", geo="")
        interest = pytrends.interest_over_time()
        if not interest.empty:
            latest = interest.iloc[-1]
            return {kw: int(latest.get(kw, 0)) for kw in kw_list if kw in latest}
    except Exception:
        pass
    return {}


def generate_daily_report(keywords: list = None) -> str:
    if not keywords:
        keywords = ["marketing digital", "redes sociales", "publicidad", "contenido viral", "ventas online"]

    today = datetime.now().strftime("%d/%m/%Y %H:%M")
    headlines = fetch_rss_headlines()
    trends = fetch_google_trends(keywords)

    data = f"""FECHA: {today}

TENDENCIAS GOOGLE (últimas 24h):
{chr(10).join(f"  - {k}: {v}/100" for k, v in trends.items()) if trends else "  No disponible"}

NOTICIAS DE MARKETING:
{chr(10).join(f"  [{h['source']}] {h['title']}" for h in headlines[:12])}
"""

    system = """Eres un analista de marketing digital senior trabajando para una agencia de lujo.
Genera un informe de mercado diario en español, conciso y 100% accionable.

Formato OBLIGATORIO (usa exactamente estos encabezados con emoji):
🔥 *TOP 3 TENDENCIAS DEL DÍA*
(3 bullets con la tendencia y por qué importa)

💡 *3 OPORTUNIDADES CONCRETAS*
(3 bullets con oportunidades reales explotables HOY)

📹 *QUÉ TIPO DE CONTENIDO ESTÁ GANANDO*
(2-3 bullets con formatos y temas que funcionan)

⚡ *3 ACCIONES PARA HOY*
(3 bullets numerados, ultra-específicos y ejecutables)

Máximo 600 palabras. Directo. Sin relleno."""

    result = analyze(system, f"Datos del mercado de hoy:\n\n{data}")
    return f"📊 *REPORTE DIARIO — {today}*\n\n{result}"
