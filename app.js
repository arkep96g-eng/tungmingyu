(function(){
  var root=document.documentElement;
  function setLang(l,save){
    root.setAttribute('data-lang',l); root.setAttribute('lang', l==='zh'?'zh-Hant':'en');
    document.querySelectorAll('.lang button').forEach(function(b){b.setAttribute('aria-pressed', b.dataset.lang===l?'true':'false');});
    if(save){ try{localStorage.setItem('lang',l);}catch(e){} }
  }
  var saved=null; try{saved=localStorage.getItem('lang');}catch(e){}
  setLang(saved==='zh'?'zh':'en',false);
  document.querySelectorAll('.lang button').forEach(function(b){b.addEventListener('click',function(){setLang(b.dataset.lang,true);});});

  var bar=document.querySelector('.filter');
  if(bar){
    var cards=document.querySelectorAll('.fam');
    bar.addEventListener('click',function(e){
      var b=e.target.closest('button'); if(!b) return;
      bar.querySelectorAll('button').forEach(function(x){x.setAttribute('aria-pressed','false');});
      b.setAttribute('aria-pressed','true');
      var d=b.dataset.domain;
      cards.forEach(function(c){ c.hidden = !(d==='all' || c.dataset.domain===d); });
    });
  }
})();
