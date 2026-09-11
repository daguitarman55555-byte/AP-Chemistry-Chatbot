import React, {useMemo} from 'react';
import katex from 'katex';
import 'katex/dist/katex.min.css';
import 'katex/contrib/mhchem';

export default function MathText({text}) {
 const parts=useMemo(()=>{
  const regex=/\$\$([\s\S]+?)\$\$|\\\[([\s\S]+?)\\\]|\\\(([\s\S]+?)\\\)|\$([^$\n]+?)\$/g;
  const output=[];let last=0;let m;
  while((m=regex.exec(text))){
   if(m.index>last)output.push({text:text.slice(last,m.index)});
   const tex=m[1]??m[2]??m[3]??m[4];
   try{output.push({html:katex.renderToString(tex,{displayMode:!!(m[1]||m[2]),throwOnError:true,trust:false,strict:'error',maxSize:10,maxExpand:100,macros:{}})})}
   catch{output.push({text:m[0]})}
   last=regex.lastIndex;
  }
  output.push({text:text.slice(last)});return output;
 },[text]);
 return <div className="message-text">{parts.map((p,i)=>p.html?<span key={i} dangerouslySetInnerHTML={{__html:p.html}}/>:<React.Fragment key={i}>{p.text}</React.Fragment>)}</div>;
}
