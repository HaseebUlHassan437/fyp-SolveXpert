// ==== Logout ====
window.logoutUrl = "{% url 'logout' %}";
document.getElementById('confirmLogout')?.addEventListener('click', () => {
  window.location.href = window.logoutUrl;
});

// ==== Image Upload Button ====
document.getElementById("image-button")?.addEventListener("click", () => {
  document.getElementById("fileUpload")?.click();
});

// ==== Auto-growing Textarea ====
const textarea = document.getElementById('questionInput');
textarea?.addEventListener('input', () => {
  textarea.style.height = 'auto';
  textarea.style.height = Math.min(textarea.scrollHeight, 96) + 'px';
});

// ==== Markdown Parsing on Load ====
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".markdown").forEach(el => {
    el.innerHTML = marked.parse(el.textContent.trim());
  });
});

// ==== Ask LLaMA (for math problem) ====
function askLlama() {
  const question = document.getElementById('questionInput').value.trim();
  if (!question) {
    alert("Please enter a math problem.");
    return;
  }

  fetch("{% url 'llama3_inference' %}", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
      "X-CSRFToken": "{{ csrf_token }}",
    },
    body: new URLSearchParams({ question: question })
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      const responseDiv = document.getElementById("responseDiv");
      const aiBox = document.createElement("div");
      aiBox.className = "ai-chat-box";

      const aiArea = document.createElement("div");
      aiArea.className = "ai-chat-area markdown";
      aiBox.appendChild(aiArea);
      responseDiv.appendChild(aiBox);

      const htmlChunks = marked.parse(data.output.trim()).split(/(?=<)/g);
      let i = 0;
      function typeHTML() {
        if (i < htmlChunks.length) {
          aiArea.innerHTML += htmlChunks[i];
          i++;
          setTimeout(typeHTML, 20);
        } else {
          if (window.MathJax) MathJax.typesetPromise();
        }
      }
      typeHTML();
    } else {
      alert("Error: " + data.error);
    }
  })
  .catch(err => {
    alert("Request failed: " + err);
  });
}

// ==== Sidebar Toggle ====
document.getElementById('sidebarToggle')?.addEventListener('click', () => {
  const sidebar = document.getElementById('sidebar');
  const chatContent = document.getElementById('chatContent');
  sidebar.classList.toggle('collapsed');
  chatContent.classList.toggle('sidebar-collapsed');
  sidebar.classList.toggle('hidden');
  chatContent.classList.toggle('sidebar-visible');
});

// ==== Theme Toggle ====
const themeToggleBtn = document.getElementById('themeToggleBtn');
function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem('theme', theme);
  if (themeToggleBtn) {
    themeToggleBtn.innerHTML = theme === 'dark'
      ? '<i class="fas fa-sun"></i> Light Theme'
      : '<i class="fas fa-moon"></i> Dark Theme';
  }
}

// ==== Scroll to Bottom ====
function scrollToBottom() {
  const responseDiv = document.getElementById('responseDiv');
  responseDiv.scrollTop = responseDiv.scrollHeight;
}

// ==== DOMContentLoaded Setup ====
document.addEventListener('DOMContentLoaded', () => {
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.has('chat_id')) currentChatId = urlParams.get('chat_id');

  applyTheme(localStorage.getItem('theme') || 'light');

  themeToggleBtn?.addEventListener('click', () => {
    const current = document.documentElement.getAttribute('data-theme');
    applyTheme(current === 'light' ? 'dark' : 'light');
  });

  textarea?.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      form.requestSubmit();
    }
  });

  document.querySelectorAll('.markdown[data-raw]').forEach(el => {
    const raw = el.getAttribute('data-raw');
    el.innerHTML += marked.parse(raw);
  });

  if (window.MathJax) MathJax.typesetPromise();
  scrollToBottom();

  document.querySelectorAll('.delete-chat').forEach(btn => {
    btn.addEventListener('click', async e => {
      e.preventDefault();
      if (!confirm('Are you sure you want to delete this chat?')) return;
      try {
        const response = await fetch(btn.href, { method: 'GET' });
        if (response.ok) btn.closest('.chat-history-item').remove();
        else alert('Failed to delete chat.');
      } catch (err) {
        console.error('Delete failed', err);
      }
    });
  });
});

// ==== Image Preview ====
const fileUpload = document.getElementById("fileUpload");
const previewImage = document.getElementById("previewImage");

fileUpload?.addEventListener("change", e => {
  const file = e.target.files[0];
  if (!file || !file.type.startsWith('image/')) {
    alert("Please upload a valid image file.");
    previewImage.src = "{% static 'Solution/img.svg' %}";
    previewImage.classList.remove('uploaded');
    return;
  }

  previewImage.src = URL.createObjectURL(file);
  previewImage.classList.add('uploaded');
});

// ==== Chat Submit Handler ====
let currentChatId = null;
const form = document.getElementById('askQuestionForm');
const questionInput = document.getElementById('questionInput');
const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
const responseDiv = document.getElementById('responseDiv');

form?.addEventListener('submit', e => {
  e.preventDefault();

  const question = questionInput.value.trim();
  if (!question) return;

  const formData = new FormData();
  formData.append('question', question);
  formData.append('chat_id', currentChatId || '');
  if (fileUpload.files.length > 0) {
    formData.append('image', fileUpload.files[0]);
  }

  const userChatBox = document.createElement('div');
  userChatBox.className = 'user-chat-box';
  userChatBox.innerHTML = `
    <div class="user-chat-area">
      <span class="role-label"></span> ${question}
    </div>
  `;
  responseDiv.appendChild(userChatBox);

  fetch('/questions/', {
    method: 'POST',
    body: formData,
    headers: {
      'X-CSRFToken': csrfToken
    }
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      if (!currentChatId && data.chat_id) currentChatId = data.chat_id;

      const aiChatBox = document.createElement('div');
      aiChatBox.className = 'ai-chat-box';
      aiChatBox.style.margin = '10px 0';

      const aiChatArea = document.createElement('div');
      aiChatArea.className = 'ai-chat-area markdown position-relative';
      aiChatArea.innerHTML = `
        <span class="role-label"></span>
        <button class="copy-btn position-absolute top-0 end-0 m-2 btn btn-sm btn-outline-danger" onclick="copyAnswer(this)">
          <i class="fas fa-copy"></i>
        </button>
        <span id="animated-response"></span>
      `;

      const animatedSpan = aiChatArea.querySelector('#animated-response');
      const rawText = data.output || "No response.";

      function typeMarkdown(element, markdownText, speed = 15) {
        let index = 0;
        const interval = setInterval(() => {
          if (index <= markdownText.length) {
            element.innerHTML = marked.parse(markdownText.slice(0, index));
            scrollToBottom();
            index++;
          } else {
            clearInterval(interval);
            if (window.MathJax) MathJax.typesetPromise();
          }
        }, speed);
      }

      typeMarkdown(animatedSpan, rawText);
      aiChatArea.style.background = '#36454F';
      aiChatArea.style.maxWidth = '80%';

      aiChatBox.appendChild(aiChatArea);
      responseDiv.appendChild(aiChatBox);

      scrollToBottom();
    } else {
      alert("❌ Error: " + data.error);
    }
  })
  .catch(err => console.error("❌ Fetch error:", err));

  questionInput.value = '';
  previewImage.src = "/static/Solution/img.svg";
  previewImage.classList.remove('uploaded');
});

// ==== Copy Answer Function ====
window.copyAnswer = (btn) => {
  const answerDiv = btn.parentElement;
  const textToCopy = answerDiv.innerText.trim();
  navigator.clipboard.writeText(textToCopy).then(() => {
    btn.innerHTML = '<i class="fas fa-check"></i>';
    setTimeout(() => {
      btn.innerHTML = '<i class="fas fa-copy"></i>';
    }, 1500);
  }).catch(err => {
    alert("Failed to copy. Try again.");
  });
};
