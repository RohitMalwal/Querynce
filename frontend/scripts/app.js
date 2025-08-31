/* -----------------------------
   Querynce frontend (app.js)
   Main logic, imports ui.js helpers
   ----------------------------- */
   window.__QUERYNCE_BASE_URL__ = "http://127.0.0.1:5000";
   import {
    setLoading,
    clearError,
    setError,
    showEmpty,
    showDoc,
    addBubble,
    populateDocUI,
    scrollChatToBottom
  } from "./ui.js";
  
  const BASE_URL = window.__QUERYNCE_BASE_URL__ || "";
  
  /* State */
  let sourceType = "url"; // "url" | "pdf"
  let doc = null;
  let fileName = "";
  
  /* Elements */
  const btnSourceUrl = document.getElementById("btnSourceUrl");
  const btnSourcePdf = document.getElementById("btnSourcePdf");
  const rowUrl = document.getElementById("rowUrl");
  const rowPdf = document.getElementById("rowPdf");
  const inpUrl = document.getElementById("inpUrl");
  const btnProcessUrl = document.getElementById("btnProcessUrl");
  const btnProcessPdf = document.getElementById("btnProcessPdf");
  const filePdf = document.getElementById("filePdf");
  const pdfName = document.getElementById("pdfName");
  const btnChoosePdf = document.getElementById("btnChoosePdf");
  const errIngest = document.getElementById("errIngest");
  
  const resultSkeleton = document.getElementById("resultSkeleton");
  const resultEmpty = document.getElementById("resultEmpty");
  const resultDoc = document.getElementById("resultDoc");
  const docIdEl = document.getElementById("docId");
  const docTitleEl = document.getElementById("docTitle");
  const docSummaryEl = document.getElementById("docSummary");
  const docBulletsEl = document.getElementById("docBullets");
  
  const btnCopy = document.getElementById("btnCopy");
  const btnExport = document.getElementById("btnExport");
  
  const chatScroll = document.getElementById("chatScroll");
  const inpMessage = document.getElementById("inpMessage");
  const btnSend = document.getElementById("btnSend");
  
  /* Helpers */
  function isYouTubeUrl(url) {
    return /(?:youtube\.com\/watch\?v=|youtu\.be\/)/i.test(url);
  }
  
  function enableChatReady() {
    inpMessage.disabled = false;
    inpMessage.placeholder = "Ask a question about the document…";
    inpMessage.value = "";
    btnSend.disabled = true;
  }
  
  /* Source switching */
  function setSource(s) {
    sourceType = s;
    btnSourceUrl.classList.toggle("is-active", s === "url");
    btnSourcePdf.classList.toggle("is-active", s === "pdf");
    rowUrl.classList.toggle("is-hidden", s !== "url");
    rowPdf.classList.toggle("is-hidden", s !== "pdf");
    clearError(errIngest);
  }
  btnSourceUrl.addEventListener("click", () => setSource("url"));
  btnSourcePdf.addEventListener("click", () => setSource("pdf"));
  
  /* File choose */
  btnChoosePdf.addEventListener("click", () => filePdf.click());
  filePdf.addEventListener("change", () => {
    fileName = filePdf.files && filePdf.files[0] ? filePdf.files[0].name : "";
    pdfName.textContent = fileName || "No file selected";
  });
  
  /* Processing */
  async function processUrl(url) {
    clearError(errIngest);
    setLoading(true, resultSkeleton);
    showEmpty(resultEmpty, resultDoc, btnCopy, btnExport);
  
    try {
      const form = new FormData();
      if (isYouTubeUrl(url)) {
        form.append("type", "youtube");
        form.append("url", url);
      } else {
        form.append("type", "url");
        form.append("url", url);
      }
  
      const resp = await fetch(`${BASE_URL}/api/ingest`, {
        method: "POST",
        body: form,
      });
      const data = await resp.json();
      if (!resp.ok) throw new Error(data.error || JSON.stringify(data));
  
      doc = {
        docId: data.docId || `doc-${Date.now()}`,
        title: new URL(url).hostname + " — Document",
        summary: data.summary || "",
        bullets: data.bullets || [],
        text: data.text || (data.raw_text || ""),
      };
  
      populateDocUI(doc, docIdEl, docTitleEl, docSummaryEl, docBulletsEl);
      setLoading(false, resultSkeleton);
      showDoc(resultEmpty, resultDoc, btnCopy, btnExport);
      enableChatReady();
      addBubble(chatScroll, "assistant", "Document processed. You can now ask questions.");
  
    } catch (err) {
      setLoading(false, resultSkeleton);
      setError(errIngest, err.message || "Could not process the URL. Try again.");
    }
  }
  
  async function processPdf(file) {
    clearError(errIngest);
    setLoading(true, resultSkeleton);
    showEmpty(resultEmpty, resultDoc, btnCopy, btnExport);
  
    try {
      const form = new FormData();
      form.append("type", "pdf");
      form.append("file", file);
  
      const resp = await fetch(`${BASE_URL}/api/ingest`, {
        method: "POST",
        body: form,
      });
      const data = await resp.json();
      if (!resp.ok) throw new Error(data.error || JSON.stringify(data));
  
      doc = {
        docId: data.docId || `pdf-${Date.now()}`,
        title: file.name || "Uploaded PDF",
        summary: data.summary || "",
        bullets: data.bullets || [],
        text: data.text || (data.raw_text || ""),
      };
  
      populateDocUI(doc, docIdEl, docTitleEl, docSummaryEl, docBulletsEl);
      setLoading(false, resultSkeleton);
      showDoc(resultEmpty, resultDoc, btnCopy, btnExport);
      enableChatReady();
      addBubble(chatScroll, "assistant", "PDF processed. Ask me anything about it.");
  
    } catch (err) {
      setLoading(false, resultSkeleton);
      setError(errIngest, err.message || "Could not process the PDF. Try again.");
    }
  }
  
  /* Validate and start */
  function validateAndProcess() {
    clearError(errIngest);
    if (sourceType === "url") {
      const value = (inpUrl.value || "").trim();
      if (!value) return setError(errIngest, "Please paste a link first.");
      try { new URL(value); } catch { return setError(errIngest, "Please paste a valid URL (incl. https://)."); }
      processUrl(value);
    } else {
      if (!filePdf.files || !filePdf.files[0]) return setError(errIngest, "Please choose a PDF file first.");
      processPdf(filePdf.files[0]);
    }
  }
  btnProcessUrl.addEventListener("click", validateAndProcess);
  btnProcessPdf.addEventListener("click", validateAndProcess);
  
  /* Chat */
  inpMessage.addEventListener("input", () => {
    btnSend.disabled = !doc || !(inpMessage.value || "").trim();
  });
  async function sendMessage() {
    if (!doc) return addBubble(chatScroll, "assistant", "Please process a document first.");
    const q = (inpMessage.value || "").trim();
    if (!q) return;
    addBubble(chatScroll, "user", q);
    inpMessage.value = "";
    btnSend.disabled = true;
  
    try {
      const loadingBubble = document.createElement("div");
      loadingBubble.className = "bubble bubble--assistant loading";
      loadingBubble.textContent = "…";
      chatScroll.appendChild(loadingBubble);
      scrollChatToBottom(chatScroll);
  
      const payload = { question: q, text: doc.text || "" };
      const resp = await fetch(`${BASE_URL}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await resp.json();
      loadingBubble.remove();
  
      if (!resp.ok) return addBubble(chatScroll, "assistant", `Error: ${data.error || "Chat failed."}`);
      addBubble(chatScroll, "assistant", data.answer || "No answer.");
    } catch (err) {
      addBubble(chatScroll, "assistant", "Chat error: " + (err.message || "unknown"));
    } finally {
      btnSend.disabled = true;
    }
  }
  btnSend.addEventListener("click", sendMessage);
  inpMessage.addEventListener("keydown", (e) => { if (e.key === "Enter") sendMessage(); });
  
  /* Copy / Export */
  btnCopy.addEventListener("click", async () => {
    if (!doc) return;
    const content = `Title: ${doc.title}\n\nSummary:\n${doc.summary}\n\nBullets:\n- ${doc.bullets.join("\n- ")}`;
    try {
      await navigator.clipboard.writeText(content);
      addBubble(chatScroll, "assistant", "Copied notes to clipboard.");
    } catch {
      addBubble(chatScroll, "assistant", "Could not copy. Use Export instead.");
    }
  });
  btnExport.addEventListener("click", () => {
    if (!doc) return;
    const content = `Title: ${doc.title}\n\nSummary:\n${doc.summary}\n\nBullets:\n- ${doc.bullets.join("\n- ")}\n\nFull text (truncated):\n${(doc.text||"").slice(0,2000)}`;
    const blob = new Blob([content], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "notes.txt";
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  });
  
  /* Init */
  setSource("url");
  showEmpty(resultEmpty, resultDoc, btnCopy, btnExport);
  