import { useEffect, useState } from "react";
import { api, authed } from "../../lib/api";
import { Card } from "../components/Card";

export default function Projects(){
  const [items,setItems]=useState<any[]|null>(null);
  useEffect(()=>{ api.get("/api/v1/projects").then(setItems).catch(()=>setItems([])); },[]);
  const canWrite = authed.hasRole(["admin","maintainer"]);
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">Projects</h2>
        {canWrite && <button className="px-3 py-1.5 rounded-xl bg-white/10 hover:bg-white/15" onClick={async()=>{
          const name=prompt("Project name?");
          if(name){ await api.post("/api/v1/projects",{name}); const list=await api.get("/api/v1/projects"); setItems(list); }
        }}>+ New</button>}
      </div>
      {(items?.length||0)===0 && <div className="opacity-80 text-sm">No projects yet.</div>}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {(items||[]).map(p=> <Card key={p.id} title={p.name} subtitle={p.status||"—"} />)}
      </div>
    </div>
  );
}