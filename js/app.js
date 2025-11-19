// js/app.js

const TEXTS_BASE_PATH = "content/texts/";
const VOCAB_URL = "content/vocab/vocab_master.json";

let vocab = {}; // { key(lowercase): { word, translation, emoji, audio } }

document.addEventListener("DOMContentLoaded", () => {
  const textContainer = document.getElementById("textContainer");
  const menuItems = document.querySelectorAll(".menu-item[data-file]");

  const popup = document.getElementById("wordPopup");
  const popupEmoji = document.getElementById("popupEmoji");
  const popupWord = document.getElementById("popupWord");
  const popupTrans = document.getElementById("popupTrans");
  const popupClose = document.getElementById("popupClose");
  const audioPlayer = document.getElementById("audioPlayer");

  // --- Load vocab once ---
  fetch(VOCAB_URL)
    .then((res) => res.json())
    .then((data) => {
      vocab = data || {};
      console.log("Vocab loaded, words:", Object.keys(vocab).length);
    })
    .catch((err) => console.error("Failed to load vocab:", err));

  // --- Helper: load text partial ---
  function loadText(file) {
    fetch(TEXTS_BASE_PATH + file)
      .then((res) => res.text())
      .then((html) => {
        textContainer.innerHTML = html;
        decorateAllWords(textContainer);
      })
      .catch((err) => {
        console.error("Failed to load text:", err);
        textContainer.innerHTML =
          "<p style='color:#fca5a5;font-size:0.85rem'>Error loading text.</p>";
      });
  }

  // --- Decorate all words inside [data-decorate="words"] elements ---
  function decorateAllWords(root) {
    const targets = root.querySelectorAll("[data-decorate='words']");
    targets.forEach((el) => decorateElementWords(el));
  }

  function decorateElementWords(element) {
    const walker = document.createTreeWalker(
      element,
      NodeFilter.SHOW_TEXT,
      {
        acceptNode(node) {
          if (!node.nodeValue.trim()) return NodeFilter.FILTER_REJECT;
          return NodeFilter.FILTER_ACCEPT;
        },
      }
    );

    const textNodes = [];
    let current;
    while ((current = walker.nextNode())) {
      textNodes.push(current);
    }

    const wordRegex = /([A-Za-z]+(?:'[A-Za-z]+)?)/g;

    textNodes.forEach((node) => {
      const text = node.nodeValue;
      const frag = document.createDocumentFragment();

      let lastIndex = 0;
      let match;
      while ((match = wordRegex.exec(text)) !== null) {
        const word = match[1];

        // text before the word
        if (match.index > lastIndex) {
          frag.appendChild(
            document.createTextNode(text.slice(lastIndex, match.index))
          );
        }

        // the word itself
        const span = document.createElement("span");
        span.className = "word";
        span.dataset.word = word.toLowerCase();
        span.textContent = word;
        frag.appendChild(span);

        lastIndex = wordRegex.lastIndex;
      }

      // remaining text after last word
      if (lastIndex < text.length) {
        frag.appendChild(document.createTextNode(text.slice(lastIndex)));
      }

      node.parentNode.replaceChild(frag, node);
    });
  }

  // --- Popup logic ---
  function showPopup(entry) {
    popupEmoji.textContent = entry.emoji || "✨";
    popupWord.textContent = entry.word || "";
    popupTrans.textContent = entry.translation || "";

    const audioPath = entry.audio;
    if (audioPath) {
      audioPlayer.src = audioPath;
      audioPlayer
        .play()
        .catch((e) => console.log("Audio play blocked:", e));
    }

    popup.classList.add("show");
  }

  function showPopupFallback(wordText) {
    popupEmoji.textContent = "❓";
    popupWord.textContent = wordText;
    popupTrans.textContent = "нет перевода (добавь в словарь)";
    popup.classList.add("show");
  }

  popupClose.addEventListener("click", () => {
    popup.classList.remove("show");
  });

  document.addEventListener("click", (e) => {
    if (!popup.contains(e.target) && !e.target.classList.contains("word")) {
      popup.classList.remove("show");
    }
  });

  // --- Event delegation: click on any word ---
  textContainer.addEventListener("click", (e) => {
    const target = e.target.closest(".word");
    if (!target) return;

    const key =
      (target.dataset.word || target.textContent || "").trim().toLowerCase();

    if (!key) return;

    const entry = vocab[key];
    if (entry) {
      showPopup(entry);
    } else {
      showPopupFallback(target.textContent.trim());
    }
  });

  // --- Menu switching ---
  menuItems.forEach((item) => {
    item.addEventListener("click", () => {
      const file = item.getAttribute("data-file");
      if (!file) return;

      menuItems.forEach((mi) => mi.classList.remove("active"));
      item.classList.add("active");

      loadText(file);
    });
  });

  // Initial load
  loadText("text1.html");
});
