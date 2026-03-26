const state = {
  me: null,
  photos: [],
  quotes: [],
  cycles: [],
  summary: null,
  collection: [],
  builderNodes: [],
  selectedCycle: null,
  runSetup: [],
  run: null,
  timerInterval: null,
  dragIndex: null,
  clickBurst: [],
  clickBurstResetTimer: null,
  audioContext: null,
};

const elements = {};

document.addEventListener("DOMContentLoaded", () => {
  cacheElements();
  bindEvents();
  bootstrap();
});

function cacheElements() {
  elements.authPanel = document.getElementById("auth-panel");
  elements.summaryPanel = document.getElementById("summary-panel");
  elements.cyclesPanel = document.getElementById("cycles-panel");
  elements.builderPanel = document.getElementById("builder-panel");
  elements.runSetupPanel = document.getElementById("run-setup-panel");
  elements.timerPanel = document.getElementById("timer-panel");
  elements.collectionPanel = document.getElementById("collection-panel");
  elements.demoLoginBtn = document.getElementById("demo-login-btn");
  elements.logoutBtn = document.getElementById("logout-btn");
  elements.focusCount = document.getElementById("focus-count");
  elements.todoCount = document.getElementById("todo-count");
  elements.nottodoCount = document.getElementById("nottodo-count");
  elements.calendarGrid = document.getElementById("calendar-grid");
  elements.cyclesList = document.getElementById("cycles-list");
  elements.builderCanvas = document.getElementById("builder-canvas");
  elements.addFocusBtn = document.getElementById("add-focus-btn");
  elements.removeFocusBtn = document.getElementById("remove-focus-btn");
  elements.saveCycleBtn = document.getElementById("save-cycle-btn");
  elements.cycleName = document.getElementById("cycle-name");
  elements.runSetupTitle = document.getElementById("run-setup-title");
  elements.runSetupList = document.getElementById("run-setup-list");
  elements.startRunBtn = document.getElementById("start-run-btn");
  elements.timerHero = document.getElementById("timer-hero");
  elements.timerMode = document.getElementById("timer-mode");
  elements.timerClock = document.getElementById("timer-clock");
  elements.timerQuote = document.getElementById("timer-quote");
  elements.timerAuthor = document.getElementById("timer-author");
  elements.timerSource = document.getElementById("timer-source");
  elements.timerProgress = document.getElementById("timer-progress");
  elements.taskPanel = document.getElementById("task-panel");
  elements.collectionList = document.getElementById("collection-list");
  elements.modalBackdrop = document.getElementById("modal-backdrop");
  elements.modalBox = document.getElementById("modal-box");
  elements.userBar = document.getElementById("user-bar");
  elements.clickDots = Array.from(document.querySelectorAll("[data-click-dot]"));
}

function bindEvents() {
  elements.demoLoginBtn.addEventListener("click", loginDemo);
  elements.logoutBtn.addEventListener("click", logout);
  elements.addFocusBtn.addEventListener("click", addBuilderNode);
  elements.removeFocusBtn.addEventListener("click", removeBuilderNode);
  elements.saveCycleBtn.addEventListener("click", saveCustomCycle);
  elements.startRunBtn.addEventListener("click", startPreparedRun);
  window.addEventListener("click", handleTripleClick);
}

async function bootstrap() {
  const meResponse = await fetch("/me");
  if (!meResponse.ok) {
    renderLoggedOut();
    return;
  }
  state.me = await meResponse.json();
  await refreshData();
  renderLoggedIn();
}

async function loginDemo() {
  await fetch("/auth/demo-login", { method: "POST" });
  await bootstrap();
}

async function logout() {
  await fetch("/auth/logout", { method: "POST" });
  stopLocalRun(true);
  renderLoggedOut();
}

async function refreshData() {
  const [photos, quotes, cycles, summary, collection] = await Promise.all([
    fetchJSON("/assets/photos"),
    fetchJSON("/assets/quotes"),
    fetchJSON("/cycles"),
    fetchJSON("/dashboard/summary"),
    fetchJSON("/collection"),
  ]);
  state.photos = photos.items;
  state.quotes = quotes.items;
  state.cycles = cycles.items;
  state.summary = summary;
  state.collection = collection.items;
  ensureBuilderNodes();
}

function renderLoggedOut() {
  state.me = null;
  elements.authPanel.classList.remove("hidden");
  elements.summaryPanel.classList.add("hidden");
  elements.cyclesPanel.classList.add("hidden");
  elements.builderPanel.classList.add("hidden");
  elements.runSetupPanel.classList.add("hidden");
  elements.timerPanel.classList.add("hidden");
  elements.collectionPanel.classList.add("hidden");
  elements.logoutBtn.classList.add("hidden");
  elements.userBar.querySelectorAll(".user-pill").forEach((node) => node.remove());
}

function renderLoggedIn() {
  elements.authPanel.classList.add("hidden");
  elements.summaryPanel.classList.remove("hidden");
  elements.cyclesPanel.classList.remove("hidden");
  elements.builderPanel.classList.remove("hidden");
  elements.timerPanel.classList.remove("hidden");
  elements.collectionPanel.classList.remove("hidden");
  elements.logoutBtn.classList.remove("hidden");
  updateUserBar();
  renderSummary();
  renderCycles();
  renderBuilder();
  renderCollection();
  renderTimerIdle();
  renderClickDots(0);
}

function updateUserBar() {
  elements.userBar.querySelectorAll(".user-pill").forEach((node) => node.remove());
  const pill = document.createElement("div");
  pill.className = "user-pill";
  pill.textContent = state.me.nickname;
  elements.userBar.prepend(pill);
}

function renderSummary() {
  elements.focusCount.textContent = state.summary.focusCount;
  elements.todoCount.textContent = state.summary.todoCount;
  elements.nottodoCount.textContent = state.summary.nottodoCount;
  if (!state.summary.focusCalendar.length) {
    elements.calendarGrid.innerHTML = "<p>No focus history yet.</p>";
    return;
  }
  elements.calendarGrid.innerHTML = state.summary.focusCalendar.map((entry) => `
    <article class="calendar-cell">
      <strong>${entry.count}</strong>
      <div>${entry.date}</div>
    </article>
  `).join("");
}

function renderCycles() {
  elements.cyclesList.innerHTML = state.cycles.map((cycle) => `
    <article class="cycle-card">
      <div class="panel-header">
        <div>
          <h3>${escapeHTML(cycle.name)}</h3>
          <p class="cycle-meta">${cycle.owned ? "Owned cycle" : "Trial preset"} · ${cycle.focusNodes.length} focus nodes</p>
        </div>
        <div class="cycle-actions">
          <button data-action="prepare-cycle" data-id="${cycle.id}" type="button">Prepare Run</button>
        </div>
      </div>
      <div class="focus-strip">
        ${cycle.focusNodes.map((node) => `
          <div class="focus-mini">
            <strong>Focus ${node.nodeOrder}</strong>
            <div>${node.focusDurationSeconds}s</div>
            <div>${escapeHTML(node.quote.authorName)}</div>
          </div>
        `).join("")}
      </div>
    </article>
  `).join("");
  elements.cyclesList.querySelectorAll("[data-action='prepare-cycle']").forEach((button) => {
    button.addEventListener("click", () => prepareRun(Number(button.dataset.id)));
  });
}

function ensureBuilderNodes() {
  if (state.builderNodes.length || !state.photos.length || !state.quotes.length) {
    return;
  }
  const total = Math.min(4, state.photos.length, state.quotes.length);
  for (let index = 0; index < total; index += 1) {
    state.builderNodes.push({
      uid: createUID(),
      focusDurationSeconds: 25,
      breakDurationSeconds: 5,
      photoId: state.photos[index].id,
      quoteId: state.quotes[index].id,
    });
  }
}

function addBuilderNode() {
  if (!state.photos.length || !state.quotes.length) {
    return;
  }
  state.builderNodes.push({
    uid: createUID(),
    focusDurationSeconds: 25,
    breakDurationSeconds: 5,
    photoId: state.photos[0].id,
    quoteId: state.quotes[0].id,
  });
  renderBuilder();
}

function removeBuilderNode() {
  state.builderNodes.pop();
  renderBuilder();
}

function renderBuilder() {
  if (!state.builderNodes.length) {
    elements.builderCanvas.innerHTML = "<p>Owned assets are required before a custom cycle can be created.</p>";
    return;
  }
  const html = [];
  state.builderNodes.forEach((node, index) => {
    html.push(`
      <article class="builder-node" draggable="true" data-index="${index}">
        <div class="panel-header">
          <strong>Focus ${index + 1}</strong>
          <span class="node-meta">Drag to reorder</span>
        </div>
        <label class="field">
          <span>Focus Seconds</span>
          <input data-field="focusDurationSeconds" data-index="${index}" type="number" min="1" value="${node.focusDurationSeconds}">
        </label>
        <label class="field">
          <span>Photo</span>
          <select data-field="photoId" data-index="${index}">
            ${state.photos.map((photo) => `
              <option value="${photo.id}" ${photo.id === node.photoId ? "selected" : ""}>Photo ${photo.id}</option>
            `).join("")}
          </select>
        </label>
        <label class="field">
          <span>Quote</span>
          <select data-field="quoteId" data-index="${index}">
            ${state.quotes.map((quote) => `
              <option value="${quote.id}" ${quote.id === node.quoteId ? "selected" : ""}>${escapeHTML(shorten(quote.text, 36))}</option>
            `).join("")}
          </select>
        </label>
      </article>
    `);
    if (index < state.builderNodes.length - 1) {
      html.push(`
        <div class="edge-chip">
          <label>
            Break
            <input data-field="breakDurationSeconds" data-index="${index}" type="number" min="1" value="${node.breakDurationSeconds}">
          </label>
        </div>
      `);
    }
  });
  elements.builderCanvas.innerHTML = html.join("");
  bindBuilderControls();
}

function bindBuilderControls() {
  elements.builderCanvas.querySelectorAll("[data-field]").forEach((input) => {
    input.addEventListener("input", (event) => {
      const index = Number(event.target.dataset.index);
      const field = event.target.dataset.field;
      const value = event.target.tagName === "SELECT" ? Number(event.target.value) : Number(event.target.value);
      state.builderNodes[index][field] = value;
    });
  });
  elements.builderCanvas.querySelectorAll(".builder-node").forEach((card) => {
    card.addEventListener("dragstart", () => {
      state.dragIndex = Number(card.dataset.index);
      card.classList.add("dragging");
    });
    card.addEventListener("dragend", () => {
      card.classList.remove("dragging");
    });
    card.addEventListener("dragover", (event) => event.preventDefault());
    card.addEventListener("drop", () => {
      const from = state.dragIndex;
      const to = Number(card.dataset.index);
      if (from === null || from === to) {
        return;
      }
      const [item] = state.builderNodes.splice(from, 1);
      state.builderNodes.splice(to, 0, item);
      renderBuilder();
    });
  });
}

async function saveCustomCycle() {
  if (!state.builderNodes.length) {
    return;
  }
  const payload = {
    name: elements.cycleName.value || "Custom cycle",
    nodes: state.builderNodes.map((node, index) => ({
      focus_duration_seconds: Number(node.focusDurationSeconds),
      break_duration_seconds: index < state.builderNodes.length - 1 ? Number(node.breakDurationSeconds) : null,
      photo_id: Number(node.photoId),
      quote_id: Number(node.quoteId),
    })),
  };
  await fetchJSON("/cycles/custom", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  elements.cycleName.value = "";
  await refreshData();
  renderSummary();
  renderCycles();
  renderBuilder();
}

function prepareRun(cycleId) {
  const cycle = state.cycles.find((item) => item.id === cycleId);
  if (!cycle) {
    return;
  }
  state.selectedCycle = cycle;
  state.runSetup = cycle.focusNodes.map((node) => ({
    nodeOrder: node.nodeOrder,
    todosText: "",
    nottodosText: "",
  }));
  elements.runSetupPanel.classList.remove("hidden");
  elements.runSetupTitle.textContent = `${cycle.name} · ${cycle.owned ? "owned" : "trial"} mode`;
  renderRunSetup();
  elements.runSetupPanel.scrollIntoView({ behavior: "smooth", block: "start" });
}

function renderRunSetup() {
  if (!state.selectedCycle) {
    elements.runSetupList.innerHTML = "";
    return;
  }
  elements.runSetupList.innerHTML = state.selectedCycle.focusNodes.map((node, index) => `
    <article class="run-card">
      <div class="panel-header">
        <div>
          <strong>Focus ${node.nodeOrder}</strong>
          <p class="node-meta">${node.focusDurationSeconds}s · ${escapeHTML(node.quote.authorName)}</p>
        </div>
      </div>
      <label class="field">
        <span>Todo (one per line)</span>
        <textarea data-setup="todos" data-index="${index}" placeholder="Write tasks to finish in this focus"></textarea>
      </label>
      <label class="field">
        <span>Nottodo (one per line)</span>
        <textarea data-setup="nottodos" data-index="${index}" placeholder="Write distractions to avoid"></textarea>
      </label>
    </article>
  `).join("");
  elements.runSetupList.querySelectorAll("[data-setup]").forEach((field) => {
    field.addEventListener("input", (event) => {
      const index = Number(event.target.dataset.index);
      const key = event.target.dataset.setup === "todos" ? "todosText" : "nottodosText";
      state.runSetup[index][key] = event.target.value;
    });
  });
}

async function startPreparedRun() {
  if (!state.selectedCycle) {
    return;
  }
  const response = await fetchJSON("/runs", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      cycle_blueprint_id: state.selectedCycle.id,
      cycle_mode: state.selectedCycle.owned ? "owned" : "trial",
    }),
  });
  state.run = {
    id: response.runId,
    cycle: JSON.parse(JSON.stringify(state.selectedCycle)),
    focusStates: state.selectedCycle.focusNodes.map((node, index) => ({
      nodeOrder: node.nodeOrder,
      todos: linesToTasks(state.runSetup[index].todosText, "todo"),
      nottodos: linesToTasks(state.runSetup[index].nottodosText, "nottodo"),
    })),
    phase: "focus",
    index: 0,
    remainingSeconds: state.selectedCycle.focusNodes[0].focusDurationSeconds,
    totalSeconds: state.selectedCycle.focusNodes[0].focusDurationSeconds,
  };
  resetClickBurst();
  elements.modalBackdrop.classList.add("hidden");
  startInterval();
  renderRun();
  elements.timerPanel.scrollIntoView({ behavior: "smooth", block: "start" });
}

function linesToTasks(text, taskType) {
  return text.split("\n").map((line) => line.trim()).filter(Boolean).map((line) => ({
    content: line,
    taskType,
    checked: false,
    deleted: false,
  }));
}

function startInterval() {
  clearInterval(state.timerInterval);
  state.timerInterval = window.setInterval(() => {
    if (!state.run) {
      return;
    }
    state.run.remainingSeconds -= 1;
    if (state.run.remainingSeconds <= 0) {
      state.run.remainingSeconds = 0;
      renderRun();
      clearInterval(state.timerInterval);
      completeCurrentStep();
      return;
    }
    renderRun();
  }, 1000);
}

async function completeCurrentStep() {
  if (!state.run) {
    return;
  }
  if (state.run.phase === "focus") {
    const currentFocus = state.run.focusStates[state.run.index];
    await fetchJSON(`/runs/${state.run.id}/focus-complete`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        focus_order: currentFocus.nodeOrder,
        checked_todos: currentFocus.todos.filter((item) => item.checked).map((item) => item.content),
        remaining_nottodos: currentFocus.nottodos.filter((item) => !item.deleted).map((item) => item.content),
      }),
    });
    const lastIndex = state.run.focusStates.length - 1;
    if (state.run.index === lastIndex) {
      const completeResponse = await fetchJSON(`/runs/${state.run.id}/complete`, { method: "POST" });
      playSessionEndSound();
      openRewardModal(completeResponse.reward.actions);
      return;
    }
    playSessionEndSound();
    const edge = state.run.cycle.breakEdges.find((item) => item.fromNodeOrder === currentFocus.nodeOrder);
    state.run.phase = "break";
    state.run.remainingSeconds = edge.breakDurationSeconds;
    state.run.totalSeconds = edge.breakDurationSeconds;
    renderRun();
    window.setTimeout(() => {
      if (!state.run || state.run.phase !== "break") {
        return;
      }
      startInterval();
      renderRun();
    }, 900);
    return;
  }
  playSessionEndSound();
  state.run.phase = "focus";
  state.run.index += 1;
  const nextNode = state.run.cycle.focusNodes[state.run.index];
  state.run.remainingSeconds = nextNode.focusDurationSeconds;
  state.run.totalSeconds = nextNode.focusDurationSeconds;
  renderRun();
  window.setTimeout(() => {
    if (!state.run || state.run.phase !== "focus") {
      return;
    }
    startInterval();
    renderRun();
  }, 900);
}

function renderRun() {
  if (!state.run) {
    renderTimerIdle();
    return;
  }
  const currentNode = state.run.cycle.focusNodes[state.run.index];
  const phaseLabel = state.run.phase === "focus" ? `Focus ${currentNode.nodeOrder}` : `Break ${currentNode.nodeOrder}`;
  elements.timerMode.textContent = phaseLabel;
  elements.timerClock.textContent = formatSeconds(state.run.remainingSeconds);
  elements.timerQuote.textContent = currentNode.quote.text;
  elements.timerAuthor.textContent = currentNode.quote.authorName;
  elements.timerSource.textContent = currentNode.photo.sourceLabel || "";
  elements.timerHero.style.backgroundImage = `linear-gradient(120deg, rgba(30, 26, 22, 0.72), rgba(30, 26, 22, 0.18)), url('${currentNode.photo.url}')`;
  const progress = ((state.run.totalSeconds - state.run.remainingSeconds) / state.run.totalSeconds) * 100;
  elements.timerProgress.style.width = `${Math.max(progress, 0)}%`;
  renderTasks();
}

function renderTimerIdle() {
  elements.timerMode.textContent = "Idle";
  elements.timerClock.textContent = "00";
  elements.timerQuote.textContent = "Choose a cycle and prepare a run.";
  elements.timerAuthor.textContent = "";
  elements.timerSource.textContent = "";
  elements.timerHero.style.backgroundImage = "linear-gradient(120deg, rgba(30, 26, 22, 0.72), rgba(30, 26, 22, 0.18))";
  elements.timerProgress.style.width = "0%";
  elements.taskPanel.innerHTML = "<p>No active run.</p>";
  renderClickDots(0);
}

function renderTasks() {
  if (!state.run) {
    return;
  }
  if (state.run.phase !== "focus") {
    elements.taskPanel.innerHTML = "<p>Break session. Wait for the next focus or stop the run.</p>";
    return;
  }
  const focusState = state.run.focusStates[state.run.index];
  elements.taskPanel.innerHTML = `
    <div class="task-list">
      <h3>Todo</h3>
      ${focusState.todos.length ? focusState.todos.map((item, index) => `
        <label class="task-item ${item.checked ? "todo-checked" : ""}">
          <input data-task-type="todo" data-index="${index}" type="checkbox" ${item.checked ? "checked" : ""}>
          <span>${escapeHTML(item.content)}</span>
        </label>
      `).join("") : "<p>No todo items for this focus.</p>"}
    </div>
    <div class="task-list">
      <h3>Nottodo</h3>
      ${focusState.nottodos.length ? focusState.nottodos.map((item, index) => `
        <button class="task-item ${item.deleted ? "deleted" : ""}" data-task-type="nottodo" data-index="${index}" type="button">
          <span>${escapeHTML(item.content)}</span>
        </button>
      `).join("") : "<p>No nottodo items for this focus.</p>"}
    </div>
  `;
  elements.taskPanel.querySelectorAll("[data-task-type='todo']").forEach((input) => {
    input.addEventListener("change", (event) => {
      const index = Number(event.target.dataset.index);
      focusState.todos[index].checked = event.target.checked;
      renderTasks();
    });
  });
  elements.taskPanel.querySelectorAll("[data-task-type='nottodo']").forEach((button) => {
    button.addEventListener("click", () => {
      const index = Number(button.dataset.index);
      focusState.nottodos[index].deleted = !focusState.nottodos[index].deleted;
      renderTasks();
    });
  });
}

function openRewardModal(actions) {
  elements.modalBackdrop.classList.remove("hidden");
  elements.modalBox.innerHTML = `
    <h3>Reward</h3>
    <p>All focus sessions are complete. Choose one reward action.</p>
    <div class="reward-actions">
      ${actions.includes("claim_cycle") ? '<button id="claim-cycle-btn" type="button">Collect This Cycle</button>' : ""}
      ${actions.includes("upload_photo") ? '<button id="show-upload-btn" class="ghost" type="button">Upload One Photo</button>' : ""}
      ${actions.includes("add_quote") ? '<button id="show-quote-btn" class="ghost" type="button">Add One Quote</button>' : ""}
    </div>
    <form id="upload-form" class="reward-form hidden">
      <input id="upload-file" type="file" accept="image/*">
      <button type="submit">Use Photo Reward</button>
    </form>
    <form id="quote-form" class="reward-form hidden">
      <input id="quote-text" type="text" placeholder="Quote text">
      <input id="quote-author" type="text" placeholder="Author">
      <button type="submit">Use Quote Reward</button>
    </form>
  `;
  const claimButton = document.getElementById("claim-cycle-btn");
  if (claimButton) {
    claimButton.addEventListener("click", async () => {
      await fetchJSON(`/rewards/${state.run.id}/claim-cycle`, { method: "POST" });
      finishRewardFlow();
    });
  }
  const uploadButton = document.getElementById("show-upload-btn");
  if (uploadButton) {
    uploadButton.addEventListener("click", () => {
      document.getElementById("upload-form").classList.toggle("hidden");
    });
    document.getElementById("upload-form").addEventListener("submit", async (event) => {
      event.preventDefault();
      const fileInput = document.getElementById("upload-file");
      if (!fileInput.files.length) {
        return;
      }
      const formData = new FormData();
      formData.append("file", fileInput.files[0]);
      await fetchJSON(`/rewards/${state.run.id}/upload-photo`, { method: "POST", body: formData });
      finishRewardFlow();
    });
  }
  const quoteButton = document.getElementById("show-quote-btn");
  if (quoteButton) {
    quoteButton.addEventListener("click", () => {
      document.getElementById("quote-form").classList.toggle("hidden");
    });
    document.getElementById("quote-form").addEventListener("submit", async (event) => {
      event.preventDefault();
      const formData = new FormData();
      formData.append("text", document.getElementById("quote-text").value);
      formData.append("author_name", document.getElementById("quote-author").value);
      formData.append("category", "custom");
      await fetchJSON(`/rewards/${state.run.id}/add-quote`, { method: "POST", body: formData });
      finishRewardFlow();
    });
  }
}

async function finishRewardFlow() {
  elements.modalBackdrop.classList.add("hidden");
  stopLocalRun(false);
  await refreshData();
  renderSummary();
  renderCycles();
  renderBuilder();
  renderCollection();
}

async function stopRunOnServer() {
  if (!state.run) {
    return;
  }
  await fetchJSON(`/runs/${state.run.id}/stop`, { method: "POST" });
}

function stopLocalRun(silent) {
  clearInterval(state.timerInterval);
  state.run = null;
  state.selectedCycle = null;
  state.runSetup = [];
  elements.runSetupPanel.classList.add("hidden");
  elements.runSetupList.innerHTML = "";
  resetClickBurst();
  if (!silent && state.me) {
    refreshData().then(() => {
      renderSummary();
      renderCycles();
      renderBuilder();
      renderCollection();
      renderTimerIdle();
    });
  } else {
    renderTimerIdle();
  }
}

function handleTripleClick(event) {
  if (!state.run) {
    return;
  }
  if (event.target.closest(".modal-box")) {
    return;
  }
  const now = Date.now();
  state.clickBurst = state.clickBurst.filter((item) => now - item < 800);
  state.clickBurst.push(now);
  renderClickDots(state.clickBurst.length);
  if (state.clickBurstResetTimer) {
    window.clearTimeout(state.clickBurstResetTimer);
  }
  state.clickBurstResetTimer = window.setTimeout(() => {
    resetClickBurst();
  }, 900);
  if (state.clickBurst.length >= 3) {
    playSessionEndSound();
    stopRunOnServer().finally(() => stopLocalRun(false));
  }
}

function renderClickDots(count) {
  elements.clickDots.forEach((dot, index) => {
    dot.classList.toggle("active", index < count);
  });
}

function resetClickBurst() {
  state.clickBurst = [];
  if (state.clickBurstResetTimer) {
    window.clearTimeout(state.clickBurstResetTimer);
    state.clickBurstResetTimer = null;
  }
  renderClickDots(0);
}

function playSessionEndSound() {
  const AudioContextClass = window.AudioContext || window.webkitAudioContext;
  if (!AudioContextClass) {
    return;
  }
  if (!state.audioContext) {
    state.audioContext = new AudioContextClass();
  }
  const context = state.audioContext;
  if (context.state === "suspended" && context.resume) {
    context.resume();
  }
  const startAt = context.currentTime;
  const oscillator = context.createOscillator();
  const gain = context.createGain();
  oscillator.type = "sine";
  oscillator.frequency.setValueAtTime(880, startAt);
  oscillator.frequency.linearRampToValueAtTime(660, startAt + 0.18);
  gain.gain.setValueAtTime(0.0001, startAt);
  gain.gain.exponentialRampToValueAtTime(0.18, startAt + 0.02);
  gain.gain.exponentialRampToValueAtTime(0.0001, startAt + 0.28);
  oscillator.connect(gain);
  gain.connect(context.destination);
  oscillator.start(startAt);
  oscillator.stop(startAt + 0.3);
}

function renderCollection() {
  if (!state.collection.length) {
    elements.collectionList.innerHTML = "<p>No collected cycles yet.</p>";
    return;
  }
  elements.collectionList.innerHTML = state.collection.map((item) => `
    <article class="collection-card">
      <div class="panel-header">
        <div>
          <h3>${escapeHTML(item.name)}</h3>
          <p class="node-meta">${new Date(item.collectedAt).toLocaleString()}</p>
        </div>
      </div>
      <div class="focus-strip">
        ${item.focusNodes.map((node) => `
          <div class="focus-mini">
            <img src="${node.photo.url}" alt="" style="width:100%;height:90px;object-fit:cover;border-radius:12px;">
            <p>${escapeHTML(shorten(node.quote.text, 48))}</p>
          </div>
        `).join("")}
      </div>
    </article>
  `).join("");
}

async function fetchJSON(url, options = {}) {
  const response = await fetch(url, options);
  if (!response.ok) {
    const payload = await response.json().catch(() => ({ detail: "Request failed" }));
    window.alert(payload.detail || "Request failed");
    throw new Error(payload.detail || "Request failed");
  }
  return response.json();
}

function formatSeconds(value) {
  const minutes = Math.floor(value / 60);
  const seconds = value % 60;
  return `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
}

function escapeHTML(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function shorten(value, maxLength) {
  if (value.length <= maxLength) {
    return value;
  }
  return `${value.slice(0, maxLength - 1)}…`;
}

function createUID() {
  return Math.random().toString(36).slice(2, 10);
}
