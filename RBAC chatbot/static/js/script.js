function uploadPDF() {
    const file = document.getElementById("pdfFile").files[0];
    if (!file) {
        alert("Please select a file.");
        return;
    }

    const formData = new FormData();
    formData.append("pdfFile", file);

    fetch("/upload", {
        method: "POST",
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById("uploadStatus").textContent = data.message;
    });
}

function askQuestion() {
  const question = document.getElementById("questionInput").value;
  const answerBox = document.getElementById("answerText");

  if (!question) {
    answerBox.innerHTML = "<p style='color: red;'>⚠️ Please enter a question.</p>";
    return;
  }

  answerBox.innerHTML = "<p class='loading'>Thinking... Please wait</p>";

  fetch("/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question })
  })
    .then(res => res.json())
    .then(data => {
      let answer = data.answer || "No response.";

      // ✅ Convert markdown-like syntax to HTML
      answer = answer
        .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>") // bold
        .replace(/\*(.*?)\*/g, "<li>$1</li>");            // bullet points

      // ✅ Wrap bullets inside <ul>
      if (answer.includes("<li>")) {
        answer = "<ul>" + answer + "</ul>";
      }

      // ✅ Display inside styled box
      answerBox.innerHTML = `<div class="answer-card">${answer}</div>`;
    })
    .catch(err => {
      console.error("Error:", err);
      answerBox.innerHTML = "<p style='color: red;'>❌ Error fetching answer.</p>";
    });
}

