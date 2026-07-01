const state = {
  apiHost: localStorage.getItem("adminApiHost") || defaultApiHost(),
  token: localStorage.getItem("adminToken") || "",
  user: null,
  mode: "login",
  activeView: "overview",
  chatbots: [],
  sessions: [],
  selectionSessions: [],
  interviewSessions: [],
  selectedSessionId: "",
  selectedSelectionId: "",
  selectedInterviewId: "",
  pollTimer: null,
};

function defaultApiHost() {
  if (window.location.protocol === "file:" || window.location.hostname === "127.0.0.1" || window.location.hostname === "localhost") {
    return "http://127.0.0.1:8000";
  }
  return `${window.location.origin}/chatbot/api`;
}

const $ = (id) => document.getElementById(id);

document.addEventListener("DOMContentLoaded", () => {
  $("apiHost").value = state.apiHost;
  bindEvents();
  if (state.token) {
    loadMe().catch(() => showAuth());
  } else {
    checkSetupStatus();
  }
});

function bindEvents() {
  $("loginTab").addEventListener("click", () => setAuthMode("login"));
  $("setupTab").addEventListener("click", () => setAuthMode("setup"));
  $("authForm").addEventListener("submit", submitAuth);
  $("logoutButton").addEventListener("click", logout);
  $("refreshButton").addEventListener("click", refreshActiveView);
  $("apiHost").addEventListener("change", () => {
    state.apiHost = $("apiHost").value.replace(/\/$/, "");
    localStorage.setItem("adminApiHost", state.apiHost);
  });
  document.querySelectorAll(".nav").forEach((button) => {
    button.addEventListener("click", () => switchView(button.dataset.view));
  });
  $("filterForm").addEventListener("submit", (event) => {
    event.preventDefault();
    loadSessions();
  });
  $("selectionFilterForm").addEventListener("submit", (event) => {
    event.preventDefault();
    loadSelectionSessions();
  });
  $("interviewFilterForm").addEventListener("submit", (event) => {
    event.preventDefault();
    loadInterviewSessions();
  });
  $("exportButton").addEventListener("click", exportCsv);
  $("selectionExportButton").addEventListener("click", exportSelectionCsv);
  $("interviewExportButton").addEventListener("click", exportInterviewCsv);
  $("createUserForm").addEventListener("submit", createUser);
}

async function checkSetupStatus() {
  try {
    const data = await request("/admin/setup/status", { auth: false });
    setAuthMode(data.has_admin_users ? "login" : "setup");
  } catch {
    setAuthMode("login");
  }
}

function setAuthMode(mode) {
  state.mode = mode;
  $("loginTab").classList.toggle("active", mode === "login");
  $("setupTab").classList.toggle("active", mode === "setup");
  $("displayNameRow").classList.toggle("hidden", mode !== "setup");
  $("authMessage").textContent = mode === "setup"
    ? "Create the first admin account. This is disabled after setup."
    : "";
}

async function submitAuth(event) {
  event.preventDefault();
  const payload = {
    email: $("email").value,
    password: $("password").value,
    display_name: $("displayName").value,
  };
  try {
    if (state.mode === "setup") {
      await request("/admin/setup/bootstrap", {
        method: "POST",
        auth: false,
        body: payload,
      });
    }
    const login = await request("/admin/login", {
      method: "POST",
      auth: false,
      body: { email: payload.email, password: payload.password },
    });
    state.token = login.token;
    state.user = login.user;
    localStorage.setItem("adminToken", state.token);
    showDashboard();
  } catch (error) {
    $("authMessage").textContent = error.message;
  }
}

async function loadMe() {
  const data = await request("/admin/me");
  state.user = data.user;
  showDashboard();
}

function showAuth() {
  $("authView").classList.remove("hidden");
  $("dashboardView").classList.add("hidden");
  clearInterval(state.pollTimer);
}

function showDashboard() {
  $("authView").classList.add("hidden");
  $("dashboardView").classList.remove("hidden");
  $("currentUser").textContent = `${state.user.display_name} · ${state.user.role}`;
  $("apiHost").value = state.apiHost;
  switchView("overview");
  clearInterval(state.pollTimer);
  state.pollTimer = setInterval(refreshActiveView, 5000);
}

function logout() {
  state.token = "";
  state.user = null;
  localStorage.removeItem("adminToken");
  showAuth();
}

function switchView(view) {
  state.activeView = view;
  document.querySelectorAll(".nav").forEach((button) => {
    button.classList.toggle("active", button.dataset.view === view);
  });
  document.querySelectorAll(".view-panel").forEach((panel) => panel.classList.add("hidden"));
  $(`${view}Panel`).classList.remove("hidden");
  $("viewTitle").textContent = view[0].toUpperCase() + view.slice(1);
  refreshActiveView();
}

function refreshActiveView() {
  if (state.activeView === "overview") loadOverview();
  if (state.activeView === "selection") loadSelectionSessions();
  if (state.activeView === "interviews") loadInterviewSessions();
  if (state.activeView === "sessions") loadSessions();
  if (state.activeView === "access") loadAccess();
  if (state.activeView === "audit") loadAudit();
}

async function loadOverview() {
  try {
    const [summary, chatbots] = await Promise.all([
      request("/admin/summary"),
      request("/admin/chatbots"),
    ]);
    state.chatbots = chatbots.chatbots;
    renderChatbotFilter();
    renderSummary(summary.chatbots);
    markUpdated(summary.updated_at);
  } catch (error) {
    renderError("summaryCards", error);
  }
}

function renderSummary(chatbots) {
  $("summaryCards").innerHTML = chatbots.length ? chatbots.map((bot) => `
    <article class="panel summary-card">
      <h3>${escapeHtml(bot.name)}</h3>
      <div class="metric-grid">
        ${metric("Active", bot.active_sessions)}
        ${metric("Completed", bot.completed_sessions)}
        ${metric("Messages", bot.total_messages)}
        ${metric("Failures", bot.failed_requests)}
        ${metric("Avg ms", bot.average_response_time_ms ?? "n/a")}
        ${metric("Recent", formatDate(bot.most_recent_activity_at))}
      </div>
    </article>
  `).join("") : `<p class="muted">No authorized chatbot data is available yet.</p>`;
}

function metric(label, value) {
  return `<div class="metric"><span>${label}</span><strong>${value}</strong></div>`;
}

async function loadSessions() {
  try {
    if (!state.chatbots.length) {
      const chatbots = await request("/admin/chatbots");
      state.chatbots = chatbots.chatbots;
      renderChatbotFilter();
    }
    const data = await request(`/admin/sessions?${filterQuery()}`);
    state.sessions = data.sessions;
    renderSessions(data.sessions);
    if (state.selectedSessionId) {
      loadConversation(state.selectedSessionId);
    }
    markUpdated();
  } catch (error) {
    $("sessionRows").innerHTML = `<tr><td colspan="6">${escapeHtml(error.message)}</td></tr>`;
  }
}

function renderChatbotFilter() {
  const current = $("filterChatbot").value;
  $("filterChatbot").innerHTML = `<option value="">All</option>${state.chatbots.map((bot) => (
    `<option value="${escapeHtml(bot.key)}">${escapeHtml(bot.name)}</option>`
  )).join("")}`;
  $("filterChatbot").value = current;
}

function renderSessions(sessions) {
  $("sessionRows").innerHTML = sessions.length ? sessions.map((session) => `
    <tr data-session-id="${escapeHtml(session.session_id)}">
      <td><strong>${escapeHtml(session.participant_id)}</strong><br><span class="muted">${escapeHtml(session.session_id)}</span></td>
      <td>${escapeHtml(session.chatbot_name)}</td>
      <td><span class="status ${escapeHtml(session.status)}">${escapeHtml(session.status)}</span></td>
      <td>${session.message_count}</td>
      <td><span class="status ${session.failed_requests ? "failed" : "ok"}">${session.failed_requests}</span></td>
      <td>${formatDate(session.updated_at)}</td>
    </tr>
  `).join("") : `<tr><td colspan="6">No sessions match the current filters.</td></tr>`;
  document.querySelectorAll("[data-session-id]").forEach((row) => {
    row.addEventListener("click", () => {
      state.selectedSessionId = row.dataset.sessionId;
      loadConversation(state.selectedSessionId);
    });
  });
}

async function loadSelectionSessions() {
  try {
    const data = await request(`/admin/selection/sessions?${selectionQuery()}`);
    state.selectionSessions = data.sessions;
    renderAttention("selectionAttention", data.sessions);
    renderSelectionSessions(data.sessions);
    if (state.selectedSelectionId) {
      loadConversation(state.selectedSelectionId, "selectionDetail");
    }
    markUpdated();
  } catch (error) {
    $("selectionRows").innerHTML = `<tr><td colspan="11">${escapeHtml(error.message)}</td></tr>`;
  }
}

function renderSelectionSessions(sessions) {
  $("selectionRows").innerHTML = sessions.length ? sessions.map((session) => `
    <tr data-selection-id="${escapeHtml(session.session_id)}" class="${session.needs_attention ? "needs-attention" : ""}">
      <td><button class="copy-id" type="button" title="${escapeHtml(session.session_id)}">${escapeHtml(session.short_session_id)}</button><br><span class="muted">${escapeHtml(session.participant_id)}</span><div class="tag-row">${renderTags(session.status_tags)}</div></td>
      <td><span class="status ${escapeHtml(session.selection_status)}">${escapeHtml(session.selection_status)}</span></td>
      <td>${escapeHtml(session.selected_mode || "missing")}</td>
      <td><span class="status ${session.selection_reason_status === "present" ? "ok" : "failed"}">${escapeHtml(session.selection_reason_status)}</span></td>
      <td><span class="status ${session.handoff_status === "handoff_completed" ? "ok" : "failed"}">${escapeHtml(session.handoff_status)}</span></td>
      <td>${session.message_count}</td>
      <td><span class="status ${session.failure_count || session.backend_error_count ? "failed" : "ok"}">${session.failure_count + session.backend_error_count}</span></td>
      <td>${formatDate(session.start_time)}</td>
      <td>${formatDate(session.end_time)}</td>
      <td>${formatDate(session.last_activity_at)}</td>
      <td>${formatDuration(session.duration_seconds)}</td>
    </tr>
  `).join("") : `<tr><td colspan="11">No Selection sessions match the current filters.</td></tr>`;
  document.querySelectorAll("[data-selection-id]").forEach((row) => {
    row.addEventListener("click", () => {
      state.selectedSelectionId = row.dataset.selectionId;
      loadConversation(state.selectedSelectionId, "selectionDetail");
    });
  });
  bindCopyButtons();
}

async function loadInterviewSessions() {
  try {
    const data = await request(`/admin/interviews/sessions?${interviewQuery()}`);
    state.interviewSessions = data.sessions;
    renderAttention("interviewAttention", data.sessions);
    renderInterviewSessions(data.sessions);
    if (state.selectedInterviewId) {
      loadConversation(state.selectedInterviewId, "interviewDetail");
    }
    markUpdated();
  } catch (error) {
    $("interviewRows").innerHTML = `<tr><td colspan="12">${escapeHtml(error.message)}</td></tr>`;
  }
}

function renderInterviewSessions(sessions) {
  $("interviewRows").innerHTML = sessions.length ? sessions.map((session) => `
    <tr data-interview-id="${escapeHtml(session.session_id)}" class="${session.needs_attention ? "needs-attention" : ""}">
      <td><button class="copy-id" type="button" title="${escapeHtml(session.session_id)}">${escapeHtml(session.short_session_id)}</button><br><span class="muted">${escapeHtml(session.participant_id)}</span><div class="tag-row">${renderTags(session.status_tags)}</div></td>
      <td>${escapeHtml(session.chatbot_type)}</td>
      <td><span class="status ${escapeHtml(session.status)}">${escapeHtml(session.status)}</span></td>
      <td>${escapeHtml(session.progress_label || "n/a")}<br><span class="muted">${escapeHtml(session.last_node || "")}</span></td>
      <td>${session.message_count} <span class="muted">(${session.user_message_count} user / ${session.assistant_message_count} bot)</span></td>
      <td><span class="status ${session.failure_count || session.backend_error_count ? "failed" : "ok"}">${session.failure_count + session.backend_error_count}</span></td>
      <td><span class="status ${session.error_status === "has_error" ? "failed" : "ok"}">${escapeHtml(session.error_status)}</span></td>
      <td>${session.average_latency_ms ?? "n/a"} ms</td>
      <td>${formatDate(session.start_time)}</td>
      <td>${formatDate(session.end_time)}</td>
      <td>${formatDate(session.last_activity_at)}</td>
      <td>${formatDuration(session.duration_seconds)}</td>
    </tr>
  `).join("") : `<tr><td colspan="12">No Interview sessions match the current filters.</td></tr>`;
  document.querySelectorAll("[data-interview-id]").forEach((row) => {
    row.addEventListener("click", () => {
      state.selectedInterviewId = row.dataset.interviewId;
      loadConversation(state.selectedInterviewId, "interviewDetail");
    });
  });
  bindCopyButtons();
}

async function loadConversation(sessionId) {
  const detail = $(arguments[1] || "conversationDetail");
  try {
    const data = await request(`/admin/sessions/${encodeURIComponent(sessionId)}`);
    detail.innerHTML = `
      <h3>${escapeHtml(data.session.participant_id)}</h3>
      <p class="muted">${escapeHtml(data.session.chatbot_name)} · ${escapeHtml(data.session.status)} · ${formatDate(data.session.updated_at)}</p>
      ${renderSelectionSummary(data.selection_summary || data.session)}
      ${renderInterviewSummary(data.interview_summary)}
      ${renderTranscriptControls(detail.id)}
      <h4>Conversation</h4>
      <div class="conversation-list" id="${detail.id}Messages">
        ${data.messages.map(renderMessage).join("") || `<p class="muted">No messages recorded yet.</p>`}
      </div>
      <h4>Backend Request Timeline</h4>
      <div class="timeline">
        ${data.request_logs.map(renderTimeline).join("") || `<p class="muted">No backend request logs recorded yet.</p>`}
      </div>
    `;
    bindTranscriptControls(detail.id);
  } catch (error) {
    detail.innerHTML = `<p class="muted">${escapeHtml(error.message)}</p>`;
  }
}

function renderMessage(message) {
  return `
    <article class="message-card ${escapeHtml(message.role)} ${message.processing_status === "failed" ? "failed" : ""}" data-role="${escapeHtml(message.role)}" data-status="${escapeHtml(message.processing_status)}" data-content="${escapeHtml(message.content)}">
      <div class="message-meta">
        <span>${message.sequence_number}</span>
        <span>${escapeHtml(message.role)}</span>
        <span class="status ${escapeHtml(message.processing_status)}">${escapeHtml(message.processing_status)}</span>
        <span>${formatDate(message.server_received_at)}</span>
        <span>${message.latency_ms ? `${message.latency_ms} ms` : ""}</span>
        ${message.raw_transcript ? `<span>raw transcript present</span>` : ""}
      </div>
      <p class="message-text">${escapeHtml(message.content)}</p>
      ${message.raw_transcript ? `<p class="debug-text"><strong>Raw transcript:</strong> ${escapeHtml(message.raw_transcript)}</p>` : ""}
      ${message.raw_user_input && message.raw_user_input !== message.content ? `<p class="debug-text"><strong>Stored input:</strong> ${escapeHtml(message.raw_user_input)}</p>` : ""}
    </article>
  `;
}

function renderSelectionSummary(summary) {
  if (!summary?.selection_reason && !summary?.selection_reason_status) return "";
  return `
    <section class="sticky-summary">
      <h4>Selection Summary</h4>
      <div class="summary-kv">
        ${kv("Selection status", summary.selection_status || summary.status)}
        ${kv("Selected mode", summary.selected_mode || summary.modality_group || "missing")}
        ${kv("Reason status", summary.selection_reason_status || (summary.selection_reason ? "present" : "missing"))}
        ${kv("Reason timestamp", formatDate(summary.selection_reason_timestamp || summary.selection_reason_client_at))}
        ${kv("Handoff", summary.handoff_status || "n/a")}
        ${kv("Messages", summary.message_count ?? "n/a")}
        ${kv("Failures", (summary.failure_count ?? summary.failed_requests ?? 0) + (summary.backend_error_count ?? 0))}
        ${kv("Start", formatDate(summary.start_time || summary.created_at))}
        ${kv("End", formatDate(summary.end_time || summary.completed_at))}
        ${kv("Duration", formatDuration(summary.duration_seconds))}
        ${kv("Last activity", formatDate(summary.last_activity_at || summary.updated_at))}
      </div>
      <div class="reason-box"><strong>Selection reason</strong><p>${escapeHtml(summary.selection_reason || "")}</p></div>
      <div class="tag-row">${renderTags(summary.status_tags || [])}</div>
    </section>
  `;
}

function renderInterviewSummary(summary) {
  if (!summary) return "";
  return `
    <section class="sticky-summary">
      <h4>Interview Summary</h4>
      <div class="summary-kv">
        ${kv("Chatbot type", summary.chatbot_type)}
        ${kv("Status", summary.status)}
        ${kv("Progress", summary.progress_label || "n/a")}
        ${kv("Last question", summary.last_completed_question || "n/a")}
        ${kv("Last node", summary.last_node || "n/a")}
        ${kv("Last speaker", summary.last_speaker || "n/a")}
        ${kv("Messages", `${summary.message_count} (${summary.user_message_count} user / ${summary.assistant_message_count} bot)`)}
        ${kv("Failures", (summary.failure_count || 0) + (summary.backend_error_count || 0))}
        ${kv("Average latency", summary.average_latency_ms ? `${summary.average_latency_ms} ms` : "n/a")}
        ${kv("Median latency", summary.median_latency_ms ? `${summary.median_latency_ms} ms` : "n/a")}
        ${kv("Start", formatDate(summary.start_time))}
        ${kv("End", formatDate(summary.end_time))}
        ${kv("Duration", formatDuration(summary.duration_seconds))}
        ${kv("Last activity", formatDate(summary.last_activity_at))}
      </div>
      <div class="tag-row">${renderTags(summary.status_tags || [])}</div>
    </section>
  `;
}

function renderTranscriptControls(scope) {
  return `
    <div class="transcript-controls" data-scope="${scope}">
      <input id="${scope}Search" type="search" placeholder="Search conversation..." />
      <select id="${scope}Role"><option value="">All speakers</option><option value="user">User</option><option value="assistant">Assistant</option><option value="system">System</option></select>
      <select id="${scope}Status"><option value="">All statuses</option><option value="completed">Completed</option><option value="failed">Failed/error</option><option value="pending">Pending</option></select>
      <button class="secondary" type="button" id="${scope}Latest">Latest</button>
      <button class="secondary" type="button" id="${scope}Error">Next error</button>
      <button class="secondary" type="button" id="${scope}Compact">Compact</button>
    </div>
  `;
}

function bindTranscriptControls(scope) {
  const apply = () => filterTranscript(scope);
  [`${scope}Search`, `${scope}Role`, `${scope}Status`].forEach((id) => $(id)?.addEventListener("input", apply));
  $(`${scope}Latest`)?.addEventListener("click", () => {
    const list = $(`${scope}Messages`);
    list?.lastElementChild?.scrollIntoView({ block: "nearest" });
  });
  $(`${scope}Error`)?.addEventListener("click", () => {
    const error = $(`${scope}Messages`)?.querySelector(".failed,[data-status='failed']");
    error?.scrollIntoView({ block: "center" });
  });
  $(`${scope}Compact`)?.addEventListener("click", () => {
    $(`${scope}Messages`)?.classList.toggle("compact-messages");
  });
}

function filterTranscript(scope) {
  const search = ($(`${scope}Search`)?.value || "").toLowerCase();
  const role = $(`${scope}Role`)?.value || "";
  const status = $(`${scope}Status`)?.value || "";
  $(`${scope}Messages`)?.querySelectorAll(".message-card").forEach((card) => {
    const matchesSearch = !search || card.dataset.content.toLowerCase().includes(search);
    const matchesRole = !role || card.dataset.role === role;
    const matchesStatus = !status || card.dataset.status === status || (status === "failed" && card.dataset.status === "error");
    card.classList.toggle("hidden", !(matchesSearch && matchesRole && matchesStatus));
  });
}

function kv(label, value) {
  return `<div><span>${escapeHtml(label)}</span><strong>${escapeHtml(value ?? "n/a")}</strong></div>`;
}

function renderTags(tags) {
  return (tags || []).map((tag) => `<span class="tag ${tag.includes("missing") || tag.includes("failed") || tag.includes("error") || tag.includes("stalled") ? "attention" : ""}">${escapeHtml(tag)}</span>`).join("");
}

function renderAttention(targetId, sessions) {
  const count = sessions.filter((session) => session.needs_attention).length;
  $(targetId).innerHTML = count
    ? `<strong>${count} need attention</strong><span class="muted">Flagged rows are sorted to the top.</span>`
    : `<strong>No attention flags</strong><span class="muted">Current filtered rows look healthy.</span>`;
}

function renderTimeline(log) {
  return `
    <article class="timeline-card ${escapeHtml(log.status)}">
      <div class="timeline-meta">
        <span>${escapeHtml(log.step)}</span>
        <span class="status ${escapeHtml(log.status)}">${escapeHtml(log.status)}</span>
        <span>${formatDate(log.created_at)}</span>
      </div>
      ${log.detail ? `<p class="message-text">${escapeHtml(log.detail)}</p>` : ""}
    </article>
  `;
}

async function exportCsv() {
  try {
    const response = await fetch(`${state.apiHost}/admin/export/messages.csv?${filterQuery()}`, {
      headers: { Authorization: `Bearer ${state.token}` },
    });
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || `Export failed (${response.status})`);
    }
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "admin-message-export.csv";
    link.click();
    URL.revokeObjectURL(url);
  } catch (error) {
    alert(error.message);
  }
}

async function exportSelectionCsv() {
  await downloadCsv(`/admin/selection/export.csv?${selectionQuery()}`, "selection-session-export.csv");
}

async function exportInterviewCsv() {
  await downloadCsv(`/admin/interviews/export.csv?${interviewQuery()}`, "interview-session-export.csv");
}

async function downloadCsv(path, filename) {
  try {
    const response = await fetch(`${state.apiHost}${path}`, {
      headers: { Authorization: `Bearer ${state.token}` },
    });
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || `Export failed (${response.status})`);
    }
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);
  } catch (error) {
    alert(error.message);
  }
}

async function loadAccess() {
  if (state.user.role !== "admin") {
    $("userRows").innerHTML = `<p class="muted">Only admins can manage user access.</p>`;
    return;
  }
  try {
    const data = await request("/admin/users");
    renderUsers(data.users);
    markUpdated();
  } catch (error) {
    $("userRows").innerHTML = `<p class="muted">${escapeHtml(error.message)}</p>`;
  }
}

function renderUsers(users) {
  $("userRows").innerHTML = users.map((user) => `
    <form class="user-row" data-user-id="${escapeHtml(user.id)}">
      <div><h4>${escapeHtml(user.display_name)}</h4><p class="muted">${escapeHtml(user.email)}</p></div>
      <label>Role<select name="role">${["admin", "project_leader", "viewer"].map((role) => (
        `<option value="${role}" ${user.role === role ? "selected" : ""}>${role}</option>`
      )).join("")}</select></label>
      <label>Sub-chatbot keys<input name="keys" value="${escapeHtml((user.chatbot_keys || []).join(", "))}" /></label>
      <label>Active<select name="active"><option value="true" ${user.is_active ? "selected" : ""}>Yes</option><option value="false" ${!user.is_active ? "selected" : ""}>No</option></select></label>
      <button class="secondary" type="submit">Save</button>
    </form>
  `).join("");
  document.querySelectorAll(".user-row").forEach((form) => {
    form.addEventListener("submit", saveUserAccess);
  });
}

async function createUser(event) {
  event.preventDefault();
  try {
    await request("/admin/users", {
      method: "POST",
      body: {
        email: $("newUserEmail").value,
        password: $("newUserPassword").value,
        display_name: $("newUserName").value,
        role: $("newUserRole").value,
        chatbot_keys: parseKeys($("newUserKeys").value),
      },
    });
    event.target.reset();
    loadAccess();
  } catch (error) {
    alert(error.message);
  }
}

async function saveUserAccess(event) {
  event.preventDefault();
  const form = event.currentTarget;
  try {
    await request(`/admin/users/${encodeURIComponent(form.dataset.userId)}/access`, {
      method: "PUT",
      body: {
        role: form.elements.role.value,
        chatbot_keys: parseKeys(form.elements.keys.value),
        is_active: form.elements.active.value === "true",
      },
    });
    loadAccess();
  } catch (error) {
    alert(error.message);
  }
}

async function loadAudit() {
  if (state.user.role !== "admin") {
    $("auditRows").innerHTML = `<tr><td colspan="4">Only admins can view audit logs.</td></tr>`;
    return;
  }
  try {
    const data = await request("/admin/audit-logs");
    $("auditRows").innerHTML = data.audit_logs.map((log) => `
      <tr><td>${formatDate(log.created_at)}</td><td>${escapeHtml(log.user_id || "")}</td><td>${escapeHtml(log.action)}</td><td>${escapeHtml(log.resource_type || "")} ${escapeHtml(log.resource_id || "")}</td></tr>
    `).join("") || `<tr><td colspan="4">No audit logs yet.</td></tr>`;
    markUpdated();
  } catch (error) {
    $("auditRows").innerHTML = `<tr><td colspan="4">${escapeHtml(error.message)}</td></tr>`;
  }
}

function filterQuery() {
  const text = $("filterText").value.trim();
  const params = new URLSearchParams();
  if ($("filterChatbot").value) params.set("chatbot_key", $("filterChatbot").value);
  if (text) {
    params.set(text.includes("-") ? "session_id" : "participant_id", text);
  }
  if ($("filterStart").value) params.set("date_start", new Date($("filterStart").value).toISOString());
  if ($("filterEnd").value) params.set("date_end", new Date($("filterEnd").value).toISOString());
  if ($("filterStatus").value) params.set("completion_status", $("filterStatus").value);
  if ($("filterErrors").value) params.set("error_status", $("filterErrors").value);
  return params.toString();
}

function selectionQuery() {
  const params = new URLSearchParams();
  const text = $("selectionText").value.trim();
  if ($("selectionMode").value) params.set("selected_mode", $("selectionMode").value);
  if (text) params.set(text.includes("-") ? "session_id" : "participant_id", text);
  if ($("selectionStart").value) params.set("date_start", new Date($("selectionStart").value).toISOString());
  if ($("selectionEnd").value) params.set("date_end", new Date($("selectionEnd").value).toISOString());
  if ($("selectionStatus").value) params.set("completion_status", $("selectionStatus").value);
  return params.toString();
}

function interviewQuery() {
  const params = new URLSearchParams();
  const text = $("interviewText").value.trim();
  if ($("interviewType").value) params.set("chatbot_type", $("interviewType").value);
  if (text) params.set(text.includes("-") ? "session_id" : "participant_id", text);
  if ($("interviewStatus").value) params.set("completion_status", $("interviewStatus").value);
  if ($("interviewInput").value) params.set("input_method", $("interviewInput").value);
  if ($("interviewFailures").checked) params.set("has_failures", "true");
  if ($("interviewStalled").checked) params.set("stalled_only", "true");
  if ($("interviewLowMessages").checked) params.set("low_message_count", "true");
  if ($("interviewLongLatency").checked) params.set("long_latency", "true");
  return params.toString();
}

function bindCopyButtons() {
  document.querySelectorAll(".copy-id").forEach((button) => {
    button.addEventListener("click", (event) => {
      event.stopPropagation();
      navigator.clipboard?.writeText(button.title);
      button.textContent = "copied";
      setTimeout(() => {
        const id = button.title;
        button.textContent = id.length > 14 ? `${id.slice(0, 8)}...${id.slice(-4)}` : id;
      }, 900);
    });
  });
}

function parseKeys(value) {
  return value.split(",").map((item) => item.trim()).filter(Boolean);
}

async function request(path, options = {}) {
  const response = await fetch(`${state.apiHost}${path}`, {
    method: options.method || "GET",
    headers: {
      "Content-Type": "application/json",
      ...(options.auth === false ? {} : { Authorization: `Bearer ${state.token}` }),
    },
    body: options.body ? JSON.stringify(options.body) : undefined,
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.detail || data.error || `Request failed (${response.status})`);
  }
  return data;
}

function renderError(targetId, error) {
  $(targetId).innerHTML = `<p class="muted">${escapeHtml(error.message)}</p>`;
}

function markUpdated(value) {
  $("lastUpdated").textContent = `Updated ${formatDate(value || new Date().toISOString())}`;
}

function formatDate(value) {
  if (!value) return "n/a";
  return new Date(value).toLocaleString();
}

function formatDuration(seconds) {
  if (seconds === null || seconds === undefined || seconds === "") return "n/a";
  const value = Number(seconds);
  if (!Number.isFinite(value)) return "n/a";
  const minutes = Math.floor(value / 60);
  const remaining = Math.floor(value % 60);
  if (minutes < 60) return `${minutes}m ${remaining}s`;
  const hours = Math.floor(minutes / 60);
  return `${hours}h ${minutes % 60}m`;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}
