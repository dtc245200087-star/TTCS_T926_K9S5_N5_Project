import React, {useEffect, useMemo, useState} from 'react';
import {apiFetch} from '../api.js';

export default function AcceptancePage({user}) {
  const [tasks,setTasks]=useState([]), [batches,setBatches]=useState([]), [project,setProject]=useState('');
  const [date,setDate]=useState(new Date().toISOString().slice(0,10));
  const [values,setValues]=useState({}), [error,setError]=useState(''), [busy,setBusy]=useState(false);
  async function load() {
    const [a,b]=await Promise.all([apiFetch('/api/acceptance/tasks'),apiFetch('/api/acceptance')]);
    if(!a.ok || !b.ok) throw new Error('Không tải được dữ liệu nghiệm thu');
    setTasks(await a.json());setBatches(await b.json());
  }
  useEffect(()=>{load().catch(e=>setError(e.message));},[]);
  const projects=[...new Set(tasks.map(t=>t.cong_trinh).filter(Boolean))];
  const selected=tasks.filter(t=>t.cong_trinh===project);
  const approved=batches.filter(b=>b.project===project && b.status==='approved');
  const previous=useMemo(()=>Object.fromEntries(selected.map(t=>{
    const last=approved.find(b=>b.lines.some(l=>l.task_id===t.id));
    return [t.id,Number(last?.lines.find(l=>l.task_id===t.id)?.cumulative||0)];
  })),[batches,project,tasks]);
  async function create(e){
    e.preventDefault();setBusy(true);setError('');
    try{
      const lines=selected.filter(t=>values[t.id]!==undefined && values[t.id]!=='')
        .map(t=>({task_id:t.id,cumulative:values[t.id]}));
      const r=await apiFetch('/api/acceptance',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({project,batch_date:date,lines})});
      const data=await r.json();if(!r.ok)throw new Error(data.message||'Không lập được phiếu');
      setValues({});await load();
    }catch(e){setError(e.message)}finally{setBusy(false)}
  }
  async function approve(id){
    if(!window.confirm('Duyệt phiếu nghiệm thu này?'))return;
    const r=await apiFetch(`/api/acceptance/${id}/approve`,{method:'POST'});
    const data=await r.json();if(!r.ok){setError(data.message);return;}await load();
  }
  async function upload(id,file){
    if(!file)return;const form=new FormData();form.append('image',file);
    const r=await apiFetch(`/api/acceptance/${id}/images`,{method:'POST',body:form});
    const data=await r.json();if(!r.ok){setError(data.message);return;}await load();
  }
  return <div className="content"><section className="panel" style={{padding:20}}>
    <h2>S-36 · Phiếu nghiệm thu theo đợt</h2>
    {error&&<p role="alert" style={{color:'crimson'}}>{error}</p>}
    <form onSubmit={create}>
      <label>Công trình <select required value={project} onChange={e=>{setProject(e.target.value);setValues({})}}><option value="">Chọn công trình</option>{projects.map(p=><option key={p}>{p}</option>)}</select></label>
      <label>Ngày nghiệm thu <input type="date" required value={date} onChange={e=>setDate(e.target.value)}/></label>
      <table><thead><tr><th>Hạng mục</th><th>Lũy kế đã duyệt</th><th>Số đo S-26</th><th>Lũy kế mới</th><th>Khối lượng đợt</th></tr></thead>
      <tbody>{selected.map(t=><tr key={t.id}><td>{t.ten}</td><td>{previous[t.id]}</td><td>{t.s26_measured??'Chưa có số liệu'}</td>
      <td><input type="number" min={previous[t.id]} step="any" value={values[t.id]??''} onChange={e=>setValues(v=>({...v,[t.id]:e.target.value}))}/></td>
      <td>{values[t.id]!==undefined && values[t.id]!=='' ? Number(values[t.id])-previous[t.id]: '—'}</td></tr>)}</tbody></table>
      <button type="submit" disabled={busy||!project||!['admin','manager','engineer'].includes(user.role)}>{busy?'Đang lưu...':'Lập phiếu nháp'}</button>
    </form></section>
    <section className="panel" style={{padding:20,marginTop:16}}><h2>Danh sách phiếu</h2>
      {batches.map(b=><article key={b.id} style={{borderBottom:'1px solid #ddd',padding:12}}>
        <b>Phiếu #{b.id}</b> · {b.project} · {b.batch_date} · {b.status==='approved'?'Đã duyệt':'Bản nháp'}
        <ul>{b.lines.map(l=><li key={l.task_id}>Hạng mục #{l.task_id}: lũy kế {l.cumulative}, đợt {l.quantity}</li>)}</ul>
        {b.images.map(img=><a key={img.id} href={`/api/acceptance/images/${img.id}`} target="_blank" rel="noreferrer">{img.original_name} </a>)}
        {b.status==='draft'&&<div><label>Ảnh hiện trường <input type="file" accept="image/png,image/jpeg" onChange={e=>upload(b.id,e.target.files?.[0])}/></label>
          {['admin','manager'].includes(user.role)&&<button type="button" onClick={()=>approve(b.id)}>Duyệt phiếu</button>}</div>}
      </article>)}
    </section>
  </div>;
}
