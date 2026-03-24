function $(selector) {
  return document.querySelector(selector);
}

const data = window.dailyBrief;

function formatSourceUrl(url) {
  try {
    const { hostname } = new URL(url);
    return hostname.replace(/^www\./, "");
  } catch {
    return url;
  }
}

function renderMeta() {
  $("#publish-date").textContent = data.publishDate;
}

function renderNav() {
  const nav = $("#topic-nav");
  const template = $("#nav-item-template");

  data.sections.forEach((section, index) => {
    const node = template.content.firstElementChild.cloneNode(true);
    node.href = `#${section.id}`;
    node.textContent = `${String(index + 1).padStart(2, "0")} ${section.title}`;
    nav.appendChild(node);
  });
}

function renderHighlights() {
  const container = $("#highlights");
  const template = $("#highlight-template");

  data.highlights.forEach((item, index) => {
    const node = template.content.firstElementChild.cloneNode(true);
    node.classList.add("reveal", `reveal-delay-${Math.min(index, 2)}`);
    node.querySelector(".highlight-card__topic").textContent = item.topic;
    node.querySelector(".highlight-card__title").textContent = item.title;
    node.querySelector(".highlight-card__summary").textContent = item.summary;
    container.appendChild(node);
  });
}

function renderSections() {
  const container = $("#topic-sections");
  const sectionTemplate = $("#section-template");
  const cardTemplate = $("#card-template");
  const briefTemplate = $("#brief-template");

  data.sections.forEach((section, sectionIndex) => {
    const sectionNode = sectionTemplate.content.firstElementChild.cloneNode(true);
    sectionNode.id = section.id;
    sectionNode.classList.add("reveal", `reveal-delay-${Math.min(sectionIndex, 2)}`);
    sectionNode.querySelector(".section-tag").textContent = section.tag;
    sectionNode.querySelector(".topic-section__title").textContent = section.title;
    sectionNode.querySelector(".topic-section__description").textContent = section.description;
    sectionNode.querySelector(".section-summary__chip--primary").textContent =
      `${(section.featured || []).length} 条重点内容`;
    sectionNode.querySelector(".section-summary__chip--secondary").textContent =
      `${(section.briefs || []).length} 条其他看点`;

    const grid = sectionNode.querySelector(".cards-grid");
    (section.featured || []).forEach((item) => {
      const card = cardTemplate.content.firstElementChild.cloneNode(true);
      card.querySelector(".news-card__priority").textContent = item.priority;
      card.querySelector(".news-card__time").textContent = item.time;
      card.querySelector(".news-card__summary").textContent = item.summary;
      card.querySelector(".news-card__impact").textContent = `影响观察：${item.impact}`;
      card.querySelector(".news-card__source").textContent = item.source;

      const titleLink = card.querySelector(".news-card__title-link");
      titleLink.href = item.url;
      titleLink.textContent = item.title;

      const sourceUrl = card.querySelector(".news-card__source-url");
      sourceUrl.href = item.url;
      sourceUrl.textContent = formatSourceUrl(item.url);

      const link = card.querySelector(".news-card__link");
      link.href = item.url;

      grid.appendChild(card);
    });

    const briefsList = sectionNode.querySelector(".briefs-list");
    (section.briefs || []).forEach((item) => {
      const brief = briefTemplate.content.firstElementChild.cloneNode(true);
      brief.querySelector(".brief-item__badge").textContent = `看点 ${String(
        (section.featured || []).length + briefsList.childElementCount + 1
      ).padStart(2, "0")}`;
      brief.querySelector(".brief-item__text").textContent = item.text;
      brief.querySelector(".brief-item__source").textContent = item.source;

      const briefLink = brief.querySelector(".brief-item__link");
      briefLink.href = item.url;

      briefsList.appendChild(brief);
    });

    container.appendChild(sectionNode);
  });
}

renderMeta();
renderNav();
renderHighlights();
renderSections();
