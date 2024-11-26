"use strict";(self.webpackChunk_N_E=self.webpackChunk_N_E||[]).push([[985],{5079:function(e,t,n){n.d(t,{A:function(){return k}});var r=n(4246),i=n(6184),o=n(5006);n(7378);var a=n(947),l=n(6415),c=n(7226),d=n(9357),u=n(4438),s=n(3206),h=n(9662),p=n(4670);let[f,v]=(0,n(2740).V)(),g={};function m(e){let{value:t,defaultValue:n,onChange:i,multiple:a,children:l}=(0,c.w)("ChipGroup",g,e),[d,u]=(0,o.C)({value:t,defaultValue:n,finalValue:a?[]:null,onChange:i});return(0,r.jsx)(f,{value:{isChipSelected:e=>Array.isArray(d)?d.includes(e):e===d,onChange:e=>{let t=e.currentTarget.value;Array.isArray(d)?u(d.includes(t)?d.filter(e=>e!==t):[...d,t]):u(t)},multiple:a},children:l})}m.displayName="@mantine/core/ChipGroup";var y={root:"m_f59ffda3",label:"m_be049a53","label--outline":"m_3904c1af","label--filled":"m_fa109255","label--light":"m_f7e165c3",iconWrapper:"m_9ac86df9",checkIcon:"m_d6d72580",input:"m_bde07329"};let b={type:"checkbox"},x=(0,l.Z)((e,{size:t,radius:n,variant:r,color:i,autoContrast:o})=>{let l=e.variantColorResolver({color:i||e.primaryColor,theme:e,variant:r||"filled",autoContrast:o});return{root:{"--chip-fz":(0,a.yv)(t),"--chip-size":(0,a.ap)(t,"chip-size"),"--chip-radius":void 0===n?void 0:(0,a.H5)(n),"--chip-checked-padding":(0,a.ap)(t,"chip-checked-padding"),"--chip-padding":(0,a.ap)(t,"chip-padding"),"--chip-icon-size":(0,a.ap)(t,"chip-icon-size"),"--chip-bg":i||r?l.background:void 0,"--chip-hover":i||r?l.hover:void 0,"--chip-color":i||r?l.color:void 0,"--chip-bd":i||r?l.border:void 0,"--chip-spacing":(0,a.ap)(t,"chip-spacing")}}}),k=(0,h.d5)((e,t)=>{let n=(0,c.w)("Chip",b,e),{classNames:a,className:l,style:h,styles:f,unstyled:g,vars:m,id:k,checked:C,defaultChecked:w,onChange:z,value:S,wrapperProps:R,type:M,disabled:_,children:j,size:Z,variant:F,icon:E,rootRef:A,autoContrast:I,mod:L,...T}=n,W=(0,d.y)({name:"Chip",classes:y,props:n,className:l,style:h,classNames:a,styles:f,unstyled:g,vars:m,varsResolver:x}),N=v(),B=(0,i.M)(k),{styleProps:D,rest:H}=(0,u.c)(T),[P,V]=(0,o.C)({value:C,defaultValue:w,finalValue:!1,onChange:z}),G=N?{checked:N.isChipSelected(S),onChange:e=>{N.onChange(e),z?.(e.currentTarget.checked)},type:N.multiple?"checkbox":"radio"}:{},O=G.checked||P;return(0,r.jsxs)(s.x,{size:Z,variant:F,ref:A,mod:L,...W("root"),...D,...R,children:[(0,r.jsx)("input",{type:M,...W("input"),checked:O,onChange:e=>V(e.currentTarget.checked),id:B,disabled:_,ref:t,value:S,...G,...H}),(0,r.jsxs)("label",{htmlFor:B,"data-checked":O||void 0,"data-disabled":_||void 0,...W("label",{variant:F||"filled"}),children:[O&&(0,r.jsx)("span",{...W("iconWrapper"),children:E||(0,r.jsx)(p.n,{...W("checkIcon")})}),(0,r.jsx)("span",{children:j})]})]})});k.classes=y,k.displayName="@mantine/core/Chip",k.Group=m},2220:function(e,t,n){n.d(t,{i:function(){return f}});var r=n(4246);n(7378);var i=n(947),o=n(6415),a=n(9104),l=n(7226),c=n(9357),d=n(3206),u=n(9662),s={root:"m_3eebeb36",label:"m_9e365f20"};let h={orientation:"horizontal"},p=(0,o.Z)((e,{color:t,variant:n,size:r})=>({root:{"--divider-color":t?(0,a.p)(t,e):void 0,"--divider-border-style":n,"--divider-size":(0,i.ap)(r,"divider-size")}})),f=(0,u.d5)((e,t)=>{let n=(0,l.w)("Divider",h,e),{classNames:i,className:o,style:a,styles:u,unstyled:f,vars:v,color:g,orientation:m,label:y,labelPosition:b,mod:x,...k}=n,C=(0,c.y)({name:"Divider",classes:s,props:n,className:o,style:a,classNames:i,styles:u,unstyled:f,vars:v,varsResolver:p});return(0,r.jsx)(d.x,{ref:t,mod:[{orientation:m,"with-label":!!y},x],...C("root"),...k,role:"separator",children:y&&(0,r.jsx)(d.x,{component:"span",mod:{position:b},...C("label"),children:y})})});f.classes=s,f.displayName="@mantine/core/Divider"},4310:function(e,t,n){n.d(t,{S:function(){return g}});var r=n(4246),i=n(7378),o=n(5006),a=n(183),l=n(7226),c=n(9662),d=n(657);let u={multiple:!1},s=(0,i.forwardRef)((e,t)=>{let{onChange:n,children:o,multiple:c,accept:d,name:s,form:h,resetRef:p,disabled:f,capture:v,inputProps:g,...m}=(0,l.w)("FileButton",u,e),y=(0,i.useRef)();return(0,a.kR)(p,()=>{y.current.value=""}),(0,r.jsxs)(r.Fragment,{children:[o({onClick:()=>{f||y.current?.click()},...m}),(0,r.jsx)("input",{style:{display:"none"},type:"file",accept:d,multiple:c,onChange:e=>{c?n(Array.from(e.currentTarget.files)):n(e.currentTarget.files[0]||null)},ref:(0,a.Yx)(t,y),name:s,form:h,capture:v,...g})]})});s.displayName="@mantine/core/FileButton";var h=n(7935),p=n(4749);let f={valueComponent:({value:e})=>(0,r.jsx)("div",{style:{overflow:"hidden",textOverflow:"ellipsis",whiteSpace:"nowrap"},children:Array.isArray(e)?e.map(e=>e.name).join(", "):e?.name})},v=(0,c.d5)((e,t)=>{let n=(0,l.w)("FileInput",f,e),{unstyled:c,vars:u,onChange:v,value:g,defaultValue:m,multiple:y,accept:b,name:x,form:k,valueComponent:C,clearable:w,clearButtonProps:z,readOnly:S,capture:R,fileInputProps:M,rightSection:_,size:j,placeholder:Z,resetRef:F,...E}=n,A=(0,i.useRef)(null),[I,L]=(0,o.C)({value:g,defaultValue:m,onChange:v,finalValue:y?[]:null}),T=Array.isArray(I)?0!==I.length:null!==I,W=_||(w&&T&&!S?(0,r.jsx)(d.P,{...z,variant:"subtle",onClick:()=>L(y?[]:null),size:j,unstyled:c}):null);return(0,i.useEffect)(()=>{(Array.isArray(I)&&0===I.length||null===I)&&A.current?.()},[I]),(0,r.jsx)(s,{onChange:L,multiple:y,accept:b,name:x,form:k,resetRef:(0,a.Yx)(A,F),disabled:S,capture:R,inputProps:M,children:e=>(0,r.jsx)(p.M,{component:"button",ref:t,rightSection:W,...e,...E,__staticSelector:"FileInput",multiline:!0,type:"button",pointer:!0,__stylesApiProps:n,unstyled:c,size:j,children:T?(0,r.jsx)(C,{value:I}):(0,r.jsx)(h.I.Placeholder,{children:Z})})})});v.classes=p.M.classes,v.displayName="@mantine/core/FileInput";let g=v},8090:function(e,t,n){n.d(t,{g:function(){return j}});var r=n(4246),i=n(5773),o=n(808),a=n(7378),l=a.useLayoutEffect,c=function(e){var t=a.useRef(e);return l(function(){t.current=e}),t},d=function(e,t){if("function"==typeof e){e(t);return}e.current=t},u=function(e,t){var n=(0,a.useRef)();return(0,a.useCallback)(function(r){e.current=r,n.current&&d(n.current,null),n.current=t,t&&d(t,r)},[t])},s={"min-height":"0","max-height":"none",height:"0",visibility:"hidden",overflow:"hidden",position:"absolute","z-index":"-1000",top:"0",right:"0"},h=function(e){Object.keys(s).forEach(function(t){e.style.setProperty(t,s[t],"important")})},p=null,f=function(e,t){var n=e.scrollHeight;return"border-box"===t.sizingStyle.boxSizing?n+t.borderSize:n-t.paddingSize},v=function(){},g=["borderBottomWidth","borderLeftWidth","borderRightWidth","borderTopWidth","boxSizing","fontFamily","fontSize","fontStyle","fontWeight","letterSpacing","lineHeight","paddingBottom","paddingLeft","paddingRight","paddingTop","tabSize","textIndent","textRendering","textTransform","width","wordBreak"],m=!!document.documentElement.currentStyle,y=function(e){var t=window.getComputedStyle(e);if(null===t)return null;var n=g.reduce(function(e,n){return e[n]=t[n],e},{}),r=n.boxSizing;if(""===r)return null;m&&"border-box"===r&&(n.width=parseFloat(n.width)+parseFloat(n.borderRightWidth)+parseFloat(n.borderLeftWidth)+parseFloat(n.paddingRight)+parseFloat(n.paddingLeft)+"px");var i=parseFloat(n.paddingBottom)+parseFloat(n.paddingTop),o=parseFloat(n.borderBottomWidth)+parseFloat(n.borderTopWidth);return{sizingStyle:n,paddingSize:i,borderSize:o}};function b(e,t,n){var r=c(n);a.useLayoutEffect(function(){var n=function(e){return r.current(e)};if(e)return e.addEventListener(t,n),function(){return e.removeEventListener(t,n)}},[])}var x=function(e){b(window,"resize",e)},k=function(e){b(document.fonts,"loadingdone",e)},C=["cacheMeasurements","maxRows","minRows","onChange","onHeightChange"],w=a.forwardRef(function(e,t){var n=e.cacheMeasurements,r=e.maxRows,l=e.minRows,c=e.onChange,d=void 0===c?v:c,s=e.onHeightChange,g=void 0===s?v:s,m=(0,o.Z)(e,C),b=void 0!==m.value,w=a.useRef(null),z=u(w,t),S=a.useRef(0),R=a.useRef(),M=function(){var e,t,i,o,a,c,d,u,s,v,m,b=w.current,x=n&&R.current?R.current:y(b);if(x){R.current=x;var k=(e=b.value||b.placeholder||"x",void 0===(t=l)&&(t=1),void 0===(i=r)&&(i=1/0),p||((p=document.createElement("textarea")).setAttribute("tabindex","-1"),p.setAttribute("aria-hidden","true"),h(p)),null===p.parentNode&&document.body.appendChild(p),o=x.paddingSize,a=x.borderSize,d=(c=x.sizingStyle).boxSizing,Object.keys(c).forEach(function(e){p.style[e]=c[e]}),h(p),p.value=e,u=f(p,x),p.value=e,u=f(p,x),p.value="x",v=(s=p.scrollHeight-o)*t,"border-box"===d&&(v=v+o+a),u=Math.max(v,u),m=s*i,"border-box"===d&&(m=m+o+a),[u=Math.min(m,u),s]),C=k[0],z=k[1];S.current!==C&&(S.current=C,b.style.setProperty("height",C+"px","important"),g(C,{rowHeight:z}))}};return a.useLayoutEffect(M),x(M),k(M),a.createElement("textarea",(0,i.Z)({},m,{onChange:function(e){b||M(),d(e)},ref:z}))}),z=n(4284),S=n(7226),R=n(9662),M=n(4749);let _={},j=(0,R.d5)((e,t)=>{let{autosize:n,maxRows:i,minRows:o,__staticSelector:a,resize:l,...c}=(0,S.w)("Textarea",_,e),d=n&&"test"!=(void 0!==z&&z.env?"production":"development");return(0,r.jsx)(M.M,{component:d?w:"textarea",ref:t,...c,__staticSelector:a||"Textarea",multiline:!0,"data-no-overflow":n&&void 0===i||void 0,__vars:{"--input-resize":l},...d?{maxRows:i,minRows:o}:{}})});j.classes=M.M.classes,j.displayName="@mantine/core/Textarea"},3688:function(e,t,n){n.d(t,{yr:function(){return r}});function r(e){return t=>{let n="nativeEvent"in t?t.nativeEvent:t;e.forEach(([e,r,i={preventDefault:!0}])=>{(function(e,t){let{alt:n,ctrl:r,meta:i,mod:o,shift:a,key:l}=e,{altKey:c,ctrlKey:d,metaKey:u,shiftKey:s,key:h}=t;if(n!==c)return!1;if(o){if(!d&&!u)return!1}else if(r!==d||i!==u)return!1;return a===s&&!!l&&(h.toLowerCase()===l.toLowerCase()||t.code.replace("Key","").toLowerCase()===l.toLowerCase())})(function(e){let t=e.toLowerCase().split("+").map(e=>e.trim()),n={alt:t.includes("alt"),ctrl:t.includes("ctrl"),meta:t.includes("meta"),mod:t.includes("mod"),shift:t.includes("shift")},r=["alt","ctrl","meta","shift","mod"],i=t.find(e=>!r.includes(e));return{...n,key:i}}(e),n)&&(i.preventDefault&&t.preventDefault(),r(n))})}}},1314:function(e,t,n){n.d(t,{Z:function(){return r}});/**
 * @license @tabler/icons-react v3.19.0 - MIT
 *
 * This source code is licensed under the MIT license.
 * See the LICENSE file in the root directory of this source tree.
 */var r=(0,n(3460).Z)("outline","circle-chevron-left","IconCircleChevronLeft",[["path",{d:"M13 15l-3 -3l3 -3",key:"svg-0"}],["path",{d:"M21 12a9 9 0 1 0 -18 0a9 9 0 0 0 18 0z",key:"svg-1"}]])},2067:function(e,t,n){n.d(t,{Z:function(){return r}});/**
 * @license @tabler/icons-react v3.19.0 - MIT
 *
 * This source code is licensed under the MIT license.
 * See the LICENSE file in the root directory of this source tree.
 */var r=(0,n(3460).Z)("outline","circle-chevron-right","IconCircleChevronRight",[["path",{d:"M11 9l3 3l-3 3",key:"svg-0"}],["path",{d:"M3 12a9 9 0 1 0 18 0a9 9 0 0 0 -18 0z",key:"svg-1"}]])},4043:function(e,t,n){n.d(t,{Z:function(){return r}});/**
 * @license @tabler/icons-react v3.19.0 - MIT
 *
 * This source code is licensed under the MIT license.
 * See the LICENSE file in the root directory of this source tree.
 */var r=(0,n(3460).Z)("outline","clock","IconClock",[["path",{d:"M3 12a9 9 0 1 0 18 0a9 9 0 0 0 -18 0",key:"svg-0"}],["path",{d:"M12 7v5l3 3",key:"svg-1"}]])},5263:function(e,t,n){n.d(t,{Z:function(){return r}});/**
 * @license @tabler/icons-react v3.19.0 - MIT
 *
 * This source code is licensed under the MIT license.
 * See the LICENSE file in the root directory of this source tree.
 */var r=(0,n(3460).Z)("outline","dice-3","IconDice3",[["path",{d:"M3 3m0 2a2 2 0 0 1 2 -2h14a2 2 0 0 1 2 2v14a2 2 0 0 1 -2 2h-14a2 2 0 0 1 -2 -2z",key:"svg-0"}],["circle",{cx:"8.5",cy:"8.5",r:".5",fill:"currentColor",key:"svg-1"}],["circle",{cx:"15.5",cy:"15.5",r:".5",fill:"currentColor",key:"svg-2"}],["circle",{cx:"12",cy:"12",r:".5",fill:"currentColor",key:"svg-3"}]])},5086:function(e,t,n){n.d(t,{Z:function(){return r}});/**
 * @license @tabler/icons-react v3.19.0 - MIT
 *
 * This source code is licensed under the MIT license.
 * See the LICENSE file in the root directory of this source tree.
 */var r=(0,n(3460).Z)("outline","info-square-rounded","IconInfoSquareRounded",[["path",{d:"M12 9h.01",key:"svg-0"}],["path",{d:"M11 12h1v4h1",key:"svg-1"}],["path",{d:"M12 3c7.2 0 9 1.8 9 9s-1.8 9 -9 9s-9 -1.8 -9 -9s1.8 -9 9 -9z",key:"svg-2"}]])},6270:function(e,t,n){n.d(t,{Z:function(){return r}});/**
 * @license @tabler/icons-react v3.19.0 - MIT
 *
 * This source code is licensed under the MIT license.
 * See the LICENSE file in the root directory of this source tree.
 */var r=(0,n(3460).Z)("outline","refresh","IconRefresh",[["path",{d:"M20 11a8.1 8.1 0 0 0 -15.5 -2m-.5 -4v4h4",key:"svg-0"}],["path",{d:"M4 13a8.1 8.1 0 0 0 15.5 2m.5 4v-4h-4",key:"svg-1"}]])},2579:function(e,t,n){n.d(t,{Z:function(){return r}});/**
 * @license @tabler/icons-react v3.19.0 - MIT
 *
 * This source code is licensed under the MIT license.
 * See the LICENSE file in the root directory of this source tree.
 */var r=(0,n(3460).Z)("outline","reload","IconReload",[["path",{d:"M19.933 13.041a8 8 0 1 1 -9.925 -8.788c3.899 -1 7.935 1.007 9.425 4.747",key:"svg-0"}],["path",{d:"M20 4v5h-5",key:"svg-1"}]])}}]);