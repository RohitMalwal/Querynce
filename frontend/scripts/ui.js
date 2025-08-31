/* -----------------------------
   UI utilities (ui.js)
   ----------------------------- */

/* Loading state */
export function setLoading(v, resultSkeleton) {
    resultSkeleton.classList.toggle("is-hidden", !v);
  }
  
  /* Error handling */
  export function clearError(errEl) {
    errEl.textContent = "";
    errEl.classList.add("is-hidden");
  }
  export function setError(errEl, msg) {
    errEl.textContent = msg;
    errEl.classList.remove("is-hidden");
  }
  
  /* Result states */
  export function showEmpty(resultEmpty, resultDoc, btnCopy, btnExport) {
    resultEmpty.classList.remove("is-hidden");
    resultDoc.classList.add("is-hidden");
    btnCopy.disabled = true;
    btnExport.disabled = true;
  }
  export function showDoc(resultEmpty, resultDoc, btnCopy, btnExport) {
    resultEmpty.classList.add("is-hidden");
    resultDoc.classList.remove("is-hidden");
    btnCopy.disabled = false;
    btnExport.disabled = false;
  }
  
  /* Chat */
  export function scrollChatToBottom(chatScroll) {
    chatScroll.scrollTop = chatScroll.scrollHeight;
  }
  
  export function addBubble(chatScroll, role, text) {
    const wrapper = document.createElement("div");
    wrapper.className =
      "bubble " + (role === "user" ? "bubble--user" : "bubble--assistant");
    wrapper.innerHTML = text.replace(/\n/g, "<br/>");
    chatScroll.appendChild(wrapper);
    scrollChatToBottom(chatScroll);
  }
  
  /* Populate document summary UI */
  export function populateDocUI(doc, docIdEl, docTitleEl, docSummaryEl, docBulletsEl) {
    docIdEl.textContent = doc.docId || "";
    docTitleEl.textContent = doc.title || "";
    docSummaryEl.textContent = doc.summary || "";
    docBulletsEl.innerHTML = "";
    (doc.bullets || []).forEach((b) => {
      const li = document.createElement("li");
      li.textContent = b;
      docBulletsEl.appendChild(li);
    });
  }
  