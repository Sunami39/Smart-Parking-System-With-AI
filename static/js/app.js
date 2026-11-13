fetch('/api/status').then(r=>r.json()).then(d=>document.documentElement.dataset.updated=d.updated).catch(()=>{});
