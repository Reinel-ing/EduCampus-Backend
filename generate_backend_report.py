"""
generate_backend_report.py
Genera un informe HTML de todas las pruebas del backend.
Secciones: Unitarias · Integración · Sistema · Aceptación
Uso: venv/Scripts/python.exe generate_backend_report.py
"""
import subprocess
import sys
import json
import webbrowser
from pathlib import Path
from datetime import datetime

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).parent
JSON_OUT = BASE_DIR / "backend-results.json"
HTML_OUT = BASE_DIR / "backend-report.html"

# ─────────────────────────────────────────────────────────────────
# 1. Ejecutar pruebas
# ─────────────────────────────────────────────────────────────────
print("\nEduCampus — Generando informe de pruebas (Backend)...\n")

subprocess.run(
    [sys.executable, "-m", "pytest", "tests/", "-v",
     "--json-report", f"--json-report-file={JSON_OUT}"],
    cwd=str(BASE_DIR)
)

if not JSON_OUT.exists():
    print("Error: No se genero backend-results.json")
    sys.exit(1)

with open(JSON_OUT, encoding="utf-8") as f:
    data = json.load(f)

# ─────────────────────────────────────────────────────────────────
# 2. Metadatos de cada archivo
# ─────────────────────────────────────────────────────────────────
FILE_META = {
    "test_security.py":              ("security — hash / verify_password",     "Unitaria",    "CE · VL · CB"),
    "test_schemas_estudiante.py":    ("schemas — EstudianteCreate / Update",   "Unitaria",    "CE · VL · CB"),
    "test_schemas_docente.py":       ("schemas — DocenteCreate / Update",      "Unitaria",    "CE · VL · CB"),
    "test_schemas_calificacion.py":  ("schemas — CalificacionCreate / Update", "Unitaria",    "CE · VL · CB"),
    "test_schemas_curso.py":         ("schemas — CursoCreate / Update",        "Unitaria",    "CE · VL · CB"),
    "test_bugs.py":                  ("Deteccion de Bugs",                     "Regresion",   "Regresion"),
    "test_int_auth.py":              ("Integracion — /auth/login",             "Integracion", "CE · VL · CB"),
    "test_int_cursos.py":            ("Integracion — /cursos/ CRUD",           "Integracion", "CE · VL · CB"),
    "test_int_estudiantes.py":       ("Integracion — /estudiantes/ CRUD",      "Integracion", "CE · VL · CB"),
    "test_int_flujo_completo.py":    ("Integracion — Flujo completo",          "Integracion", "CB"),
    "test_sis_inscripciones.py":     ("Sistema — Inscripciones y cupo",        "Sistema",     "CE · VL · CB"),
    "test_sis_calificaciones.py":    ("Sistema — Calificaciones y promedio",   "Sistema",     "CE · VL · CB"),
    "test_acep_historias_usuario.py":("Aceptacion — HU-01 a HU-04",           "Aceptacion",  "CB (HU)"),
}

# Etiqueta corta para el menú de navegación
FILE_NAV_LABEL = {
    "test_security.py":              "security",
    "test_schemas_estudiante.py":    "schemas estudiante",
    "test_schemas_docente.py":       "schemas docente",
    "test_schemas_calificacion.py":  "schemas calificacion",
    "test_schemas_curso.py":         "schemas curso",
    "test_bugs.py":                  "deteccion de bugs",
    "test_int_auth.py":              "/auth/login",
    "test_int_cursos.py":            "/cursos/ CRUD",
    "test_int_estudiantes.py":       "/estudiantes/ CRUD",
    "test_int_flujo_completo.py":    "flujo completo",
    "test_sis_inscripciones.py":     "inscripciones y cupo",
    "test_sis_calificaciones.py":    "calificaciones y promedio",
    "test_acep_historias_usuario.py":"historias de usuario",
}

NIVELES = {
    "Pruebas Unitarias": [
        "test_security.py",
        "test_schemas_estudiante.py",
        "test_schemas_docente.py",
        "test_schemas_calificacion.py",
        "test_schemas_curso.py",
        "test_bugs.py",
    ],
    "Pruebas de Integracion": [
        "test_int_auth.py",
        "test_int_cursos.py",
        "test_int_estudiantes.py",
        "test_int_flujo_completo.py",
    ],
    "Pruebas de Sistema": [
        "test_sis_inscripciones.py",
        "test_sis_calificaciones.py",
    ],
    "Pruebas de Aceptacion": [
        "test_acep_historias_usuario.py",
    ],
}

NIVEL_DESC = {
    "Pruebas Unitarias":       "Funciones y validadores de forma aislada. Tecnicas: CE, VL, CB.",
    "Pruebas de Integracion":  "Endpoints HTTP completos sobre SQLite usando FastAPI TestClient.",
    "Pruebas de Sistema":      "Reglas de negocio del sistema: cupo, duplicados, promedios.",
    "Pruebas de Aceptacion":   "Historias de usuario HU-01 a HU-04.",
}

NIVEL_ICON  = {"Pruebas Unitarias":"U","Pruebas de Integracion":"I","Pruebas de Sistema":"S","Pruebas de Aceptacion":"A"}
NIVEL_COLOR = {"Pruebas Unitarias":"#1849b5","Pruebas de Integracion":"#0f766e","Pruebas de Sistema":"#7c3aed","Pruebas de Aceptacion":"#b45309"}

# IDs HTML para anclas
NIVEL_IDS   = {"Pruebas Unitarias":"sec-unitarias","Pruebas de Integracion":"sec-integracion","Pruebas de Sistema":"sec-sistema","Pruebas de Aceptacion":"sec-aceptacion"}

def file_to_id(fname):
    """test_int_auth.py  ->  s-int-auth"""
    return "s-" + fname.replace("test_","").replace(".py","").replace("_","-")

# ─────────────────────────────────────────────────────────────────
# 3. Helpers
# ─────────────────────────────────────────────────────────────────
def parse_nodeid(nodeid):
    parts = nodeid.split("::")
    fname = Path(parts[0]).name if parts else ""
    cls   = parts[1] if len(parts) > 1 else ""
    test  = parts[2] if len(parts) > 2 else (parts[-1] if parts else "")
    return fname, cls, test

def fmt_ms(s):
    if s is None: return "< 1 ms"
    ms = s * 1000
    return f"{round(ms)} ms" if ms < 1000 else f"{s:.2f} s"

def fmt_date(ts):
    try:    return datetime.fromtimestamp(ts).strftime("%A, %d de %B de %Y, %I:%M %p")
    except: return datetime.now().strftime("%A, %d de %B de %Y, %I:%M %p")

def esc(s):
    return str(s).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;")

# ─────────────────────────────────────────────────────────────────
# 4. Agrupar tests
# ─────────────────────────────────────────────────────────────────
summary  = data.get("summary", {})
total    = summary.get("total",  0)
passed   = summary.get("passed", 0)
failed   = summary.get("failed", 0)
duration = data.get("duration", 0)
pass_rate= round(passed / total * 100) if total > 0 else 0
exec_date= fmt_date(data.get("created", 0))

by_file = {}
for t in data.get("tests", []):
    fname, cls, tname = parse_nodeid(t["nodeid"])
    by_file.setdefault(fname, {}).setdefault(cls, []).append({
        "name":     tname,
        "outcome":  t.get("outcome", "?"),
        "duration": (t.get("call") or {}).get("duration"),
        "longrepr": (t.get("call") or {}).get("longrepr", ""),
    })

# ─────────────────────────────────────────────────────────────────
# 5. Funciones de estadísticas
# ─────────────────────────────────────────────────────────────────
def nivel_stats(files):
    t = p = f = d = 0
    for fname in files:
        if fname not in by_file: continue
        tests = [x for g in by_file[fname].values() for x in g]
        p += sum(1 for x in tests if x["outcome"] == "passed")
        t += len(tests)
        d += sum(x["duration"] or 0 for x in tests)
    return t, p, t - p, d

# ─────────────────────────────────────────────────────────────────
# 6. Navegación desplegable
# ─────────────────────────────────────────────────────────────────
def nav_html():
    items = ""
    for nivel, files in NIVELES.items():
        t, p, f, _ = nivel_stats(files)
        nid   = NIVEL_IDS[nivel]
        color = NIVEL_COLOR[nivel]
        icon  = NIVEL_ICON[nivel]
        label = nivel.replace("Pruebas ", "").replace("de ", "")

        links = ""
        for fname in files:
            fid      = file_to_id(fname)
            nav_lbl  = FILE_NAV_LABEL.get(fname, fname)
            tf       = [x for g in by_file.get(fname, {}).values() for x in g]
            pf       = sum(1 for x in tf if x["outcome"] == "passed")
            dot_cls  = "dot-ok" if pf == len(tf) else "dot-err"
            links += f'<a href="#{fid}" class="dd-link"><span class="dot {dot_cls}"></span>{esc(nav_lbl)}<span class="dd-cnt">{len(tf)}</span></a>'

        items += f"""
    <div class="nav-item" id="nav-{nid}">
      <a href="#{nid}" class="nav-a" style="--c:{color}">
        <span class="nav-badge" style="background:{color}">{icon}</span>
        {label}
        <span class="nav-cnt">{t}</span>
        <span class="nav-arrow">&#9662;</span>
      </a>
      <div class="dropdown">
        <div class="dd-header" style="border-top:3px solid {color}">{nivel}</div>
        {links}
      </div>
    </div>"""

    return f"""
<nav class="sticky-nav" id="top-nav">
  <div class="nav-inner">
    <a href="#resumen-global" class="nav-brand">EC Tests</a>
    <div class="nav-group">
      <a href="#resumen-global" class="nav-a nav-plain">Resumen</a>
      <a href="#sec-bugs"       class="nav-a nav-plain">Bugs</a>
      {items}
    </div>
  </div>
</nav>"""

# ─────────────────────────────────────────────────────────────────
# 7. Bloques de nivel
# ─────────────────────────────────────────────────────────────────
def mini_cards(files, color):
    t, p, f, d = nivel_stats(files)
    rate = round(p / t * 100) if t > 0 else 0
    rc   = "#22c55e" if rate == 100 else ("#f59e0b" if rate >= 80 else "#ef4444")
    fail_html = f'<div class="mc"><div class="mc-num" style="color:#ef4444">{f}</div><div class="mc-lbl">Fallidas</div></div>' if f > 0 else ""
    return f"""
  <div class="mini-cards" style="--acc:{color}">
    <div class="mc"><div class="mc-num" style="color:{color}">{t}</div><div class="mc-lbl">Total</div></div>
    <div class="mc"><div class="mc-num" style="color:#22c55e">{p}</div><div class="mc-lbl">Pasaron</div></div>
    {fail_html}
    <div class="mc"><div class="mc-num" style="color:#8b5cf6;font-size:16px">{fmt_ms(d)}</div><div class="mc-lbl">Tiempo</div></div>
    <div class="mc mc-rate">
      <div class="pbar-top"><span style="font-size:12px;font-weight:700;color:#475569">Exito</span>
        <span style="font-size:18px;font-weight:900;color:{rc}">{rate}%</span></div>
      <div class="pbar-track"><div class="pbar-fill" style="width:{rate}%;background:{rc}"></div></div>
    </div>
  </div>"""

def nivel_table(files):
    rows = ""
    for fname in files:
        if fname not in by_file: continue
        tests = [x for g in by_file[fname].values() for x in g]
        p = sum(1 for x in tests if x["outcome"] == "passed")
        f = len(tests) - p
        ok = f == 0
        badge = '<span class="badge badge-ok">PASS</span>' if ok else '<span class="badge badge-err">FAIL</span>'
        lbl, _, tec = FILE_META.get(fname, (fname,"–","–"))
        dur = sum(x["duration"] or 0 for x in tests)
        fail_cell = f'<span class="num-fail">{f}</span>' if f > 0 else '<span class="dim">–</span>'
        rows += f"""
    <tr>
      <td>{badge}</td>
      <td><a href="#{file_to_id(fname)}" class="tbl-anchor"><strong>{esc(lbl)}</strong></a></td>
      <td><span class="chip chip-tec">{esc(tec)}</span></td>
      <td class="center">{len(tests)}</td>
      <td class="center num-pass">{p}</td>
      <td class="center">{fail_cell}</td>
      <td class="center dim">{fmt_ms(dur)}</td>
    </tr>"""
    return f"""
  <table class="tbl">
    <thead><tr>
      <th>Estado</th><th>Modulo / Archivo</th><th>Tecnica</th>
      <th class="center">Total</th><th class="center">Pasaron</th>
      <th class="center">Fallaron</th><th class="center">Tiempo</th>
    </tr></thead>
    <tbody>{rows}</tbody>
  </table>"""

def nivel_detail(files):
    html = ""
    for fname in files:
        if fname not in by_file: continue
        groups     = by_file[fname]
        tests_flat = [x for g in groups.values() for x in g]
        p   = sum(1 for x in tests_flat if x["outcome"] == "passed")
        f   = len(tests_flat) - p
        dur = sum(x["duration"] or 0 for x in tests_flat)
        lbl, _, _ = FILE_META.get(fname, (fname,"–","–"))
        hdr_cls = "suite-bad" if f > 0 else "suite-good"
        icon    = "x" if f > 0 else "v"
        s_err   = f'<span class="s-err">{f} fallaron</span>' if f > 0 else ""

        groups_html = ""
        for cls_name, tests in groups.items():
            gp = sum(1 for t in tests if t["outcome"] == "passed")
            gf = len(tests) - gp
            grp_cls = "grp-fail" if gf > 0 else "grp-pass"
            g_err   = f'<span class="g-err">{gf} fallaron</span>' if gf > 0 else ""
            rows = ""
            for t in tests:
                ok     = t["outcome"] == "passed"
                tr_cls = "tr-ok" if ok else "tr-err"
                ic     = "+" if ok else "x"
                err_row = ""
                if not ok and t.get("longrepr"):
                    first = esc(str(t["longrepr"]).split("\n")[0][:200])
                    err_row = f'<tr class="err-row"><td></td><td colspan="2" class="err-msg">! {first}</td></tr>'
                rows += f"""
              <tr class="{tr_cls}">
                <td class="icon-cell">{ic}</td>
                <td>{esc(t["name"])}</td>
                <td class="center dim">{fmt_ms(t["duration"])}</td>
              </tr>{err_row}"""

            groups_html += f"""
          <tr class="grp-row {grp_cls}">
            <td colspan="3"><strong>{esc(cls_name)}</strong>
              <span class="grp-meta"><span class="g-ok">{gp} pasaron</span>{g_err}</span>
            </td>
          </tr>{rows}"""

        html += f"""
  <div class="suite" id="{file_to_id(fname)}">
    <div class="suite-hdr {hdr_cls}">
      <span class="suite-icon">{icon}</span>
      <span class="suite-name">{esc(lbl)}</span>
      <span class="suite-right">
        <span class="s-ok">{p} pasaron</span>{s_err}
        <span class="dim">{fmt_ms(dur)}</span>
      </span>
    </div>
    <table class="tbl tbl-detail">
      <thead><tr><th style="width:42px">Est.</th><th>Prueba</th><th class="center" style="width:90px">Tiempo</th></tr></thead>
      <tbody>{groups_html}</tbody>
    </table>
  </div>"""
    return html

# ─────────────────────────────────────────────────────────────────
# 8. Bugs
# ─────────────────────────────────────────────────────────────────
def bugs_html():
    bugs = [
        {
            "id":"BUG-02","sev":"MEDIA","status":"CORREGIDO",
            "title":"CalificacionCreate acepta notas fuera del rango 0 a 5",
            "module":"schemas/calificacion.py",
            "desc":"El campo nota era float sin validador. Pydantic aceptaba -1.0 o 10.0 sin error. En la escala colombiana las notas van de 0.0 a 5.0.",
            "before":"nota: float  # sin validacion de rango",
            "after":"@field_validator('nota')\n@classmethod\ndef validar_nota(cls, v):\n    if v < 0.0 or v > 5.0:\n        raise ValueError('La nota debe estar entre 0.0 y 5.0')\n    return v",
            "tests":["CE-04 nota=-1.0 debe ser INVALIDA","CE-05 nota=6.0 debe ser INVALIDA","VL-01 nota=-0.1 invalida"],
            "impact":"Notas imposibles podian insertarse en la BD corrompiendo el historial academico."
        },
        {
            "id":"BUG-03","sev":"MEDIA","status":"CORREGIDO",
            "title":"CursoCreate acepta cupo=0/negativo y horario vacio",
            "module":"schemas/curso.py",
            "desc":"cupo_estudiante y horario no tenian validadores. Un curso con cupo=0 o horario=[] pasaba sin error.",
            "before":"cupo_estudiante: int  # acepta 0 o negativos\nhorario: List[Any]   # acepta lista vacia",
            "after":"@field_validator('cupo_estudiante')\n@classmethod\ndef validar_cupo(cls, v):\n    if v < 1: raise ValueError('El cupo debe ser al menos 1')\n    return v\n\n@field_validator('horario')\n@classmethod\ndef validar_horario(cls, v):\n    if not v: raise ValueError('Debe haber al menos un horario')\n    return v",
            "tests":["CE-02 cupo=0 invalido","CE-03 cupo=-5 invalido","CE-06 horario=[] invalido"],
            "impact":"Se podian crear cursos sin cupo ni horario, datos inconsistentes en la BD."
        },
        {
            "id":"BUG-04","sev":"ALTA","status":"CORREGIDO",
            "title":"hash_password lanza ValueError con contrasenas de mas de 72 caracteres",
            "module":"utils/security.py",
            "desc":"hash_password no truncaba la contrasena. bcrypt v5 lanza ValueError si recibe mas de 72 bytes.",
            "before":"password_bytes = password.encode('utf-8')\nhashed = bcrypt.hashpw(password_bytes, salt)  # crash si > 72 bytes",
            "after":"password_bytes = password.encode('utf-8')\npassword_bytes = password_bytes[:72]  # truncar al limite de bcrypt\nhashed = bcrypt.hashpw(password_bytes, salt)",
            "tests":["VL-03 contrasena de 100 chars no lanza error"],
            "impact":"Una peticion con contrasena larga derribaba el servidor con error 500."
        },
    ]
    html = ""
    for b in bugs:
        sev_cls  = f"sev-{b['sev'].lower()}"
        stat_cls = "stat-fixed" if b["status"]=="CORREGIDO" else "stat-open"
        tests_li = "".join(f"<li><code>{esc(t)}</code></li>" for t in b["tests"])
        html += f"""
  <div class="bug-card">
    <div class="bug-hdr">
      <span class="bug-id">{b['id']}</span>
      <span class="bug-title">{b['title']}</span>
      <div class="bug-tags">
        <span class="bug-sev {sev_cls}">{b['sev']}</span>
        <span class="bug-stat {stat_cls}">{b['status']}</span>
      </div>
    </div>
    <div class="bug-body">
      <div class="info-grid">
        <div class="info-item"><span class="info-key">Modulo</span><code>{b['module']}</code></div>
        <div class="info-item"><span class="info-key">Severidad</span>{b['sev']}</div>
        <div class="info-item"><span class="info-key">Estado</span>{b['status']}</div>
      </div>
      <p class="block-text" style="margin-bottom:12px">{esc(b['desc'])}</p>
      <p class="block-text" style="margin-bottom:12px;color:#7c3aed"><strong>Impacto:</strong> {esc(b['impact'])}</p>
      <div class="code-row">
        <div><p class="code-label code-label-bad">Codigo con defecto</p>
          <pre class="code-blk code-bad">{esc(b['before'])}</pre></div>
        <div><p class="code-label code-label-good">Codigo corregido</p>
          <pre class="code-blk code-good">{esc(b['after'])}</pre></div>
      </div>
      <p class="block-label">Pruebas que detectaron el defecto:</p>
      <ul class="bug-tests">{tests_li}</ul>
    </div>
  </div>"""
    return html

# ─────────────────────────────────────────────────────────────────
# 9. Tarjetas globales
# ─────────────────────────────────────────────────────────────────
def global_cards():
    rc = "#22c55e" if pass_rate==100 else ("#f59e0b" if pass_rate>=80 else "#ef4444")
    return f"""
  <div class="cards-global">
    <div class="cg"><div class="cg-num" style="color:#3b82f6">{total}</div><div class="cg-lbl">Total</div></div>
    <div class="cg"><div class="cg-num" style="color:#22c55e">{passed}</div><div class="cg-lbl">Pasaron</div></div>
    <div class="cg"><div class="cg-num" style="color:#ef4444">{failed}</div><div class="cg-lbl">Fallaron</div></div>
    <div class="cg"><div class="cg-num" style="color:#8b5cf6;font-size:22px">{fmt_ms(duration)}</div><div class="cg-lbl">Duracion</div></div>
    <div class="cg cg-wide">
      <div class="pbar-top"><span style="font-size:12px;font-weight:700;color:#475569">Tasa global de exito</span>
        <span style="font-size:22px;font-weight:900;color:{rc}">{pass_rate}%</span></div>
      <div class="pbar-track"><div class="pbar-fill" style="width:{pass_rate}%;background:{rc}"></div></div>
      <div style="font-size:11px;color:#94a3b8;margin-top:6px">{passed} de {total} pruebas exitosas</div>
    </div>
  </div>"""

# ─────────────────────────────────────────────────────────────────
# 10. HTML completo
# ─────────────────────────────────────────────────────────────────
CSS = """
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',system-ui,sans-serif;background:#eef2f7;color:#2d3748;font-size:14px;line-height:1.5}
code{font-family:'Cascadia Code','Consolas',monospace;background:#edf2ff;color:#3730a3;padding:1px 6px;border-radius:4px;font-size:12px}
a{text-decoration:none;color:inherit}

/* ── Header ──────────────────────────── */
.hdr{background:linear-gradient(135deg,#0d2b6b 0%,#1849b5 100%);color:#fff}
.hdr-inner{max-width:1140px;margin:0 auto;padding:28px 32px 24px}
.hdr-brand-row{display:flex;align-items:center;gap:14px}
.hdr-logo{width:48px;height:48px;background:rgba(255,255,255,.15);border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:17px;font-weight:900;color:#fff;flex-shrink:0}
.hdr-brand{font-size:22px;font-weight:800;letter-spacing:-.5px}
.hdr-brand-sub{font-size:12px;color:rgba(255,255,255,.6);margin-top:2px}
.hdr-divider{height:1px;background:rgba(255,255,255,.15);margin:16px 0 14px}
.hdr-title{font-size:17px;font-weight:700}
.hdr-meta{margin-top:7px;display:flex;flex-wrap:wrap;gap:18px;font-size:12px;color:rgba(255,255,255,.65)}

/* ── Navegación sticky ────────────────── */
.sticky-nav{position:sticky;top:0;z-index:200;background:#162d59;box-shadow:0 2px 10px rgba(0,0,0,.35)}
.nav-inner{max-width:1140px;margin:0 auto;padding:0 24px;display:flex;align-items:center;gap:4px}
.nav-brand{font-size:13px;font-weight:800;color:rgba(255,255,255,.7);padding:0 12px 0 4px;white-space:nowrap;border-right:1px solid rgba(255,255,255,.12);margin-right:6px}
.nav-brand:hover{color:#fff}
.nav-group{display:flex;align-items:center}
.nav-a{display:flex;align-items:center;gap:6px;padding:11px 12px;font-size:12.5px;font-weight:600;color:rgba(255,255,255,.82);white-space:nowrap;transition:background .15s,color .15s;border-radius:0;cursor:pointer}
.nav-a:hover,.nav-item:hover>.nav-a{background:rgba(255,255,255,.1);color:#fff}
.nav-plain{font-size:12px;font-weight:500;color:rgba(255,255,255,.65)}
.nav-plain:hover{color:#fff;background:rgba(255,255,255,.08)}
.nav-badge{width:20px;height:20px;border-radius:5px;display:inline-flex;align-items:center;justify-content:center;font-size:11px;font-weight:900;color:#fff;flex-shrink:0}
.nav-cnt{background:rgba(255,255,255,.18);color:#fff;font-size:10px;font-weight:700;padding:1px 6px;border-radius:99px}
.nav-arrow{font-size:10px;opacity:.5;margin-left:2px}
.nav-item{position:relative}

/* ── Dropdown ─────────────────────────── */
.dropdown{display:none;position:absolute;top:calc(100% + 2px);left:0;background:#fff;border-radius:10px;box-shadow:0 8px 28px rgba(0,0,0,.18);min-width:210px;z-index:300;overflow:hidden;animation:ddFade .12s ease}
@keyframes ddFade{from{opacity:0;transform:translateY(-4px)}to{opacity:1;transform:translateY(0)}}
.nav-item:hover .dropdown{display:block}
.dd-header{padding:8px 14px 6px;font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.8px;color:#94a3b8;background:#f8fafc;border-bottom:1px solid #e2e8f0}
.dd-link{display:flex;align-items:center;gap:8px;padding:9px 14px;font-size:12.5px;font-weight:500;color:#334155;border-bottom:1px solid #f1f5f9;transition:background .1s}
.dd-link:last-child{border-bottom:none}
.dd-link:hover{background:#f0f7ff;color:#1a3a6b}
.dot{width:7px;height:7px;border-radius:50%;flex-shrink:0}
.dot-ok{background:#22c55e}.dot-err{background:#ef4444}
.dd-cnt{margin-left:auto;background:#f1f5f9;color:#64748b;font-size:10px;font-weight:700;padding:1px 6px;border-radius:99px}

/* ── Layout ───────────────────────────── */
.page{max-width:1140px;margin:0 auto;padding:0 32px 60px}
.sec-title{font-size:12px;font-weight:800;color:#1a3a6b;text-transform:uppercase;letter-spacing:1px;margin-bottom:14px;margin-top:28px}
.cards-global{display:flex;flex-wrap:wrap;gap:14px;background:#fff;border-radius:14px;padding:20px 24px;box-shadow:0 2px 12px rgba(0,0,0,.07)}
.cg{text-align:center;padding:4px 20px;border-right:1px solid #f1f5f9}
.cg:last-child{border-right:none}
.cg-wide{flex:1;min-width:200px;text-align:left;padding-left:24px}
.cg-num{font-size:30px;font-weight:900;line-height:1}
.cg-lbl{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.8px;color:#94a3b8;margin-top:4px}
.pbar-top{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px}
.pbar-track{height:11px;background:#e2e8f0;border-radius:99px;overflow:hidden}
.pbar-fill{height:100%;border-radius:99px}

/* ── Bloque de nivel ──────────────────── */
.nivel-block{margin-top:32px;border-radius:14px;overflow:hidden;box-shadow:0 2px 16px rgba(0,0,0,.08)}
.nivel-hdr{padding:16px 22px;color:#fff;display:flex;align-items:center;gap:14px}
.nivel-badge{width:40px;height:40px;border-radius:10px;background:rgba(255,255,255,.2);display:flex;align-items:center;justify-content:center;font-size:16px;font-weight:900;flex-shrink:0}
.nivel-info{flex:1}
.nivel-title{font-size:16px;font-weight:800}
.nivel-desc{font-size:12px;color:rgba(255,255,255,.7);margin-top:2px}
.nivel-body{background:#fff;padding:22px}
.mini-cards{display:flex;flex-wrap:wrap;gap:10px;margin-bottom:20px;padding:14px;background:#f8fafc;border-radius:10px;border-left:4px solid var(--acc)}
.mc{text-align:center;padding:4px 14px;border-right:1px solid #e2e8f0}
.mc:last-child{border-right:none}
.mc-rate{flex:1;min-width:160px;text-align:left;padding-left:18px}
.mc-num{font-size:24px;font-weight:900;line-height:1}
.mc-lbl{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.8px;color:#94a3b8;margin-top:3px}
.subsec{font-size:11px;font-weight:800;color:#64748b;text-transform:uppercase;letter-spacing:1px;margin:18px 0 10px;padding-bottom:5px;border-bottom:1px solid #e2e8f0}

/* ── Tabla ────────────────────────────── */
.tbl{width:100%;border-collapse:collapse;border-radius:10px;overflow:hidden;box-shadow:0 1px 8px rgba(0,0,0,.06)}
.tbl thead tr{background:#1a3a6b;color:#fff}
.tbl th{padding:10px 14px;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.7px;white-space:nowrap}
.tbl td{padding:10px 14px;border-bottom:1px solid #f1f5f9;font-size:13px}
.tbl tbody tr:last-child td{border-bottom:none}
.tbl tbody tr:hover td{background:#f8faff}
.tbl-anchor{color:#1a3a6b;font-weight:700}
.tbl-anchor:hover{text-decoration:underline}
.center{text-align:center}.dim{color:#94a3b8}.num-pass{color:#16a34a;font-weight:700}.num-fail{color:#dc2626;font-weight:700}
.badge{display:inline-block;padding:3px 10px;border-radius:5px;font-size:11px;font-weight:700;letter-spacing:.5px}
.badge-ok{background:#dcfce7;color:#15803d}.badge-err{background:#fee2e2;color:#b91c1c}
.chip{display:inline-block;padding:2px 9px;border-radius:5px;font-size:11px;font-weight:600;white-space:nowrap}
.chip-tec{background:#fef3c7;color:#92400e}

/* ── Suites de detalle ────────────────── */
.suite{margin-bottom:18px;border-radius:10px;overflow:hidden;box-shadow:0 1px 8px rgba(0,0,0,.06)}
.suite-hdr{padding:11px 16px;display:flex;align-items:center;gap:10px}
.suite-good{background:#f0fdf4;border-left:5px solid #22c55e}
.suite-bad{background:#fff5f5;border-left:5px solid #ef4444}
.suite-icon{font-size:13px;font-weight:900}
.suite-good .suite-icon{color:#16a34a}.suite-bad .suite-icon{color:#dc2626}
.suite-name{flex:1;font-weight:700;font-size:13px;color:#1e293b}
.suite-right{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.s-ok{color:#16a34a;font-weight:700;font-size:12px}.s-err{color:#dc2626;font-weight:700;font-size:12px}
.tbl-detail{border-radius:0;box-shadow:none}
.grp-row td{padding:7px 14px !important;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.5px;border-bottom:none !important}
.grp-pass td{background:#f0fdf4;color:#166534}.grp-fail td{background:#fff5f5;color:#991b1b}
.grp-meta{float:right;text-transform:none;font-weight:400;letter-spacing:0}
.g-ok{color:#16a34a;margin-left:10px}.g-err{color:#dc2626;margin-left:8px}
.icon-cell{width:40px;text-align:center;font-weight:900}
.tr-ok .icon-cell{color:#16a34a}.tr-err .icon-cell{color:#dc2626}.tr-err td:not(.icon-cell){color:#b91c1c}
.err-row{background:#fff5f5}.err-msg{font-family:'Cascadia Code',monospace;font-size:11px;color:#b91c1c;padding:4px 14px !important}

/* ── Bugs ─────────────────────────────── */
.bug-card{background:#fff;border-radius:12px;box-shadow:0 1px 8px rgba(0,0,0,.07);margin-bottom:18px;overflow:hidden;border-left:6px solid #ef4444}
.bug-hdr{background:#fff5f5;padding:13px 18px;display:flex;align-items:center;gap:10px;border-bottom:1px solid #fee2e2;flex-wrap:wrap}
.bug-id{background:#ef4444;color:#fff;padding:3px 10px;border-radius:5px;font-size:11px;font-weight:800;white-space:nowrap}
.bug-title{flex:1;font-weight:700;font-size:14px;color:#1e293b}
.bug-tags{display:flex;gap:7px}
.bug-sev,.bug-stat{padding:3px 10px;border-radius:5px;font-size:11px;font-weight:700}
.sev-media{background:#fef3c7;color:#92400e}.sev-alta{background:#fee2e2;color:#b91c1c}
.stat-fixed{background:#dcfce7;color:#15803d}.stat-open{background:#fee2e2;color:#b91c1c}
.bug-body{padding:16px 18px}
.info-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:12px}
.info-item{background:#f8fafc;border-radius:8px;padding:9px 12px}
.info-key{display:block;font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.8px;color:#94a3b8;margin-bottom:3px}
.block-label{font-size:11px;font-weight:700;color:#475569;margin-bottom:5px;text-transform:uppercase;letter-spacing:.5px}
.block-text{font-size:13px;color:#334155;line-height:1.7}
.code-row{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:12px}
.code-label{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.5px;margin-bottom:5px}
.code-label-bad{color:#b91c1c}.code-label-good{color:#15803d}
.code-blk{border-radius:8px;padding:14px;font-family:'Cascadia Code','Consolas',monospace;font-size:12px;line-height:1.7;overflow-x:auto;white-space:pre;background:#0f172a;color:#cbd5e1}
.code-bad{border-left:4px solid #ef4444}.code-good{border-left:4px solid #22c55e}
.bug-tests{list-style:none;padding:0;margin-top:5px}
.bug-tests li{padding:5px 0;border-bottom:1px solid #f1f5f9;font-size:12px;color:#475569}
.bug-tests li:last-child{border-bottom:none}

/* ── Footer ───────────────────────────── */
.footer{text-align:center;padding:24px 20px;color:#94a3b8;font-size:12px;border-top:1px solid #e2e8f0;margin-top:16px}
.footer strong{color:#475569}
@media print{
  body{background:#fff}
  .sticky-nav{display:none}
  .nivel-block,.suite,.bug-card,.tbl{box-shadow:none !important;border:1px solid #e2e8f0}
  .hdr,.nivel-hdr{print-color-adjust:exact;-webkit-print-color-adjust:exact}
}
"""

# Construir secciones
sections_html = ""
for nivel, files in NIVELES.items():
    color  = NIVEL_COLOR[nivel]
    desc   = NIVEL_DESC[nivel]
    icon   = NIVEL_ICON[nivel]
    nid    = NIVEL_IDS[nivel]
    t, p, f, _ = nivel_stats(files)
    sections_html += f"""
<div class="nivel-block" id="{nid}">
  <div class="nivel-hdr" style="background:{color}">
    <div class="nivel-badge">{icon}</div>
    <div class="nivel-info">
      <div class="nivel-title">{nivel}</div>
      <div class="nivel-desc">{desc}</div>
    </div>
    <div style="text-align:right;font-size:13px;font-weight:800;color:rgba(255,255,255,.9)">{p}/{t} exitosas</div>
  </div>
  <div class="nivel-body">
    {mini_cards(files, color)}
    <div class="subsec">Archivos de prueba</div>
    {nivel_table(files)}
    <div class="subsec">Detalle de cada prueba</div>
    {nivel_detail(files)}
  </div>
</div>"""

HTML = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>EduCampus — Informe de Pruebas Backend</title>
<style>{CSS}</style>
</head>
<body>
<div class="hdr">
  <div class="hdr-inner">
    <div class="hdr-brand-row">
      <div class="hdr-logo">EC</div>
      <div>
        <div class="hdr-brand">EduCampus — Backend</div>
        <div class="hdr-brand-sub">API REST · FastAPI + Python</div>
      </div>
    </div>
    <div class="hdr-divider"></div>
    <div class="hdr-title">Informe Completo de Pruebas — Backend</div>
    <div class="hdr-meta">
      <span>Fecha: {exec_date}</span>
      <span>Framework: pytest</span>
      <span>Carpeta: API-EduCampus/tests/</span>
      <span>Resultado: {passed}/{total} exitosas</span>
    </div>
  </div>
</div>

{nav_html()}

<div class="page">
  <div id="resumen-global">
    <div class="sec-title">Resumen Global</div>
    {global_cards()}
  </div>
  <div id="sec-bugs" style="margin-top:32px">
    <div class="sec-title">Defectos Detectados y Corregidos</div>
    {bugs_html()}
  </div>
  {sections_html}
</div>
<div class="footer">
  <strong>EduCampus — Backend</strong> · Informe Completo de Pruebas<br/>
  Generado el {exec_date}<br/>
  {passed} de {total} pruebas exitosas · Tasa de exito: {pass_rate}%
</div>
</body>
</html>"""

with open(HTML_OUT, "w", encoding="utf-8") as f:
    f.write(HTML)

print(f"\nReporte generado -> backend-report.html\n")
webbrowser.open(HTML_OUT.as_uri())
print("   El reporte se abrio en el navegador.\n")
