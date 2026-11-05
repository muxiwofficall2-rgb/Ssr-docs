self.addEventListener('install',()=>self.skipWaiting());
self.addEventListener('activate',e=>e.waitUntil(clients.claim()));
self.addEventListener('push',e=>{
  const d=e.data?e.data.json():{};
  e.waitUntil((async()=>{
    await self.registration.showNotification(d.title||'Omad Tour',{
      body:d.body||'',icon:'/icon-192.png',badge:'/badge-96.png',
      vibrate:[200,100,200],tag:'omad-chat',renotify:true,silent:false,timestamp:Date.now(),data:{url:'/#chat'}});
    const cs=await clients.matchAll({type:'window'});cs.forEach(c=>c.postMessage({t:'push'}));
  })());
});
self.addEventListener('notificationclick',e=>{
  e.notification.close();
  e.waitUntil((async()=>{
    const cs=await clients.matchAll({type:'window',includeUncontrolled:true});
    for(const c of cs){if('focus' in c){c.postMessage({t:'open'});return c.focus()}}
    return clients.openWindow('/#chat');
  })());
});
