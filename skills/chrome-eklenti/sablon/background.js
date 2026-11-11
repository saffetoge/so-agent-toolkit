// Service worker. Sürekli çalışmaz, birkaç saniye boşta kalınca uyur.
// Durumu global değişkende TUTMA, chrome.storage.local kullan.

chrome.runtime.onInstalled.addListener(() => {
  console.log("[eklenti] kuruldu");
});

// Content script'ten gelen istekler. Dış API çağrısı buradan yapılır ki
// CORS engeline takılmasın (manifest'te host_permissions şart).
chrome.runtime.onMessage.addListener((istek, gonderen, cevapla) => {
  if (istek.tur === "apiCagir") {
    fetch(istek.adres, { headers: istek.baslik || {} })
      .then((y) => y.json())
      .then((veri) => cevapla({ tamam: true, veri }))
      .catch((h) => cevapla({ tamam: false, hata: h.message }));
    return true; // asenkron cevap için zorunlu
  }
});
