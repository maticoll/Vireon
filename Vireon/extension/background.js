chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "SAVE_TOKEN") {
    chrome.storage.local.set({ accessToken: message.token }, () => {
      console.log("🗃️ Token guardado exitosamente.");
    });
  }

  if (message.type === "GET_TOKEN") {
    chrome.storage.local.get("accessToken", (result) => {
      sendResponse({ token: result.accessToken });
    });
    return true;
  }
});
