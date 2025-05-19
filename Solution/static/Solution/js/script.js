
// document.addEventListener('DOMContentLoaded', function () {
//     const fileUpload = document.getElementById('fileUpload');
//     const submitBtn = document.getElementById('submitBtn');
//     const questionInput = document.getElementById('questionInput');
//     const responseDiv = document.getElementById('responseDiv');
//     const responseText = document.getElementById('responseText');
//     const readAloudBtn = document.getElementById('readAloudBtn');
//     const audioPlayer = document.getElementById('audioPlayer');
//     const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    
//     // Function to handle OCR processing
//     fileUpload.addEventListener('change', async (e) => {
//         const file = e.target.files[0];
//         if (!file) return;

//         // Validate file type (image)
//         if (!file.type.startsWith('image/')) {
//             alert('Please upload a valid image file.');
//             return;
//         }

//         // Show loading text
//         responseDiv.style.display = 'block';
//         responseText.textContent = 'Extracting text from image...';

//         // Disable the submit button during OCR
//         submitBtn.disabled = true;

//         try {
//             // Perform OCR using Tesseract.js
//             const result = await Tesseract.recognize(file, 'eng', {
//                 logger: (m) => console.log(m), // Logs OCR progress in the console
//             });

//             // Insert the extracted text into the input field
//             questionInput.value = result.data.text.trim();

//             // Reset the responseDiv
//             responseDiv.style.display = 'none';
//             responseText.textContent = '';

//         } catch (err) {
//             console.error("OCR failed:", err);
//             responseText.textContent = 'Failed to extract text. Please try again.';
//         } finally {
//             // Enable the submit button after OCR
//             submitBtn.disabled = false;
//         }
//     });

//     // Auto-resize the textarea
//     questionInput.addEventListener('input', () => {
//         questionInput.style.height = 'auto';
//         questionInput.style.height = questionInput.scrollHeight + 'px';
//     });

//     // Submit the question
//     submitBtn.addEventListener('click', async () => {
//         const question = questionInput.value.trim();
//         if (question === '') {
//             alert('Please enter a question.');
//             return;
//         }

//         // Show loading text while processing the question
//         responseText.textContent = 'Processing...';
//         responseDiv.style.display = 'block';

//         try {
//             const response = await fetch('/process-question/', {
//                 method: 'POST',
//                 headers: {
//                     'Content-Type': 'application/x-www-form-urlencoded',
//                     'X-CSRFToken': csrfToken,
//                 },
//                 body: new URLSearchParams({ question }),
//             });

//             const data = await response.json();
//             responseText.textContent = data.answer;

//             // Syntax highlight the code if any
//             if (data.answer) {
//                 const answerContainer = document.getElementById('responseTextContainer');
//                 answerContainer.innerHTML = data.answer;
//                 if (typeof hljs !== 'undefined') {
//                     hljs.highlightAll(); // Apply syntax highlighting if hljs is available
//                 }
//             }

//         } catch (error) {
//             responseText.textContent = 'An error occurred while processing your question.';
//             console.error('Error:', error);
//         }
//     });

//     // Read Aloud button logic
//     readAloudBtn.addEventListener('click', async () => {
//         const text = document.getElementById('responseText').textContent.trim();

//         if (!text) {
//             alert("No text available to read aloud.");
//             return;
//         }

//         try {
//             // Show "Generating audio..." text and disable button
//             readAloudBtn.textContent = "🔊 Generating...";
//             readAloudBtn.disabled = true;

//             // Make an AJAX request to generate audio from the response text
//             const response = await fetch('/generate-audio/', {
//                 method: 'POST',
//                 headers: {
//                     'Content-Type': 'application/x-www-form-urlencoded',
//                     'X-CSRFToken': csrfToken,
//                 },
//                 body: new URLSearchParams({ text }),
//             });

//             const data = await response.json();

//             if (response.ok && data.audio_url) {
//                 // Play the generated audio
//                 audioPlayer.src = data.audio_url;
//                 audioPlayer.style.display = 'block';
//                 audioPlayer.play();
//             } else {
//                 alert(`Error: ${data.error || 'An unknown error occurred.'}`);
//             }
//         } catch (err) {
//             console.error("Error generating audio:", err);
//             alert("An error occurred while trying to read aloud the text.");
//         } finally {
//             // Reset the button after processing
//             readAloudBtn.textContent = "🔊 Get Audio";
//             readAloudBtn.disabled = false;
//         }
//     });
// });



























































/* script.js */

let currentChatId = null;

const form = document.getElementById('askQuestionForm');
const responseDiv = document.getElementById('responseDiv');
const fileUpload = document.getElementById('fileUpload');
const questionInput = document.getElementById('questionInput');
const audioPlayer = document.getElementById('audioPlayer');
const readAloudBtn = document.getElementById('readAloudBtn');
const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
const themeToggleBtn = document.getElementById('themeToggleBtn');

// ============ THEME ============
function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem('theme', theme);
  themeToggleBtn.innerHTML = theme === 'dark'
    ? '<i class="fas fa-sun"></i> Light Theme'
    : '<i class="fas fa-moon"></i> Dark Theme';
}

document.addEventListener('DOMContentLoaded', () => {
  // ✅ Detect current chat ID from URL (e.g. ?chat_id=123)
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.has('chat_id')) {
    currentChatId = urlParams.get('chat_id');
  }

  // Initialize theme
  const saved = localStorage.getItem('theme') || 'light';
  applyTheme(saved);

  // Logout modal
  const logoutBtn = document.getElementById('logoutBtn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', () => {
      const modal = new bootstrap.Modal(document.getElementById('logoutModal'));
      modal.show();
    });
  }

  // Sidebar toggle
  const toggleSidebar = document.querySelector('.toggle-sidebar');
  const sidebar = document.querySelector('.sidebar');
  if (toggleSidebar && sidebar) {
    toggleSidebar.addEventListener('click', () => sidebar.classList.toggle('active'));
  }

  // Theme toggle
  if (themeToggleBtn) {
    themeToggleBtn.addEventListener('click', () => {
      const current = document.documentElement.getAttribute('data-theme');
      applyTheme(current === 'light' ? 'dark' : 'light');
    });
  }

  // Safely render markdown if present
  const responseText = document.getElementById('responseText');
  if (responseText) {
    const escaped = responseText.getAttribute('data-markdown');
    if (escaped) {
      const raw = JSON.parse(`"${escaped}"`);
      responseText.innerHTML = marked.parse(raw);
      responseDiv.style.display = 'block';
    }
  }

  // Enter key submits
  if (questionInput && form) {
    questionInput.addEventListener('keydown', e => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        if (form.requestSubmit) form.requestSubmit();
        else form.dispatchEvent(new Event('submit'));
      }
    });
  }
});

// ============ OCR ============
if (fileUpload) {
  fileUpload.addEventListener('change', async e => {
    const file = e.target.files[0];
    if (!file) return;
    responseDiv.style.display = 'block';
    const responseText = document.getElementById('responseText');
    responseText.textContent = 'Extracting text from image...';
    try {
      const result = await Tesseract.recognize(file, 'eng', { logger: m => console.log(m) });
      questionInput.value = result.data.text.trim();
      responseDiv.style.display = 'none';
      responseText.textContent = '';
    } catch {
      responseText.textContent = 'Failed to extract text.';
    }
  });
}

// ============ FORM SUBMIT ============
if (form) {
  form.addEventListener('submit', e => {
    e.preventDefault();
    const q = questionInput.value.trim();
    if (!q) return;
    responseDiv.style.display = 'block';
    const responseText = document.getElementById('responseText');
    responseText.textContent = 'Loading...';
    fetch('/questions/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-CSRFToken': csrfToken
      },
      body: new URLSearchParams({
        question: q,
        chat_id: currentChatId || ''
      })
    })
      .then(r => r.json())
      .then(data => {
        if (data.success) {
          responseText.innerHTML = marked.parse(data.output);
          readAloudBtn.style.opacity = 1;
        } else {
          responseText.textContent = `Error: ${data.error || 'Unknown.'}`;
        }
      })
      .catch(() => responseText.textContent = 'Oops, something went wrong.');
    questionInput.value = '';
  });
}

// ============ READ ALOUD ============
if (readAloudBtn) {
  readAloudBtn.addEventListener('click', async () => {
    const text = document.getElementById('responseText').textContent.trim();
    if (!text) return alert('No text to read.');
    try {
      const res = await fetch('/generate-audio/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'X-CSRFToken': csrfToken },
        body: new URLSearchParams({ text })
      });
      const d = await res.json();
      if (res.ok && d.audio_url) {
        audioPlayer.src = d.audio_url;
        audioPlayer.style.display = 'block';
        audioPlayer.play();
      } else alert(`Error: ${d.error || 'Audio failed.'}`);
    } catch {
      alert('Audio generation failed.');
    }
  });
}

// ============ COPY ============
window.copyToClipboard = () => {
  const txt = document.getElementById('responseText').innerText;
  const btn = document.getElementById('copyButton');
  navigator.clipboard.writeText(txt)
    .then(() => {
      btn.innerHTML = '<i class="fas fa-check"></i> Copied!';
      setTimeout(() => btn.innerHTML = '<i class="fas fa-copy"></i> Copy', 2000);
    })
    .catch(() => alert('Copy failed.'));
};
