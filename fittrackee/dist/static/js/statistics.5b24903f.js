"use strict";(self["webpackChunkfittrackee_client"]=self["webpackChunkfittrackee_client"]||[]).push([[193],{7749:function(e,s,t){t.r(s),t.d(s,{default:function(){return A}});var r=t(6252),a=t(2262),l=t(3577),o=t(3324),c=t(7402);const n={class:"chart-menu"},i={class:"chart-arrow"},u={class:"time-frames custom-checkboxes-group"},d={class:"time-frames-checkboxes custom-checkboxes"},p=["id","name","checked","onInput"],m={class:"chart-arrow"};var v=(0,r.aZ)({emits:["arrowClick","timeFrameUpdate"],setup(e,{emit:s}){let t=(0,a.iH)("month");const o=["week","month","year"];function c(e){t.value=e,s("timeFrameUpdate",e)}return(e,v)=>((0,r.wg)(),(0,r.iD)("div",n,[(0,r._)("div",i,[(0,r._)("i",{class:"fa fa-chevron-left","aria-hidden":"true",onClick:v[0]||(v[0]=e=>s("arrowClick",!0))})]),(0,r._)("div",u,[(0,r._)("div",d,[((0,r.wg)(),(0,r.iD)(r.HY,null,(0,r.Ko)(o,(s=>(0,r._)("div",{class:"time-frame custom-checkbox",key:s},[(0,r._)("label",null,[(0,r._)("input",{type:"radio",id:s,name:s,checked:(0,a.SU)(t)===s,onInput:e=>c(s)},null,40,p),(0,r._)("span",null,(0,l.zw)(e.$t(`statistics.TIME_FRAMES.${s}`)),1)])]))),64))])]),(0,r._)("div",m,[(0,r._)("i",{class:"fa fa-chevron-right","aria-hidden":"true",onClick:v[1]||(v[1]=e=>s("arrowClick",!1))})])]))}}),k=t(3744);const S=(0,k.Z)(v,[["__scopeId","data-v-af15954c"]]);var w=S,f=t(631);const _={class:"sports-menu"},h=["id","name","checked","onInput"],U={class:"sport-label"};var b=(0,r.aZ)({props:{userSports:null,selectedSportIds:{default:()=>[]}},emits:["selectedSportIdsUpdate"],setup(e,{emit:s}){const t=e,{t:c}=(0,o.QT)(),n=(0,r.f3)("sportColors"),{selectedSportIds:i}=(0,a.BK)(t),u=(0,r.Fl)((()=>(0,f.xH)(t.userSports,c)));function d(e){s("selectedSportIdsUpdate",e)}return(e,s)=>{const t=(0,r.up)("SportImage");return(0,r.wg)(),(0,r.iD)("div",_,[((0,r.wg)(!0),(0,r.iD)(r.HY,null,(0,r.Ko)((0,a.SU)(u),(e=>((0,r.wg)(),(0,r.iD)("label",{type:"checkbox",key:e.id,style:(0,l.j5)({color:e.color?e.color:(0,a.SU)(n)[e.label]})},[(0,r._)("input",{type:"checkbox",id:e.id,name:e.label,checked:(0,a.SU)(i).includes(e.id),onInput:s=>d(e.id)},null,40,h),(0,r.Wm)(t,{"sport-label":e.label,color:e.color},null,8,["sport-label","color"]),(0,r._)("span",U,(0,l.zw)(e.translatedLabel),1)],4)))),128))])}}});const I=b;var g=I,T=t(9318);const y={key:0,id:"user-statistics"};var C=(0,r.aZ)({props:{sports:null,user:null},setup(e){const s=e,{t:t}=(0,o.QT)(),{sports:l,user:n}=(0,a.BK)(s);let i=(0,a.iH)("month");const u=(0,a.iH)(v(i.value)),d=(0,r.Fl)((()=>(0,f.xH)(s.sports,t))),p=(0,a.iH)(S(s.sports));function m(e){i.value=e,u.value=v(i.value)}function v(e){return(0,T.aZ)(new Date,e,s.user.weekm)}function k(e){u.value=(0,T.FN)(u.value,e,s.user.weekm)}function S(e){return e.map((e=>e.id))}function _(e){p.value.includes(e)?p.value=p.value.filter((s=>s!==e)):p.value.push(e)}return(0,r.YP)((()=>s.sports),(e=>{p.value=S(e)})),(e,s)=>(0,a.SU)(d)?((0,r.wg)(),(0,r.iD)("div",y,[(0,r.Wm)(w,{onTimeFrameUpdate:m,onArrowClick:k}),(0,r.Wm)(c.Z,{sports:(0,a.SU)(l),user:(0,a.SU)(n),chartParams:u.value,"displayed-sport-ids":p.value,fullStats:!0},null,8,["sports","user","chartParams","displayed-sport-ids"]),(0,r.Wm)(g,{"selected-sport-ids":p.value,"user-sports":(0,a.SU)(l),onSelectedSportIdsUpdate:_},null,8,["selected-sport-ids","user-sports"])])):(0,r.kq)("",!0)}});const F=(0,k.Z)(C,[["__scopeId","data-v-7d54529b"]]);var Z=F,D=t(5630),H=t(8602),x=t(9917);const E={id:"statistics",class:"view"},R={key:0,class:"container"};var W=(0,r.aZ)({setup(e){const s=(0,x.o)(),t=(0,r.Fl)((()=>s.getters[H.YN.GETTERS.AUTH_USER_PROFILE])),o=(0,r.Fl)((()=>s.getters[H.O8.GETTERS.SPORTS].filter((e=>t.value.sports_list.includes(e.id)))));return(e,s)=>{const c=(0,r.up)("Card");return(0,r.wg)(),(0,r.iD)("div",E,[(0,a.SU)(t).username?((0,r.wg)(),(0,r.iD)("div",R,[(0,r.Wm)(c,null,{title:(0,r.w5)((()=>[(0,r.Uk)((0,l.zw)(e.$t("statistics.STATISTICS")),1)])),content:(0,r.w5)((()=>[(0,r.Wm)(Z,{class:(0,l.C_)({"stats-disabled":0===(0,a.SU)(t).nb_workouts}),user:(0,a.SU)(t),sports:(0,a.SU)(o)},null,8,["class","user","sports"])])),_:1}),0===(0,a.SU)(t).nb_workouts?((0,r.wg)(),(0,r.j4)(D.Z,{key:0})):(0,r.kq)("",!0)])):(0,r.kq)("",!0)])}}});const P=(0,k.Z)(W,[["__scopeId","data-v-2e341d4e"]]);var A=P}}]);
//# sourceMappingURL=statistics.5b24903f.js.map