import React,{createContext,useContext,useEffect,useState,useCallback} from 'react'
import snap from './data/snapshot.json'
const S:any=snap; const BASE=(import.meta as any).env.VITE_API_URL||''
export async function call(path:string,init?:RequestInit){const c=new AbortController();const t=setTimeout(()=>c.abort(),5000)
 try{const r=await fetch(BASE+path,{...init,signal:c.signal});if(!r.ok)throw new Error('HTTP '+r.status);return await r.json()}finally{clearTimeout(t)}}
export const ORDER=['STABLE','LOW','MEDIUM','HIGH','CRITICAL']
export const COLOR:any={CRITICAL:'#dc2626',HIGH:'#ea580c',MEDIUM:'#ca8a04',LOW:'#65a30d',STABLE:'#16a34a'}
const TH:[string,number][]=[['CRITICAL',3],['HIGH',5],['MEDIUM',8],['LOW',14]]
export const classify=(d:number)=>(TH.find(([,l])=>d<=l)||['STABLE'])[0]
export const worst=(rs:any[])=>rs.reduce((a,r)=>ORDER.indexOf(r.risk)>ORDER.indexOf(a)?r.risk:a,'STABLE')
const Ctx=createContext<any>(null); export const useData=()=>useContext(Ctx)
const KEYS:[string,string][]=[['phcs','/api/phcs'],['risks','/api/risks'],['recs','/api/redistribution'],['forecasts','/api/forecasts'],['history','/api/history']]
export function DataProvider({children}:any){
 const [d,setD]=useState<any>({...S,sim:null}); const [offline,setOff]=useState<string[]>([]); const [loading,setL]=useState(true)
 const reload=useCallback(async()=>{setL(true);const res=await Promise.allSettled(KEYS.map(([,p])=>call(p)));const next:any={},off:string[]=[]
  res.forEach((r,i)=>{const k=KEYS[i][0];if(r.status==='fulfilled'&&r.value){next[k]=r.value}else{next[k]=S[k];off.push(k)}})
  try{next.sim=(await call('/api/dashboard')).simulation}catch{next.sim=null}
  setD(next);setOff(off);setL(false)},[])
 useEffect(()=>{reload()},[reload])
 const simulate=async()=>{try{await call('/api/simulation/outbreak',{method:'POST'});await reload();return null}catch(e){return localSim(d,setD)}}
 const reset=async()=>{try{await call('/api/simulation/reset',{method:'POST'})}catch{}; await reload()}
 return <Ctx.Provider value={{...d,offline,loading,reload,simulate,reset}}>{children}</Ctx.Provider>}
const metrics=(phcs:any[],risks:any[])=>({available_beds:phcs.reduce((a,p)=>a+p.beds-p.occupied_beds,0),ors_demand:Math.round(risks.filter(r=>r.medicine==='ORS').reduce((a,r)=>a+r.predicted_daily_demand,0)),
 critical_phcs:phcs.filter(p=>worst(risks.filter(r=>r.phc_id===p.id))==='CRITICAL').length,high_risk_phcs:phcs.filter(p=>['HIGH','CRITICAL'].includes(worst(risks.filter(r=>r.phc_id===p.id)))).length})
// Client-side approximation used only when the backend is unreachable.
function localSim(d:any,setD:any){const hr=new Set(d.phcs.filter((p:any)=>p.district==='Hyderabad Rural').map((p:any)=>p.id)),before=metrics(d.phcs,d.risks)
 const risks=d.risks.map((r:any)=>{if(!hr.has(r.phc_id))return r;const dm=r.predicted_daily_demand*(r.medicine==='ORS'?1.81:1.5),days=r.current_stock/dm;return{...r,predicted_daily_demand:+dm.toFixed(1),days_remaining:+days.toFixed(1),risk:classify(days)}})
 const phcs=d.phcs.map((p:any)=>hr.has(p.id)?{...p,occupied_beds:Math.min(p.beds,Math.floor(p.occupied_beds*1.3)+2)}:p).map((p:any)=>({...p,risk:worst(risks.filter((r:any)=>r.phc_id===p.id))}))
 const after=metrics(phcs,risks),change_pct:any={};Object.keys(before).forEach(k=>change_pct[k]=+(100*(after[k]-before[k])/Math.max(before[k],1)).toFixed(1))
 setD({...d,risks,phcs,sim:{district:'Hyderabad Rural',before,after,change_pct,local:true}})}
