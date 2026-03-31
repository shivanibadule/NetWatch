const NETWATCH_API_URL = "http://127.0.0.1:8000/ftp-event";
// Helper function to send an event to NetWatch dashboard
function sendToNetwatch(eventData) {
  fetch(NETWATCH_API_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(eventData)
  }).catch(err => console.error("NetWatch Ext: Failed to reach backend.", err));
}

// -------------------------------------------------------------
// 1. TRACK DOWNLOADS
// -------------------------------------------------------------
chrome.downloads.onChanged.addListener((downloadDelta) => {
  // Only log the download once it has successfully completed
  if (downloadDelta.state && downloadDelta.state.current === 'complete') {
    chrome.downloads.search({ id: downloadDelta.id }, (results) => {
      if (results && results.length > 0) {
        const item = results[0];

        // 1. Get the final, actual filename from the user's hard drive
        let finalFilename = "downloaded_file";
        if (item.filename) {
          finalFilename = item.filename.split('\\').pop().split('/').pop();
        }

        // 2. Extact the exact website the file came from
        let sourceWebsite = "Unknown Website";

        // Strategy 1: The standard direct URL
        try {
          if (item.url && !item.url.startsWith("blob:") && !item.url.startsWith("data:")) {
            const h = new URL(item.url).hostname;
            if (h) sourceWebsite = h;
          }
        } catch (e) { }

        // Strategy 2: The Referrer (the webpage tab you were browsing)
        if (sourceWebsite === "Unknown Website") {
          try {
            if (item.referrer) {
              const h = new URL(item.referrer).hostname;
              if (h) sourceWebsite = h;
            }
          } catch (e) { }
        }

        // Strategy 3: Deep inspection of complex blob chunks (blob:https://github.com/uuid)
        if (sourceWebsite === "Unknown Website") {
          try {
            if (item.url && item.url.startsWith("blob:")) {
              const cleanUrl = item.url.substring(5); // Rip off the blob: part
              const h = new URL(cleanUrl).hostname;
              if (h) sourceWebsite = h;
            }
          } catch (e) { }
        }

        // Strategy 4: The Final URL Chrome resolved to
        if (sourceWebsite === "Unknown Website") {
          try {
            if (item.finalUrl && !item.finalUrl.startsWith("blob:") && !item.finalUrl.startsWith("data:")) {
              const h = new URL(item.finalUrl).hostname;
              if (h) sourceWebsite = h;
            }
          } catch (e) { }
        }

        // Failsafe format
        if (sourceWebsite === "") {
          sourceWebsite = "Local App / Script";
        }

        // Send the fully baked data to NetWatch
        sendToNetwatch({
          event: "download",
          ip: "Local Browser",
          username: sourceWebsite,
          filename: finalFilename,
          file_size: item.fileSize || item.totalBytes || 0,
          timestamp: new Date().toISOString()
        });
      }
    });
  }
});

// -------------------------------------------------------------
// 2. TRACK FILE UPLOADS
// -------------------------------------------------------------
// -------------------------------------------------------------
// TRACK FILE UPLOADS (WORKS WITH DRIVE / GMAIL)
// -------------------------------------------------------------
chrome.webRequest.onBeforeSendHeaders.addListener(
  (details) => {
    console.log("WEB REQUEST:", details.method, details.url);

    const method = details.method;

    if (method === "POST" || method === "PUT") {

      let site = "Unknown";

      try {
        site = new URL(details.url).hostname;
      } catch (e) { }

      const url = details.url.toLowerCase();

      if (
        url.includes("upload") ||
        url.includes("drive") ||
        url.includes("attachment") ||
        url.includes("files")
      ) {

        sendToNetwatch({
          event: "upload",
          ip: "Local Browser",
          username: site,
          filename: "browser_upload",
          file_size: 0,
          timestamp: new Date().toISOString()
        });

      }

    }

  },
  { urls: ["<all_urls>"] },
  ["requestHeaders"]
);

// -------------------------------------------------------------
// 3. TRACK LOGIN EVENTS
// -------------------------------------------------------------
chrome.webRequest.onBeforeRequest.addListener(
  (details) => {

    if (details.method === "POST") {

      const loginKeywords = ["login", "signin", "auth", "session"];

      const url = details.url.toLowerCase();

      const isLogin = loginKeywords.some(keyword => url.includes(keyword));

      if (isLogin) {

        let site = "Unknown Site";

        try {
          site = new URL(details.url).hostname;
        } catch (e) { }

        sendToNetwatch({
          event: "login",
          ip: "Local Browser",
          username: site,
          filename: "login_attempt",
          file_size: 0,
          timestamp: new Date().toISOString()
        });

      }

    }

  },
  { urls: ["<all_urls>"] }
);