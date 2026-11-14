// Inject in a YouTube Studio tab (correct channel selected), then: bbRun(rawUrl, fileName, title, desc, dateStr|null, 'HH:MM'); poll window._res
// dateStr null = Studio default (tomorrow); 'today' = today; else 'DD Mon YYYY' typed into the date picker input.
const sl=ms=>new Promise(r=>setTimeout(r,ms));
window.bbRun=async(url,name,title,desc,date,hhmm)=>{ window._res='running';
 try{ (document.querySelector('ytcp-button.ytcpAppHeaderCreateIcon')||document.querySelector('#create-icon')).click(); await sl(1200); document.querySelector('#text-item-0')?.click(); await sl(2500);
 const b=await (await fetch(url)).blob(); if(b.size<100000){window._res='bad blob '+b.size; return}
 const inp=document.querySelector('ytcp-uploads-file-picker input[type=file]'); if(!inp){window._res='no input';return}
 const dt=new DataTransfer(); dt.items.add(new File([b],name,{type:'video/mp4'})); inp.files=dt.files; inp.dispatchEvent(new Event('change',{bubbles:true})); await sl(7000);
 const d=document.querySelector('ytcp-uploads-dialog'); const tb=d.querySelectorAll('#textbox'); const set=(el,t)=>{el.focus(); el.innerText=t; el.dispatchEvent(new InputEvent('input',{bubbles:true}));}; set(tb[0],title); await sl(300); set(tb[1],desc); await sl(300);
 const mfk=d.querySelector('tp-yt-paper-radio-button[name="VIDEO_MADE_FOR_KIDS_MFK"]'); if(mfk && mfk.getAttribute('aria-checked')!=='true') mfk.click(); await sl(500);
 d.querySelector('#step-badge-3').click(); await sl(1500); d.querySelector('#second-container-expand-button').click(); await sl(1200);
 if(date==='today'){d.querySelector('#datepicker-trigger').click(); await sl(1000); document.querySelector('span.calendar-day.today').click(); await sl(800);}
 else if(date){d.querySelector('#datepicker-trigger').click(); await sl(1000); const di=[...document.querySelectorAll('ytcp-date-picker input, tp-yt-paper-dialog input')].find(e=>e.offsetParent); di.focus(); di.select(); document.execCommand('insertText',false,date); di.dispatchEvent(new Event('input',{bubbles:true})); di.dispatchEvent(new KeyboardEvent('keydown',{key:'Enter',keyCode:13,bubbles:true})); await sl(1000);}
 const ti=d.querySelector('#time-of-day-container input'); ti.click(); await sl(900); const it=[...document.querySelectorAll('tp-yt-paper-item')].find(e=>e.innerText.trim()===hhmm); it.scrollIntoView(); await sl(300); it.click(); await sl(600);
 const when=d.querySelector('#datepicker-trigger').innerText.trim()+' '+ti.value; window._when=when;
 for(let k=0;k<4;k++){ const got=[...document.querySelectorAll('ytcp-button,button,tp-yt-paper-button')].find(e=>/^Got it$/i.test(e.innerText.trim())&&e.offsetParent); if(got){got.click(); await sl(1000);} let s=document.querySelector('ytcp-video-share-dialog'); if(s&&s.offsetParent&&/scheduled/i.test(s.innerText)) break; for(let i=0;i<60;i++){const bt=d.querySelector('#done-button'); if(bt && !bt.hasAttribute('disabled') && bt.getAttribute('aria-disabled')!=='true'){bt.click(); break} await sl(3000);} await sl(5000);}
 const s=document.querySelector('ytcp-video-share-dialog'); window._res=(s&&s.offsetParent?s.innerText.replace(/\s+/g,' ').slice(0,100):'no share')+' | '+when+' | '+((s?.innerText.match(/shorts\/([\w-]{11})/)||['',''])[1]);
 }catch(e){window._res='ERR '+e+' when='+window._when}};
'loaded';
