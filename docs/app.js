(() => {
  "use strict";

  const { repo, updated, categories, skills } = window.SKILLS_CATALOG;
  const byId = id => document.getElementById(id);
  const repoUrl = "https://github.com/" + repo;
  const clone = "git clone " + repoUrl + ".git";
  const names = new Map(categories.map(category => [category.id, category.label]));
  const cards = new Map();
  const chips = new Map();
  const installers = [];
  let selected = "";
  let platform = "mac";

  function element(tag, className, value) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (value !== undefined) node.textContent = value;
    return node;
  }

  function fallbackCopy(value) {
    const previous = document.activeElement;
    const field = element("textarea", "sr");
    field.value = value;
    field.readOnly = true;
    document.body.append(field);
    try {
      field.select();
      return document.execCommand("copy");
    } finally {
      field.remove();
      previous.focus({ preventScroll: true });
    }
  }

  function command(box, value, label) {
    const code = element("code", "", value);
    const button = element("button", "", "Copy");
    button.type = "button";
    button.setAttribute("aria-label", "Copy " + label);
    let timer;
    button.addEventListener("click", async () => {
      let copied = false;
      try {
        await navigator.clipboard.writeText(code.textContent);
        copied = true;
      } catch {
        try { copied = fallbackCopy(code.textContent); } catch { copied = false; }
      }
      clearTimeout(timer);
      button.textContent = copied ? "Copied" : "Select text";
      byId("copy-status").textContent = copied ? "Copied " + label + "." : "Select the command and copy it manually.";
      if (!copied) {
        const range = document.createRange();
        range.selectNodeContents(code);
        const selection = window.getSelection();
        selection.removeAllRanges();
        selection.addRange(range);
      }
      timer = setTimeout(() => { button.textContent = "Copy"; }, 1800);
    });
    box.append(code, button);
    return code;
  }

  function installer(container, commands, label) {
    const group = element("div", "platforms");
    group.setAttribute("role", "group");
    group.setAttribute("aria-label", "Operating system for " + label);
    const box = element("div", "command");
    const code = command(box, commands[platform], label + " install command");
    const buttons = [];
    for (const [key, title] of [["mac", "Mac/Linux"], ["win", "Windows"]]) {
      const button = element("button", "", title);
      button.type = "button";
      button.setAttribute("aria-pressed", String(platform === key));
      button.addEventListener("click", () => {
        platform = key;
        installers.forEach(update => update());
      });
      buttons.push([key, button]);
      group.append(button);
    }
    installers.push(() => {
      code.textContent = commands[platform];
      for (const [key, button] of buttons) button.setAttribute("aria-pressed", String(platform === key));
    });
    container.append(group, box);
  }

  function list(items, asCode = false) {
    const ul = element("ul");
    for (const item of items) {
      const li = element("li");
      li.append(asCode ? element("code", "", item) : item);
      ul.append(li);
    }
    return ul;
  }

  function makeCard(skill) {
    const card = element("details", "card");
    card.id = "skill-" + skill.name;
    const summary = element("summary");
    const body = element("span", "card-body");
    const title = element("span");
    title.append(element("span", "category", names.get(skill.category)), element("span", "card-title", skill.title),
      element("code", "identifier", skill.name));
    const description = element("span", "", skill.summary);
    description.append(element("span", "audience", "For: " + skill.for));
    const expand = element("span", "expand");
    expand.setAttribute("aria-hidden", "true");
    body.append(title, description);
    summary.append(body, expand);

    const detail = element("div", "detail");
    const fields = element("dl", "fields");
    function field(label, content) {
      const pair = element("div");
      const dd = element("dd");
      dd.append(content);
      pair.append(element("dt", "detail-label", label), dd);
      fields.append(pair);
    }
    field("When to use it", skill.when);
    field("What you need", list(skill.needs));
    field("Make it your own", skill.customize);
    field("Try this prompt", skill.try);
    field("Included files", list(skill.files, true));
    if (skill.license) field("License", skill.license);
    if (skill.conflicts.length) field("Choose one", "Use this skill or " + skill.conflicts.join(", ") + ".");
    detail.append(fields, element("h3", "", "Install this skill"));
    installer(detail, skill.install, skill.name);
    const link = element("a", "text-link", "View skill on GitHub ↗");
    link.href = repoUrl + "/tree/main/skills/" + encodeURIComponent(skill.name);
    detail.append(element("p", "manual", skill.install.manual), link);
    card.append(summary, detail);
    cards.set(skill.name, card);
    byId("cards").append(card);
  }

  function applyFilters() {
    const terms = byId("query").value.trim().toLowerCase().split(/\s+/).filter(Boolean);
    let count = 0;
    for (const skill of skills) {
      const haystack = [skill.name, skill.title, skill.summary, skill.for, skill.when].join(" ").toLowerCase();
      const visible = (!selected || skill.category === selected) && terms.every(term => haystack.includes(term));
      cards.get(skill.name).hidden = !visible;
      if (visible) count++;
    }
    for (const [id, button] of chips) button.setAttribute("aria-pressed", String(id === selected));
    byId("count").textContent = count + " of " + skills.length + (skills.length === 1 ? " skill" : " skills");
    byId("empty").hidden = count !== 0;
  }

  function clearFilters(category = "") {
    selected = category;
    byId("query").value = "";
    applyFilters();
  }

  function addChip(id, title, count) {
    const chip = element("button", "", title);
    chip.type = "button";
    chip.append(element("small", "", count));
    chip.addEventListener("click", () => { selected = id; applyFilters(); });
    byId("filters").append(chip);
    chips.set(id, chip);
  }

  function openSkill(hash, focus = false) {
    if (!hash.startsWith("#skill-")) return;
    const card = cards.get(hash.slice(7));
    if (!card) return;
    if (card.hidden) clearFilters();
    card.open = true;
    if (focus) card.querySelector("summary").focus({ preventScroll: true });
    card.scrollIntoView({ block: "start" });
  }

  command(byId("hero-clone"), clone, "clone command");
  command(byId("install-clone"), clone, "clone command");
  installer(byId("local-install"), { mac: "./install.sh a b", win: ".\\install.ps1 a b" }, "selected skills");
  const date = byId("updated");
  date.dateTime = updated;
  date.textContent = new Intl.DateTimeFormat("en", { month: "long", day: "numeric", year: "numeric", timeZone: "UTC" })
    .format(new Date(updated + "T00:00:00Z"));

  const starters = skills.filter(skill => skill.start_here);
  for (const skill of starters) {
    const link = element("a", "starter-link", skill.title);
    const arrow = element("span", "arrow", "↘");
    arrow.setAttribute("aria-hidden", "true");
    link.append(arrow);
    link.href = "#skill-" + skill.name;
    link.addEventListener("click", () => openSkill(link.hash, true));
    byId("starter-list").append(link);
  }
  const pairs = new Set();
  for (const skill of starters) {
    for (const other of skill.conflicts) {
      const key = [skill.name, other].sort().join("|");
      if (pairs.has(key)) continue;
      pairs.add(key);
      const note = element("p", "", "Pick one session routine, not both: ");
      note.append(element("code", "", "session-refresh"),
        " keeps one main session all day and works well from your phone; ",
        element("code", "", "session-handoff-60"),
        " starts a fresh session each time context reaches 60%. If unsure, start with session-refresh.");
      byId("choice").append(note);
    }
  }

  if (starters.some(skill => skill.name === "mac-mini-station-setup")) {
    byId("choice").append(element("p", "", "The station setup guide is for Macs. On Windows, keep the laptop plugged in, "
      + "turn off sleep in Settings, System, Power, and install the other starters."));
  }

  addChip("", "All skills", skills.length);
  byId("shelf-count").textContent = skills.length + " skills";
  for (const category of categories) {
    const count = skills.filter(skill => skill.category === category.id).length;
    addChip(category.id, category.label, count);
    const book = element("a", "book", category.label);
    book.append(element("small", "", String(count).padStart(2, "0")));
    book.href = "#catalog";
    book.setAttribute("aria-label", category.label + ", " + count + " skills");
    book.addEventListener("click", () => {
      clearFilters(category.id);
      chips.get(category.id).focus({ preventScroll: true });
    });
    byId("books").append(book);
  }
  skills.forEach(makeCard);
  byId("query").addEventListener("input", applyFilters);
  byId("reset").addEventListener("click", () => { clearFilters(); byId("query").focus(); });
  window.addEventListener("hashchange", () => openSkill(location.hash));
  applyFilters();
  openSkill(location.hash);
  if (window.matchMedia("(prefers-reduced-motion: no-preference)").matches) {
    byId("books").animate([{ opacity: .55, transform: "translateY(5px)" }, { opacity: 1, transform: "none" }],
      { duration: 350, easing: "ease-out" });
  }
})();
