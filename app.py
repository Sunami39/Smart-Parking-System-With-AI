from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from datetime import datetime
import sqlite3, os, random
ROOT=os.path.dirname(os.path.abspath(__file__))
DB=os.path.join(ROOT,"data","parking.db")
app=Flask(__name__); app.secret_key="replace-this-demo-secret"
SEED=[("A01","Zone A",0),("A02","Zone A",1),("A03","Zone A",0),("A04","Zone A",1),("B01","Zone B",0),("B02","Zone B",0),("B03","Zone B",1),("B04","Zone B",0),("C01","Zone C",1),("C02","Zone C",0),("C03","Zone C",0),("C04","Zone C",1)]
def conn():
 c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c
def now(): return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
def init():
 os.makedirs(os.path.dirname(DB),exist_ok=True)
 with conn() as c:
  c.execute("CREATE TABLE IF NOT EXISTS parking_spaces(id INTEGER PRIMARY KEY,label TEXT UNIQUE,zone TEXT,occupied INTEGER,active INTEGER DEFAULT 1,updated_at TEXT)")
  c.execute("CREATE TABLE IF NOT EXISTS parking_status(id INTEGER PRIMARY KEY,space_id INTEGER,occupied INTEGER,observed_at TEXT)")
  if c.execute("SELECT COUNT(*) FROM parking_spaces").fetchone()[0]==0:
   for label,zone,state in SEED:
    cur=c.execute("INSERT INTO parking_spaces(label,zone,occupied,updated_at) VALUES(?,?,?,?)",(label,zone,state,now()))
    c.execute("INSERT INTO parking_status(space_id,occupied,observed_at) VALUES(?,?,?)",(cur.lastrowid,state,now()))
def spaces(active=True):
 with conn() as c:
  return c.execute("SELECT * FROM parking_spaces"+(" WHERE active=1" if active else "")+" ORDER BY zone,label").fetchall()
def log(sid,state):
 with conn() as c: c.execute("INSERT INTO parking_status(space_id,occupied,observed_at) VALUES(?,?,?)",(sid,state,now()))
@app.route("/")
def index():
 ss=spaces(); total=len(ss); occ=sum(x["occupied"] for x in ss)
 with conn() as c: hist=c.execute("SELECT p.label,h.occupied,h.observed_at FROM parking_status h JOIN parking_spaces p ON p.id=h.space_id ORDER BY h.id DESC LIMIT 7").fetchall()
 return render_template("index.html",spaces=ss,total=total,occupied=occ,free=total-occ,history=hist,now=datetime.now().strftime("%d %b %Y · %I:%M %p"))
@app.route("/admin")
def admin(): return render_template("admin.html",spaces=spaces(False))
@app.route("/presentation")
def presentation(): return render_template("presentation.html")
@app.route("/api/status")
def status():
 ss=spaces(); occ=sum(x["occupied"] for x in ss)
 return jsonify(total=len(ss),occupied=occ,available=len(ss)-occ,updated=now(),spaces=[dict(label=x["label"],zone=x["zone"],occupied=bool(x["occupied"])) for x in ss])
@app.post("/admin/toggle/<int:sid>")
def toggle(sid):
 with conn() as c:
  r=c.execute("SELECT * FROM parking_spaces WHERE id=?",(sid,)).fetchone()
  if r:
   state=1-int(r["occupied"]); c.execute("UPDATE parking_spaces SET occupied=?,updated_at=? WHERE id=?",(state,now(),sid)); log(sid,state)
   flash(f'{r["label"]} updated to {"occupied" if state else "available"}.',"success")
 return redirect(url_for("admin"))
@app.post("/admin/add")
def add():
 label=request.form.get("label","").strip().upper(); zone=request.form.get("zone","Zone A")
 try:
  with conn() as c:
   cur=c.execute("INSERT INTO parking_spaces(label,zone,occupied,updated_at) VALUES(?,?,0,?)",(label,zone,now())); log(cur.lastrowid,0)
  flash(f"Slot {label} added.","success")
 except sqlite3.IntegrityError: flash("Slot label already exists.","error")
 return redirect(url_for("admin"))
@app.post("/admin/delete/<int:sid>")
def delete(sid):
 with conn() as c: c.execute("UPDATE parking_spaces SET active=0 WHERE id=?",(sid,))
 flash("Slot removed from active monitoring.","success"); return redirect(url_for("admin"))
@app.post("/demo/refresh")
def refresh():
 ss=spaces()
 if ss:
  s=random.choice(ss); state=1-int(s["occupied"])
  with conn() as c: c.execute("UPDATE parking_spaces SET occupied=?,updated_at=? WHERE id=?",(state,now(),s["id"]))
  log(s["id"],state); flash(f'Demo simulator updated {s["label"]}.',"success")
 return redirect(url_for("index"))
@app.route("/health")
def health(): return jsonify(ok=True,mode="demo")
init()
if __name__=="__main__": app.run(host="0.0.0.0", port=5000, debug=False)
