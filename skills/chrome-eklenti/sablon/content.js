// Sayfa içi betik. Sayfanın kendi JS'ine erişemez, izole dünyada çalışır.

(function () {
  "use strict";

  // Element gelene kadar bekle. SPA'larda ve geç yüklenen sayfalarda gerekli.
  function bekle(secici, sure = 10000) {
    return new Promise((cozumle, reddet) => {
      const mevcut = document.querySelector(secici);
      if (mevcut) return cozumle(mevcut);

      const gozlemci = new MutationObserver(() => {
        const el = document.querySelector(secici);
        if (el) {
          gozlemci.disconnect();
          cozumle(el);
        }
      });
      gozlemci.observe(document.body, { childList: true, subtree: true });

      setTimeout(() => {
        gozlemci.disconnect();
        reddet(new Error(`bulunamadi: ${secici}`));
      }, sure);
    });
  }

  async function calistir() {
    const ayarlar = await chrome.storage.local.get(["apiAnahtari"]);
    const hedef = await bekle(".hedef-element");
    console.log("[eklenti] hedef bulundu", hedef, ayarlar);
    // İş buraya.
  }

  calistir().catch((h) => console.error("[eklenti]", h.message));

  // SPA'da adres değişince yeniden çalıştır.
  let sonAdres = location.href;
  new MutationObserver(() => {
    if (location.href !== sonAdres) {
      sonAdres = location.href;
      calistir().catch((h) => console.error("[eklenti]", h.message));
    }
  }).observe(document.body, { childList: true, subtree: true });
})();
