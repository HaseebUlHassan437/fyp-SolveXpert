// Combined and cleaned version of all RAG page scripts

let documentId = null;
let isMuted = false;
let currentAudio = null;

const uploadForm = document.getElementById('uploadForm');
const documentUpload = document.getElementById('documentUpload');
const askQuestionForm = document.getElementById('askQuestionForm');
const questionInput = document.getElementById('questionInput');
const responseDiv = document.getElementById('responseDiv');
const muteBtn = document.getElementById('muteBtn');
const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
const voiceBtn = document.getElementById('voiceBtn');

document.getElementById('themeToggleBtn').addEventListener('click', () => {
      const current = document.documentElement.getAttribute('data-theme') || 'light';
      document.documentElement.setAttribute('data-theme', current === 'light' ? 'dark' : 'light');
    });
// Voice Recognition
if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  const recognition = new SpeechRecognition();
  recognition.lang = 'en-US';
  recognition.interimResults = false;
  recognition.continuous = false;

  voiceBtn.addEventListener('click', () => {
    questionInput.value = "Listening...";
    recognition.start();
  });

  recognition.onresult = (event) => {
    questionInput.value = event.results[0][0].transcript;
    questionInput.dispatchEvent(new Event('input'));
  };

  recognition.onend = () => {
    if (questionInput.value === "Listening...") questionInput.value = "";
  };

  recognition.onerror = (event) => {
    console.error("Speech recognition error:", event.error);
    questionInput.value = "";
    alert("Microphone access failed: " + event.error);
  };
} else {
  voiceBtn.disabled = true;
  alert("Speech recognition is not supported in this browser.");
}

// Auto-resize input field
questionInput.addEventListener('input', () => {
  questionInput.style.height = 'auto';
  questionInput.style.height = Math.min(questionInput.scrollHeight, 120) + 'px';
});

// Upload Document
uploadForm.addEventListener('change', async (e) => {
  e.preventDefault();
  const file = documentUpload.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append('document', file);
  formData.append('csrfmiddlewaretoken', csrfToken);

  try {
    const res = await fetch('/upload_document/', {
      method: 'POST',
      body: formData
    });
    const data = await res.json();

    if (data.success) {
      documentId = data.document_id;
      alert("✅ Document uploaded successfully. Now you can ask questions!");
      await loadDocuments();
      selectDocument(documentId);
    } else {
      alert("❌ Upload failed: " + data.error);
    }
  } catch (err) {
    console.error("Upload Error:", err);
    alert("❌ Upload failed.");
  }
});

// Typing animation
function typeText(element, text, speed = 15, onComplete = () => {}) {
  let index = 0;
  const interval = setInterval(() => {
    if (index < text.length) {
      element.textContent += text.charAt(index++);
      responseDiv.scrollTop = responseDiv.scrollHeight;
    } else {
      clearInterval(interval);
      onComplete();
    }
  }, speed);
}

// Submit question with Enter
questionInput.addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    askQuestionForm.requestSubmit();
    setTimeout(() => { questionInput.value = ''; }, 50);
  }
});

// Ask Question
askQuestionForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  if (!documentId) return alert("Please upload a document first.");

  const question = questionInput.value.trim();
  if (!question) return;

  const userChatBox = document.createElement('div');
  userChatBox.className = 'user-chat-box';
  userChatBox.innerHTML = `<div class="user-chat-area">${question}</div>`;
  responseDiv.appendChild(userChatBox);

  const loadingBox = document.createElement('div');
  loadingBox.className = 'ai-chat-box';
  loadingBox.innerHTML = `
    <div class="ai-chat-area markdown position-relative" id="loading-area">
      <em>Loading...</em>
    </div>`;
  responseDiv.appendChild(loadingBox);
  responseDiv.scrollTop = responseDiv.scrollHeight;

  const formData = new FormData();
  formData.append('question', question);
  formData.append('document_id', documentId);
  formData.append('csrfmiddlewaretoken', csrfToken);

  try {
    const res = await fetch('/ask_question_document/', {
      method: 'POST',
      body: formData
    });

    if (!res.ok) return console.error("Server Error:", await res.text());

    const data = await res.json();
    const textResponse = data.answer || "No answer found.";
    const audioBlob = new Blob([Uint8Array.from(atob(data.audio_base64), c => c.charCodeAt(0))], { type: 'audio/mpeg' });
    const audioUrl = URL.createObjectURL(audioBlob);

    const aiResponseBox = document.createElement('div');
    aiResponseBox.className = 'ai-chat-box';
    aiResponseBox.style.display = 'flex';
    aiResponseBox.style.alignItems = 'flex-start';
    aiResponseBox.style.margin = '10px 0';

    const aiChatArea = document.createElement('div');
    aiChatArea.className = 'ai-chat-area markdown position-relative';
    aiChatArea.innerHTML = `
      <button class="copy-btn position-absolute top-0 end-0 m-2 btn btn-sm btn-outline-danger" onclick="copyAnswer(this)">
        <i class="fas fa-copy"></i>
      </button>
      <span id="animated-text"></span>`;

    const animatedText = aiChatArea.querySelector('#animated-text');
    typeText(animatedText, textResponse, 15, () => {
      animatedText.innerHTML = marked.parse(textResponse);
      if (window.MathJax) MathJax.typesetPromise();
    });

    // aiChatArea.style.background = '#36454F';
    // aiChatArea.style.maxWidth = '80%';
    loadingBox.remove();
    aiResponseBox.appendChild(aiChatArea);
    responseDiv.appendChild(aiResponseBox);
    responseDiv.scrollTop = responseDiv.scrollHeight;

    if (currentAudio) currentAudio.pause();
    currentAudio = new Audio(audioUrl);
    currentAudio.volume = isMuted ? 0 : 1;
    avatarSpeaking(true);
    currentAudio.play();
    currentAudio.onended = () => {
      avatarSpeaking(false);
      currentAudio = null;
    };
  } catch (err) {
    console.error("Fetch Error:", err);
  }

  questionInput.value = '';
});

// Load Documents
async function loadDocuments() {
  try {
    const res = await fetch('/load_documents/');
    const data = await res.json();

    if (data.success) {
      const documentList = document.getElementById('documentList');
      documentList.innerHTML = '';

      data.documents.forEach(doc => {
        const container = document.createElement('div');
        container.className = 'd-flex justify-content-between align-items-center';

        const docLink = document.createElement('button');
        docLink.className = 'btn btn-outline-primary w-100 mb-2 text-start';
        docLink.textContent = doc.title.length > 25 ? doc.title.slice(0, 20) + '...' : doc.title;
        docLink.onclick = () => selectDocument(doc.id);

        const deleteBtn = document.createElement('a');
        deleteBtn.href = `/delete_document/${doc.id}/`;
        deleteBtn.className = 'text-danger ms-2';
        deleteBtn.innerHTML = '<i class="fas fa-trash"></i>';
        deleteBtn.onclick = () => confirm("Are you sure you want to delete this document and its chat?");

        container.appendChild(docLink);
        container.appendChild(deleteBtn);
        documentList.appendChild(container);
      });
    } else {
      console.error("Failed to load documents:", data.error);
    }
  } catch (error) {
    console.error("Error loading documents:", error);
  }
}

// Load Chat
async function selectDocument(docId) {
  documentId = docId;
  responseDiv.innerHTML = '';

  try {
    const res = await fetch(`/load_document_chat/${docId}/`);
    const data = await res.json();

    if (data.success) {
      data.chat.forEach(item => {
        const userBox = document.createElement('div');
        userBox.className = 'user-chat-box';
        userBox.innerHTML = `<div class="user-chat-area">${item.question}</div>`;
        responseDiv.appendChild(userBox);

        const aiBox = document.createElement('div');
        aiBox.className = 'ai-chat-box';
        aiBox.innerHTML = `<div class="ai-chat-area markdown" data-raw="${item.answer.replace(/"/g, '&quot;')}"></div>`;
        responseDiv.appendChild(aiBox);

        const markdownDiv = aiBox.querySelector('.markdown');
        if (markdownDiv) {
          markdownDiv.innerHTML = marked.parse(markdownDiv.dataset.raw);
          if (window.MathJax) MathJax.typesetPromise();
        }
      });
      responseDiv.scrollTop = responseDiv.scrollHeight;
    } else {
      console.error("Failed to load chat:", data.error);
    }
  } catch (error) {
    console.error("Error loading chat:", error);
  }
}

// Mute Button
muteBtn.addEventListener('click', () => {
  isMuted = !isMuted;
  muteBtn.textContent = isMuted ? "🔇" : "🔊";
  if (currentAudio) currentAudio.volume = isMuted ? 0 : 1;
});

// Avatar animation
function avatarSpeaking(speaking) {
  const avatar = document.getElementById('avatarImage');
  avatar.style.transform = speaking ? "scale(1.2)" : "scale(1)";
  avatar.style.transition = "transform 0.3s ease";
}

// Copy to clipboard
window.copyAnswer = (btn) => {
  const answerDiv = btn.parentElement;
  const textToCopy = answerDiv.innerText.trim();
  navigator.clipboard.writeText(textToCopy).then(() => {
    btn.innerHTML = '<i class="fas fa-check"></i>';
    setTimeout(() => {
      btn.innerHTML = '<i class="fas fa-copy"></i>';
    }, 1500);
  }).catch(() => alert("Failed to copy. Try again."));
};

// Sidebar toggle
document.getElementById('sidebarToggle').addEventListener('click', () => {
  document.getElementById('sidebar').classList.toggle('collapsed');
  document.getElementById('chatContent').classList.toggle('sidebar-collapsed');
});

// Initial Load
document.addEventListener('DOMContentLoaded', async () => {
  await loadDocuments();
});