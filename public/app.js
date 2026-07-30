const form = document.getElementById("update-form");
const generateBtn = document.getElementById("generate-btn");
const copyBtn = document.getElementById("copy-btn");
const output = document.getElementById("output");
const errorEl = document.getElementById("error");

function setError(message) {
  if (!message) {
    errorEl.hidden = true;
    errorEl.textContent = "";
    return;
  }
  errorEl.hidden = false;
  errorEl.textContent = message;
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  setError("");

  const payload = {
    apiKey: form.apiKey.value,
    accountName: form.accountName.value,
    recentActivity: form.recentActivity.value,
    followUp: form.followUp.value,
    riskStatus: form.riskStatus.value,
    riskNotes: form.riskNotes.value,
    renewalDate: form.renewalDate.value,
    tone: form.tone.value,
    style: form.style.value,
  };

  generateBtn.disabled = true;
  generateBtn.textContent = "Generating...";
  copyBtn.disabled = true;

  try {
    const res = await fetch("/api/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();

    if (!res.ok) {
      setError(data.error || "Something went wrong.");
      return;
    }

    output.value = data.update;
    copyBtn.disabled = false;
  } catch (err) {
    setError("Could not reach the server. Is it running?");
  } finally {
    generateBtn.disabled = false;
    generateBtn.textContent = "Generate update";
  }
});

copyBtn.addEventListener("click", async () => {
  const original = copyBtn.textContent;
  let copied = false;

  try {
    await navigator.clipboard.writeText(output.value);
    copied = true;
  } catch (err) {
    output.select();
    copied = document.execCommand("copy");
    output.setSelectionRange(0, 0);
  }

  copyBtn.textContent = copied ? "Copied!" : "Couldn't copy — select & Cmd/Ctrl+C";
  setTimeout(() => (copyBtn.textContent = original), copied ? 1200 : 2500);
});
