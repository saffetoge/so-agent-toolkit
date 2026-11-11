const alan = document.getElementById("apiAnahtari");
const durum = document.getElementById("durum");

chrome.storage.local.get(["apiAnahtari"]).then(({ apiAnahtari }) => {
  if (apiAnahtari) alan.value = apiAnahtari;
});

document.getElementById("kaydet").addEventListener("click", async () => {
  await chrome.storage.local.set({ apiAnahtari: alan.value.trim() });
  durum.textContent = "Kaydedildi";
  setTimeout(() => (durum.textContent = ""), 1500);
});
