"""
Motor de flujos encadenados — Samuel Marketing AI v2.0
Implementa la metodología del Manual de Agencia de Crecimiento Digital (12 volúmenes)
"""
from datetime import date, timedelta
from ..database import get_conn
from .groq_agent import analyze

# ──────────────────────────────────────────────
# Definición de los 8 pasos y sus prompts base
# ──────────────────────────────────────────────

STEPS = [
    "onboarding",
    "auditoria",
    "estrategia",
    "calendario",
    "produccion",
    "qa",
    "reporte",
    "renovacion",
]

STEP_LABELS = {
    "onboarding":  "Onboarding",
    "auditoria":   "Auditoría",
    "estrategia":  "Estrategia",
    "calendario":  "Calendario de contenido",
    "produccion":  "Producción",
    "qa":          "Control de calidad (QA)",
    "reporte":     "Reporte mensual",
    "renovacion":  "Propuesta de renovación",
}

STEP_SYSTEMS = {
    "onboarding": """Eres un consultor estratégico de marketing digital.
Tu tarea es hacer el onboarding de un nuevo cliente siguiendo la metodología profesional de agencia.
Genera: (1) un mensaje de bienvenida profesional y cálido para enviarle al cliente, (2) las 10 preguntas del cuestionario inicial del negocio (qué vende, a quién, ticket promedio, canal de ventas actual, clientes al mes, meta de clientes, publicidad anterior, diferenciador, mayor preocupación digital, qué sería éxito en 6 meses), (3) el brief de marca con las 9 preguntas de identidad visual (adjetivos que describen la marca, referencias visuales, colores preferidos, emociones que quiere provocar, dónde se usa el logo), (4) si tiene sitio web: las preguntas clave del brief web.
Adapta el tono y el contenido al tipo de evento o contexto indicado.
Responde en español con estructura clara, encabezados y formato profesional.""",

    "auditoria": """Eres un consultor de auditoría digital 360° con metodología de agencia profesional.
Genera un diagnóstico completo basado en la información del cliente. Cubre: (1) Auditoría de redes sociales: perfil, contenido, engagement, crecimiento, competencia — con tasa de engagement calculada y top 3 oportunidades por plataforma. (2) Auditoría de sitio web: velocidad, SEO técnico, UX, conversión, tracking — si aplica. (3) Google Business Profile: completitud, reseñas, posición local. (4) Publicidad pagada: si tiene Meta Ads o Google Ads, diagnóstica estructura, ROAS, creatividades. (5) Branding: coherencia visual, tono de comunicación, propuesta de valor. (6) Análisis de competencia: 3 competidores, qué hacen bien, qué gaps hay.
Al final incluye una MATRIZ DE PRIORIDADES (urgente-alto impacto / no urgente-alto impacto / urgente-bajo impacto / no urgente-bajo impacto) y un PLAN DE ACCIÓN de 60-90 días.
Adapta la profundidad al tiempo disponible indicado en el contexto.
Responde en español con estructura clara y accionable.""",

    "estrategia": """Eres un estratega de marketing digital de alto nivel.
Diseña la estrategia completa basada en la auditoría y el perfil del cliente. Incluye: (1) Objetivos SMART del período. (2) Plataformas prioritarias y por qué. (3) 4-6 pilares de contenido definidos para el cliente (con ejemplos específicos de su nicho). (4) Frecuencia de publicación por plataforma (Instagram feed 3-5/semana, Reels 2-4/semana, Stories 5-7/semana, TikTok 1-2/día, LinkedIn 3-5/semana). (5) Estrategia de hashtags: mix de grandes/medianos/pequeños, hashtags de ciudad si es negocio local. (6) Si tiene presupuesto de ads: objetivos de campaña, audiencias (fría + retargeting 20-30%), formatos. (7) Si tiene web: keywords de cola larga a trabajar. (8) Las 3 acciones de mayor impacto si solo hubiera 5 horas esta semana.
Adapta todo al contexto del evento y tiempo disponible.
Responde en español con estructura clara, objetivos medibles y tono motivador.""",

    "calendario": """Eres un especialista en redes sociales y planificación de contenido.
Genera el CALENDARIO DE CONTENIDO completo del período. Para cada publicación incluye: Fecha | Plataforma | Formato | Pilar | Concepto/título | Copy completo (hook en primera línea máx 125 chars, cuerpo en párrafos cortos de máx 3 líneas, CTA claro) | Referencia visual | Hashtags (5-15, mix de tamaños) | Horario de publicación.
Regla 80/20: 80% contenido de valor, 20% venta directa.
Los primeros 3 segundos de cada reel deben detener el scroll.
Si hay evento próximo: incluye contenido de anticipación, día del evento y post-evento.
Responde en español con formato estructurado y fácil de ejecutar.""",

    "produccion": """Eres un director creativo de contenido digital con experiencia en redes sociales hispanohablantes.
Genera el CONTENIDO LISTO PARA USAR. Para cada pieza: (1) COPY FINAL completo con emojis (3-7 por post) y hashtags al final. (2) GUIÓN DE VIDEO si aplica — [0-3s HOOK VISUAL + texto en pantalla] → [3-10s PROBLEMA/contexto] → [10-30s SOLUCIÓN en pasos] → [30-45s CIERRE + CTA]. (3) DESCRIPCIÓN VISUAL: qué mostrar (colores, estilo, elementos). (4) VARIANTE de anuncio si aplica.
Reglas: texto máximo 20% del espacio visual, logo siempre presente, máximo 3 fuentes, subtítulos en todos los videos, colores exactos de la paleta de la marca.
Responde en español, creativo, específico y listo para entregar.""",

    "qa": """Eres el QA Manager de una agencia de marketing digital profesional.
Revisa TODO el contenido producido y aplica checklists de calidad. Para cada pieza evalúa:
VIDEO: subtítulos en todo el video | música con licencia comercial | logo visible | sin errores de texto | duración apropiada | primeros 3s engancha.
DISEÑO: colores exactos de la paleta | logo correctamente colocado | tipografías correctas | texto legible | sin errores ortográficos | CTA presente | dimensiones correctas.
COPY: hook en primera línea (<125 chars) | párrafos cortos | 3-7 emojis | hashtags al final | CTA claro | sin errores ortográficos | tono coherente.
ADS: texto <20% del visual | landing page coherente | mínimo 3 variantes.
Genera: lista de correcciones necesarias (críticas vs menores), piezas que PASAN y piezas que deben REVISARSE.
Responde en español con lista estructurada.""",

    "reporte": """Eres un consultor que genera reportes mensuales profesionales para clientes de marketing digital.
Genera el REPORTE MENSUAL con esta estructura:
1. RESUMEN EJECUTIVO: 3-5 resultados más importantes en lenguaje simple.
2. RESULTADOS POR ÁREA: Redes sociales (seguidores ganados, alcance, engagement, publicaciones — benchmark: IG>3% bueno, >6% excelente / TikTok>9% bueno) | Publicidad si aplica (inversión, impresiones, ROAS, CPL) | SEO si aplica (tráfico orgánico, posiciones de keywords).
3. COMPARATIVA MES ANTERIOR: tabla de evolución.
4. CONTENIDO DESTACADO: top 3 publicaciones y por qué funcionaron.
5. APRENDIZAJES: qué funcionó, qué no y por qué.
6. PLAN DEL MES SIGUIENTE: qué se hará y por qué.
7. PRÓXIMOS PASOS: qué necesita el cliente para continuar.
Tono claro, transparente, en el idioma del cliente no-experto.
Responde en español con formato visual y estructurado.""",

    "renovacion": """Eres un consultor preparando una propuesta de renovación de contrato de marketing digital.
Genera la PROPUESTA DE CONTINUIDAD con:
1. RESUMEN DE LOGROS: resultados más importantes del período (con números concretos).
2. EVOLUCIÓN: estado inicial vs estado actual (antes/después).
3. OPORTUNIDADES DETECTADAS: qué más se puede hacer (upsell natural basado en datos).
4. PROPUESTA DE CONTINUIDAD: qué se recomienda y por qué, con objetivos concretos.
5. ARGUMENTOS DE RENOVACIÓN: 3-5 razones específicas para continuar (efecto compuesto SEO, audiencias de retargeting construidas, momentum de engagement).
6. PRÓXIMOS PASOS: cómo confirmar la renovación.
Tono confiado, basado en datos, orientado al valor.
Responde en español con estructura clara y convincente.""",
}


# ──────────────────────────────────────────────
# Generador de timeline
# ──────────────────────────────────────────────

def _days_until(event_date_str: str) -> int:
    try:
        event = date.fromisoformat(event_date_str)
        return max(1, (event - date.today()).days)
    except Exception:
        return 30


def generate_timeline(workflow_id: int):
    """Calcula planned_date y priority para cada paso según el timeline del workflow."""
    conn = get_conn()
    wf = conn.execute("SELECT * FROM workflows WHERE id=?", (workflow_id,)).fetchone()
    if not wf:
        conn.close()
        return

    timeline_type = wf["timeline_type"]
    event_date_str = wf["event_date"]
    today = date.today()

    if timeline_type == "urgente" and event_date_str:
        days = _days_until(event_date_str)
        ev = date.fromisoformat(event_date_str)
        if days <= 3:
            schedule = [
                ("onboarding",  today,                         "urgent"),
                ("auditoria",   today,                         "urgent"),
                ("estrategia",  today + timedelta(days=1),     "urgent"),
                ("calendario",  today + timedelta(days=1),     "urgent"),
                ("produccion",  today + timedelta(days=2),     "urgent"),
                ("qa",          today + timedelta(days=2),     "urgent"),
                ("reporte",     ev + timedelta(days=3),        "high"),
                ("renovacion",  ev + timedelta(days=7),        "normal"),
            ]
        else:
            schedule = [
                ("onboarding",  today,                         "urgent"),
                ("auditoria",   today + timedelta(days=1),     "urgent"),
                ("estrategia",  today + timedelta(days=2),     "urgent"),
                ("calendario",  today + timedelta(days=3),     "high"),
                ("produccion",  today + timedelta(days=4),     "high"),
                ("qa",          today + timedelta(days=5),     "high"),
                ("reporte",     ev + timedelta(days=3),        "normal"),
                ("renovacion",  ev + timedelta(days=14),       "normal"),
            ]
    elif timeline_type == "corto":
        schedule = [
            ("onboarding",  today,                          "high"),
            ("auditoria",   today + timedelta(days=2),      "high"),
            ("estrategia",  today + timedelta(days=5),      "high"),
            ("calendario",  today + timedelta(days=7),      "normal"),
            ("produccion",  today + timedelta(days=10),     "normal"),
            ("qa",          today + timedelta(days=14),     "normal"),
            ("reporte",     today + timedelta(days=18),     "normal"),
            ("renovacion",  today + timedelta(days=21),     "low"),
        ]
    elif timeline_type == "continuo":
        schedule = [
            ("onboarding",  today,                          "normal"),
            ("auditoria",   today + timedelta(days=3),      "normal"),
            ("estrategia",  today + timedelta(days=7),      "normal"),
            ("calendario",  today + timedelta(days=10),     "normal"),
            ("produccion",  today + timedelta(days=14),     "normal"),
            ("qa",          today + timedelta(days=20),     "normal"),
            ("reporte",     today + timedelta(days=30),     "normal"),
            ("renovacion",  today + timedelta(days=60),     "low"),
        ]
    else:  # mensual
        schedule = [
            ("onboarding",  today,                          "normal"),
            ("auditoria",   today + timedelta(days=2),      "normal"),
            ("estrategia",  today + timedelta(days=7),      "normal"),
            ("calendario",  today + timedelta(days=10),     "normal"),
            ("produccion",  today + timedelta(days=14),     "normal"),
            ("qa",          today + timedelta(days=20),     "normal"),
            ("reporte",     today + timedelta(days=28),     "normal"),
            ("renovacion",  today + timedelta(days=58),     "low"),
        ]

    for i, (step_type, planned, priority) in enumerate(schedule, start=1):
        conn.execute(
            """UPDATE workflow_steps
               SET planned_date=?, priority=?
               WHERE workflow_id=? AND step_order=?""",
            (planned.isoformat(), priority, workflow_id, i),
        )

    conn.commit()
    conn.close()


# ──────────────────────────────────────────────
# Creación de workflow
# ──────────────────────────────────────────────

def create_workflow(client_id: int, name: str, focus: str,
                    event_type: str, event_description: str,
                    event_date: str, timeline_type: str) -> int:
    conn = get_conn()
    cur = conn.execute(
        """INSERT INTO workflows
           (client_id, name, focus, event_type, event_description, event_date, timeline_type)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (client_id, name, focus, event_type, event_description, event_date, timeline_type),
    )
    workflow_id = cur.lastrowid

    for i, step_type in enumerate(STEPS, start=1):
        conn.execute(
            "INSERT INTO workflow_steps (workflow_id, step_order, step_type) VALUES (?, ?, ?)",
            (workflow_id, i, step_type),
        )

    conn.commit()
    conn.close()
    generate_timeline(workflow_id)
    return workflow_id


# ──────────────────────────────────────────────
# Inyección de contexto acumulado
# ──────────────────────────────────────────────

def _build_context(workflow_id: int, up_to_step: int) -> str:
    conn = get_conn()
    wf = conn.execute("SELECT * FROM workflows WHERE id=?", (workflow_id,)).fetchone()
    client = conn.execute("SELECT * FROM clients WHERE id=?", (wf["client_id"],)).fetchone()
    steps = conn.execute(
        "SELECT * FROM workflow_steps WHERE workflow_id=? AND step_order < ? ORDER BY step_order",
        (workflow_id, up_to_step),
    ).fetchall()
    conn.close()

    c = dict(client)
    w = dict(wf)

    ctx = f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PERFIL DEL CLIENTE:
- Nombre: {c['name']}
- Nicho: {c.get('niche') or 'No especificado'}
- Descripción: {c.get('description') or 'No especificada'}
- Instagram: {c.get('instagram') or 'N/A'}
- TikTok: {c.get('tiktok') or 'N/A'}
- Facebook: {c.get('facebook') or 'N/A'}
- YouTube: {c.get('youtube') or 'N/A'}
- Web: {c.get('website') or 'N/A'}
- Tono de marca: {c.get('brand_tone') or 'No definido'}
- Audiencia objetivo: {c.get('target_audience') or 'No definida'}

OBJETIVO DEL FLUJO: {w.get('focus') or 'No especificado'}
"""

    if w.get("event_type") or w.get("event_description"):
        days_left = ""
        if w.get("event_date"):
            try:
                ev = date.fromisoformat(w["event_date"])
                diff = (ev - date.today()).days
                days_left = f" ({diff} días restantes)"
            except Exception:
                pass

        ctx += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CONTEXTO DEL EVENTO:
- Tipo: {w.get('event_type') or 'N/A'}
- Descripción: {w.get('event_description') or 'N/A'}
- Fecha: {w.get('event_date') or 'N/A'}{days_left}
- Modo de trabajo: {w.get('timeline_type', 'mensual')}
"""

    if steps:
        ctx += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\nCONTEXTO ACUMULADO DE PASOS ANTERIORES:\n"
        for s in steps:
            if s["result"]:
                ctx += f"\n[Paso {s['step_order']} — {STEP_LABELS.get(s['step_type'], s['step_type'])}]\n"
                ctx += s["result"][:3000]
                if s["samuel_notes"]:
                    ctx += f"\nNotas de Samuel: {s['samuel_notes']}\n"

    return ctx


# ──────────────────────────────────────────────
# Ejecutar siguiente paso
# ──────────────────────────────────────────────

def run_next_step(workflow_id: int) -> dict:
    conn = get_conn()
    wf = conn.execute("SELECT * FROM workflows WHERE id=?", (workflow_id,)).fetchone()
    if not wf:
        conn.close()
        return {"error": "Workflow no encontrado"}

    next_order = wf["current_step"] + 1
    if next_order > len(STEPS):
        conn.close()
        return {"error": "El flujo ya está completo"}

    step = conn.execute(
        "SELECT * FROM workflow_steps WHERE workflow_id=? AND step_order=?",
        (workflow_id, next_order),
    ).fetchone()

    if not step:
        conn.close()
        return {"error": "Paso no encontrado"}

    conn.execute("UPDATE workflow_steps SET status='running' WHERE id=?", (step["id"],))
    conn.commit()
    conn.close()

    context = _build_context(workflow_id, next_order)
    system = STEP_SYSTEMS.get(step["step_type"], "Eres un consultor de marketing digital. Responde en español.")
    result = analyze(system, context)

    conn = get_conn()
    conn.execute(
        "UPDATE workflow_steps SET status='waiting_samuel', result=? WHERE id=?",
        (result, step["id"]),
    )
    conn.commit()
    conn.close()

    return {
        "step_id": step["id"],
        "step_order": next_order,
        "step_type": step["step_type"],
        "step_label": STEP_LABELS.get(step["step_type"], step["step_type"]),
        "result": result,
        "planned_date": step["planned_date"],
        "priority": step["priority"],
    }


# ──────────────────────────────────────────────
# Samuel aprueba y avanza
# ──────────────────────────────────────────────

def samuel_continues(workflow_id: int, step_id: int, notes: str, choice: str) -> dict:
    new_status = "skipped" if choice == "skip" else "approved"
    conn = get_conn()
    conn.execute(
        "UPDATE workflow_steps SET status=?, samuel_notes=?, samuel_choice=? WHERE id=?",
        (new_status, notes, choice, step_id),
    )
    step = conn.execute("SELECT step_order FROM workflow_steps WHERE id=?", (step_id,)).fetchone()
    if step:
        conn.execute(
            "UPDATE workflows SET current_step=?, updated_at=datetime('now') WHERE id=?",
            (step["step_order"], workflow_id),
        )
        # Marcar workflow como completado si todos los pasos están terminados
        remaining = conn.execute(
            "SELECT COUNT(*) as n FROM workflow_steps WHERE workflow_id=? AND status='pending'",
            (workflow_id,),
        ).fetchone()
        if remaining and remaining["n"] == 0:
            conn.execute(
                "UPDATE workflows SET status='completed', updated_at=datetime('now') WHERE id=?",
                (workflow_id,),
            )
    conn.commit()
    conn.close()
    return {"status": new_status, "next_step": (step["step_order"] + 1) if step else None}


# ──────────────────────────────────────────────
# Regenerar un paso con ajuste de Samuel
# ──────────────────────────────────────────────

def regenerate_step(workflow_id: int, step_id: int, adjustment: str) -> dict:
    conn = get_conn()
    step = conn.execute("SELECT * FROM workflow_steps WHERE id=?", (step_id,)).fetchone()
    if not step:
        conn.close()
        return {"error": "Paso no encontrado"}

    conn.execute("UPDATE workflow_steps SET status='regenerating' WHERE id=?", (step_id,))
    conn.commit()
    conn.close()

    context = _build_context(workflow_id, step["step_order"])
    context += f"\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\nAJUSTE SOLICITADO POR SAMUEL:\n{adjustment}\n\nTen en cuenta este ajuste y genera una versión mejorada."

    system = STEP_SYSTEMS.get(step["step_type"], "Eres un consultor de marketing digital. Responde en español.")
    result = analyze(system, context)

    conn = get_conn()
    conn.execute(
        "UPDATE workflow_steps SET status='waiting_samuel', result=?, samuel_notes=? WHERE id=?",
        (result, adjustment, step_id),
    )
    conn.commit()
    conn.close()

    return {
        "step_id": step_id,
        "step_type": step["step_type"],
        "step_label": STEP_LABELS.get(step["step_type"], step["step_type"]),
        "result": result,
    }


# ──────────────────────────────────────────────
# Consultas de lectura
# ──────────────────────────────────────────────

def get_workflow_detail(workflow_id: int) -> dict:
    conn = get_conn()
    wf = conn.execute(
        """SELECT w.*, c.name as client_name, c.niche as client_niche
           FROM workflows w LEFT JOIN clients c ON w.client_id=c.id
           WHERE w.id=?""",
        (workflow_id,),
    ).fetchone()
    if not wf:
        conn.close()
        return {}

    steps = conn.execute(
        "SELECT * FROM workflow_steps WHERE workflow_id=? ORDER BY step_order",
        (workflow_id,),
    ).fetchall()
    conn.close()

    return {
        **dict(wf),
        "steps": [dict(s) for s in steps],
    }


def list_workflows(include_completed: bool = False) -> list:
    conn = get_conn()
    query = """SELECT w.*, c.name as client_name
               FROM workflows w LEFT JOIN clients c ON w.client_id=c.id"""
    if not include_completed:
        query += " WHERE w.status != 'completed'"
    query += " ORDER BY w.updated_at DESC"
    rows = conn.execute(query).fetchall()
    result = []
    for r in rows:
        wf = dict(r)
        steps = conn.execute(
            "SELECT id, step_order, step_type, planned_date, priority, status FROM workflow_steps WHERE workflow_id=? ORDER BY step_order",
            (wf["id"],),
        ).fetchall()
        wf["steps"] = [dict(s) for s in steps]
        result.append(wf)
    conn.close()
    return result


def list_pending_workflows() -> list:
    conn = get_conn()
    rows = conn.execute(
        """SELECT DISTINCT w.*, c.name as client_name,
                  (SELECT COUNT(*) FROM workflow_steps ws2
                   WHERE ws2.workflow_id=w.id AND ws2.status='waiting_samuel') as pending_count
           FROM workflows w
           LEFT JOIN clients c ON w.client_id=c.id
           JOIN workflow_steps ws ON ws.workflow_id=w.id
           WHERE ws.status='waiting_samuel'
           ORDER BY w.updated_at DESC""",
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
