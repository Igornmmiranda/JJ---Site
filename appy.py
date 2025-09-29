import os
from flask import Flask, render_template_string, request, redirect, url_for, flash
import psycopg
from psycopg.rows import tuple_row

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://neondb_owner:npg_H3G6ltChrJgT@ep-noisy-credit-adf5zzh9-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require")
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "jj-secret")

BASE_HTML = """
<!doctype html>
<html lang="pt-br">
<head>
  <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{{ title or "Grupo de Estudos JJ" }}</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>html{scroll-behavior:smooth}body{font-family:Inter,system-ui,-apple-system,Segoe UI,Roboto,Ubuntu,Cantarell,Noto Sans,sans-serif}</style>
</head>
<body class="min-h-screen bg-gradient-to-b from-indigo-50 to-white text-gray-900">
  <header class="sticky top-0 z-20 backdrop-blur bg-white/70 border-b">
    <div class="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div class="h-9 w-9 rounded-2xl bg-indigo-600 text-white grid place-items-center font-bold">JJ</div>
        <div><h1 class="text-xl font-semibold leading-tight">Grupo de Estudos JJ</h1><p class="text-xs text-gray-500 -mt-1">Pesquisa • Projetos • Comunidade</p></div>
      </div>
      <nav class="hidden md:flex items-center gap-6 text-sm">
        <a href="#sobre" class="hover:text-indigo-600">Sobre</a>
        <a href="#diretoria" class="hover:text-indigo-600">Diretoria</a>
        <a href="#projetos" class="hover:text-indigo-600">Projetos</a>
        <a href="#agenda" class="hover:text-indigo-600">Agenda</a>
        <a href="#contato" class="hover:text-indigo-600">Contato</a>
      </nav>
    </div>
  </header>
  {% with messages = get_flashed_messages() %}
    {% if messages %}
      <div class="max-w-6xl mx-auto px-4 pt-4"><div class="p-3 rounded-xl bg-emerald-50 text-emerald-800 border border-emerald-200 text-sm">{{ messages[0] }}</div></div>
    {% endif %}
  {% endwith %}
  {{ content|safe }}
  <footer class="border-t">
    <div class="max-w-6xl mx-auto px-4 py-6 flex flex-col md:flex-row items-center justify-between gap-3 text-sm text-gray-600">
      <div>© <span id="ano"></span> Grupo de Estudos JJ</div>
      <div class="flex items-center gap-4"><a href="#" class="hover:text-indigo-600">Código de Conduta</a><a href="#" class="hover:text-indigo-600">Documentação</a></div>
    </div>
  </footer>
  <script>document.getElementById("ano").textContent=new Date().getFullYear()</script>
</body>
</html>
"""

INDEX_HTML = """
<section class="max-w-6xl mx-auto px-4 pt-14 pb-10">
  <div class="grid md:grid-cols-2 gap-10 items-center">
    <div>
      <h2 class="text-4xl md:text-5xl font-extrabold tracking-tight">Estudar bem, praticar sempre, compartilhar tudo.</h2>
      <p class="mt-4 text-lg text-gray-600">O JJ transforma leitura em prática. Revisões, réplicas, bancos de dados e projetos para eventos acadêmicos.</p>
      <div class="mt-6 flex flex-wrap gap-3">
        <a href="#projetos" class="px-5 py-2.5 rounded-xl bg-indigo-600 text-white font-medium shadow hover:shadow-md">Ver projetos</a>
        <a href="#contato" class="px-5 py-2.5 rounded-xl border font-medium hover:bg-gray-50">Quero participar</a>
      </div>
    </div>
    <div class="rounded-3xl overflow-hidden shadow-xl border">
      <img src="https://images.unsplash.com/photo-1529336953121-a0ce66f616b0?q=80&w=1280&auto=format&fit=crop" alt="Sessão de estudos" class="w-full h-full object-cover">
    </div>
  </div>
</section>
<section id="sobre" class="max-w-6xl mx-auto px-4 py-10">
  <div class="grid md:grid-cols-3 gap-6">
    <div class="p-6 rounded-2xl border shadow-sm bg-white"><h3 class="text-lg font-semibold">Missão</h3><p class="mt-2 text-gray-600">Formar talentos que dominem método científico e dados, conectando teoria a prática.</p></div>
    <div class="p-6 rounded-2xl border shadow-sm bg-white"><h3 class="text-lg font-semibold">Trilhas</h3><p class="mt-2 text-gray-600">Leitura guiada, réplicas, labs de SQL/Python, escrita científica e conferências.</p></div>
    <div class="p-6 rounded-2xl border shadow-sm bg-white"><h3 class="text-lg font-semibold">Valores</h3><p class="mt-2 text-gray-600">Rigor, colaboração, autoria coletiva e impacto aplicado.</p></div>
  </div>
</section>
<section id="diretoria" class="max-w-6xl mx-auto px-4 py-10">
  <h3 class="text-2xl font-bold">Diretoria</h3>
  <div class="mt-6 grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
    {% for d in directors %}
    <div class="group p-5 rounded-2xl border bg-white shadow-sm hover:shadow-md transition">
      <div class="aspect-[4/3] w-full overflow-hidden rounded-xl"><img src="{{ d[6] }}" alt="{{ d[1] }}" class="h-full w-full object-cover group-hover:scale-105 transition"></div>
      <div class="mt-4">
        <h4 class="text-lg font-semibold">{{ d[1] }}</h4>
        <p class="text-sm text-indigo-600 font-medium">{{ d[2] }}</p>
        <p class="mt-2 text-sm text-gray-600">{{ d[3] }}</p>
        <div class="mt-3 flex items-center gap-3 text-sm">
          <a class="px-3 py-1.5 rounded-lg border hover:bg-gray-50" href="mailto:{{ d[4] }}">Email</a>
          <a class="px-3 py-1.5 rounded-lg border hover:bg-gray-50" href="{{ d[5] }}">LinkedIn</a>
        </div>
      </div>
    </div>
    {% endfor %}
  </div>
</section>
<section id="projetos" class="max-w-6xl mx-auto px-4 py-10">
  <h3 class="text-2xl font-bold">Projetos em destaque</h3>
  <div class="mt-6 grid md:grid-cols-3 gap-6">
    {% for p in projects %}
    <a href="{{ p[4] }}" class="p-5 rounded-2xl border bg-white shadow-sm hover:shadow-md transition block">
      <span class="text-xs uppercase tracking-wide text-indigo-600 font-semibold">{{ p[2] }}</span>
      <h4 class="mt-2 text-lg font-semibold">{{ p[1] }}</h4>
      <p class="mt-1 text-sm text-gray-600">{{ p[3] }}</p>
    </a>
    {% endfor %}
  </div>
</section>
<section id="agenda" class="max-w-6xl mx-auto px-4 py-10">
  <h3 class="text-2xl font-bold">Próximos encontros</h3>
  <div class="mt-6 grid md:grid-cols-2 gap-6">
    {% for m in meetings %}
    <div class="p-5 rounded-2xl border bg-white shadow-sm">
      <div class="text-sm text-gray-500">{{ m[1] }}</div>
      <div class="text-lg font-semibold">{{ m[2] }}</div>
      <div class="text-sm text-gray-600">{{ m[3] }}</div>
      <a href="{{ m[4] }}" class="mt-3 inline-block px-3 py-1.5 rounded-lg border hover:bg-gray-50 text-sm">Entrar</a>
    </div>
    {% endfor %}
  </div>
</section>
<section id="contato" class="max-w-6xl mx-auto px-4 py-12">
  <div class="rounded-3xl border bg-white shadow-sm p-6 md:p-8">
    <h3 class="text-2xl font-bold">Fale com a JJ</h3>
    <p class="mt-2 text-gray-600">Dúvidas, parcerias ou inscrição? Envie uma mensagem.</p>
    <form class="mt-6 grid md:grid-cols-2 gap-4" method="post" action="/contato">
      <input class="w-full rounded-xl border px-4 py-3" name="name" placeholder="Seu nome">
      <input class="w-full rounded-xl border px-4 py-3" name="email" placeholder="Seu e-mail">
      <input class="md:col-span-2 w-full rounded-xl border px-4 py-3" name="subject" placeholder="Assunto">
      <textarea class="md:col-span-2 w-full rounded-xl border px-4 py-3 min-h-[120px]" name="body" placeholder="Mensagem"></textarea>
      <button class="md:col-span-2 px-5 py-3 rounded-xl bg-indigo-600 text-white font-medium hover:shadow-md">Enviar</button>
    </form>
  </div>
</section>
"""

def db():
    return psycopg.connect(DATABASE_URL, row_factory=tuple_row)

def init_db():
    with db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
            create table if not exists directors(
              id serial primary key,
              name text not null,
              role text not null,
              bio text not null,
              email text not null,
              linkedin text not null,
              photo text not null
            );
            create table if not exists projects(
              id serial primary key,
              title text not null,
              tag text not null,
              status text not null,
              link text not null
            );
            create table if not exists meetings(
              id serial primary key,
              date_label text not null,
              subject text not null,
              place text not null,
              link text not null
            );
            create table if not exists messages(
              id serial primary key,
              name text not null,
              email text not null,
              subject text not null,
              body text not null,
              created_at timestamp not null default now()
            );
            """)
            cur.execute("select count(*) from directors"); c = cur.fetchone()[0]
            if c == 0:
                cur.executemany("insert into directors(name,role,bio,email,linkedin,photo) values (%s,%s,%s,%s,%s,%s)", [
                    ("Igor","Diretor-Geral","Coordena estratégia, agenda e parcerias.","igor@jj.study","#","https://images.unsplash.com/photo-1603415526960-f7e0328d13e8?q=80&w=640&auto=format&fit=crop"),
                    ("Gustavo","Diretor de Pesquisa","Lidera trilhas de pesquisa e revisão de literatura.","gustavo@jj.study","#","https://images.unsplash.com/photo-1544005313-94ddf0286df2?q=80&w=640&auto=format&fit=crop"),
                    ("Carlos Eduardo","Diretor de Projetos","Conduz projetos aplicados e hackathons acadêmicos.","carloseduardo@jj.study","#","https://images.unsplash.com/photo-1547425260-76bcadfb4f2c?q=80&w=640&auto=format&fit=crop"),
                    ("Isabela","Diretora de Pessoas","Recrutamento, cultura e capacitação.","isabela@jj.study","#","https://images.unsplash.com/photo-1544005316-04ce1f3c95fa?q=80&w=640&auto=format&fit=crop")
                ])
            cur.execute("select count(*) from projects"); c = cur.fetchone()[0]
            if c == 0:
                cur.executemany("insert into projects(title,tag,status,link) values (%s,%s,%s,%s)", [
                    ("Revisão Sistemática: IA em Gestão","Pesquisa","Em andamento","#"),
                    ("Base de Casos JJ (SQL/ETL)","Dados","Em andamento","#"),
                    ("Workshop: Escrita Científica","Capacitação","Inscrições abertas","#")
                ])
            cur.execute("select count(*) from meetings"); c = cur.fetchone()[0]
            if c == 0:
                cur.executemany("insert into meetings(date_label,subject,place,link) values (%s,%s,%s,%s)", [
                    ("Seg 19:00","Seminário: Métodos Quantitativos","Google Meet","#"),
                    ("Qui 18:30","Leitura guiada: Paper da semana","Sala 203 / Meet","#")
                ])
            conn.commit()

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/")
def home():
    with db() as conn, conn.cursor() as cur:
        cur.execute("select id,name,role,bio,email,linkedin,photo from directors order by id")
        directors = cur.fetchall()
        cur.execute("select id,title,tag,status,link from projects order by id")
        projects = cur.fetchall()
        cur.execute("select id,date_label,subject,place,link from meetings order by id")
        meetings = cur.fetchall()
    html = render_template_string(INDEX_HTML, directors=directors, projects=projects, meetings=meetings)
    return render_template_string(BASE_HTML, content=html)

@app.post("/contato")
def contato():
    name = request.form.get("name","").strip()
    email = request.form.get("email","").strip()
    subject = request.form.get("subject","").strip()
    body = request.form.get("body","").strip()
    if not name or not email or not subject or not body:
        flash("Preencha todos os campos.")
        return redirect(url_for("home")+"#contato")
    with db() as conn, conn.cursor() as cur:
        cur.execute("insert into messages(name,email,subject,body) values (%s,%s,%s,%s)", (name,email,subject,body))
        conn.commit()
    flash("Mensagem enviada com sucesso.")
    return redirect(url_for("home")+"#contato")

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))

