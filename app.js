function $(selector) {
  return document.querySelector(selector);
}

const data = window.dailyBrief;

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

  data.sections.forEach((section, sectionIndex) => {
    const sectionNode = sectionTemplate.content.firstElementChild.cloneNode(true);
    sectionNode.id = section.id;
    sectionNode.classList.add("reveal", `reveal-delay-${Math.min(sectionIndex, 2)}`);
    sectionNode.querySelector(".section-tag").textContent = section.tag;
    sectionNode.querySelector(".topic-section__title").textContent = section.title;
    sectionNode.querySelector(".topic-section__description").textContent = section.description;

    const grid = sectionNode.querySelector(".cards-grid");
    section.items.forEach((item) => {
      const card = cardTemplate.content.firstElementChild.cloneNode(true);
      card.querySelector(".news-card__priority").textContent = item.priority;
      card.querySelector(".news-card__time").textContent = item.time;
      card.querySelector(".news-card__title").textContent = item.title;
      card.querySelector(".news-card__summary").textContent = item.summary;
      card.querySelector(".news-card__impact").textContent = `影响观察：${item.impact}`;
      card.querySelector(".news-card__source").textContent = item.source;

      const link = card.querySelector(".news-card__link");
      link.href = item.url;

      grid.appendChild(card);
    });

    container.appendChild(sectionNode);
  });
}

renderMeta();
renderNav();
renderHighlights();
renderSections();
