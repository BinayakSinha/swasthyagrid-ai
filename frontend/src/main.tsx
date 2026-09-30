import React from 'react'; import {createRoot} from 'react-dom/client'; import './index.css'
import {DataProvider,useData} from './api'; import {Dashboard,Phcs,PhcDetail,Redistribution,Emergency,Copilot} from './pages'
class EB extends React.Component<any,any>{state={e:null};static getDerivedStateFromError(e:any){return{e}}
 componentDidUpdate(p:any){if(p.k!==this.props.k&&this.state.e)this.setState({e:null})}
 render(){return this.state.e?<div className="p-6 bg-white border border-red-200 rounded">This page hit an error ({String(this.state.e)}). Other pages still work.</div>:this.props.children}}
const NAV=[['dashboard','Dashboard'],['phcs','PHCs'],['redistribution','Redistribution'],['emergency','Emergency'],['copilot','AI Copilot']]
function App(){const [h,setH]=React.useState(location.hash||'#/dashboard'); const {offline,loading,reload}=useData()
 React.useEffect(()=>{const f=()=>setH(location.hash||'#/dashboard');addEventListener('hashchange',f);return()=>removeEventListener('hashchange',f)},[])
 const [, page, id]=h.split('/'); const P:any={dashboard:Dashboard,phcs:id?PhcDetail:Phcs,redistribution:Redistribution,emergency:Emergency,copilot:Copilot}[page]||Dashboard
 return <div className="min-h-screen flex flex-col">
  <header className="bg-slate-900 text-white px-5 py-3 flex flex-wrap items-center gap-x-6 gap-y-2">
   <div><div className="font-bold tracking-wide">SWASTHYAGRID AI</div><div className="text-xs text-slate-400">See the shortage before the patient does · prototype · synthetic data</div></div>
   <nav className="flex gap-1 flex-wrap">{NAV.map(([k,l])=><a key={k} href={'#/'+k} className={'px-3 py-1 rounded text-sm '+(page===k||(!page&&k==='dashboard')?'bg-slate-700':'hover:bg-slate-800')}>{l}</a>)}</nav>
   <button onClick={reload} className="ml-auto text-xs border border-slate-600 rounded px-2 py-1">{loading?'Loading…':'Refresh'}</button></header>
  {offline.length>0&&<div className="bg-amber-100 text-amber-900 text-sm px-5 py-2 border-b border-amber-300">Backend unavailable for: {offline.join(', ')}. Showing bundled demo snapshot (synthetic). Live actions may be limited.</div>}
  <main className="p-4 md:p-6 max-w-7xl w-full mx-auto"><EB k={h}><P id={id}/></EB></main></div>}
createRoot(document.getElementById('root')!).render(<DataProvider><App/></DataProvider>)
