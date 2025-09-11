async function fetchNewsData() {
  try {
    let response = await fetch("/data");
    let data = await response.json();

    let container = document.getElementById("news");
    container.innerHTML = "";

    data.forEach((item) => {
      let div = document.createElement("div");
      div.innerHTML = `<img src="${item.favicon}" style="display: inline; width: 1em; height: 1em; margin-bottom: 0;">
                            <a href="${item.link}" target="_blank"><h3 style="margin-bottom: 0; display: inline;">${item.title}</h3></a>
                            <p style="font-size: 12px; font-style: italic; margin-block: 4px;">${item.date}</p>
                            <p style="margin-top: 10px;">${item.snippet}</p>`;
      container.appendChild(div);
    });
  } catch (error) {
    console.error("Error fetching data:", error);
  }
}

async function fetchHighlightData() {
  try {
    let response = await fetch("/official-highlights/None");
    let data = await response.json();

    let container = document.getElementById("official-highlights");
    container.innerHTML = "";

    data.forEach((item) => {
      let div = document.createElement("div");
      div.innerHTML = `<img src="${item.favicon}" style="display: inline; width: 1em; height: 1em; margin-bottom: 0;">
                            <a href="${item.link}" target="_blank"><h3 style="margin-bottom: 0; display: inline;">${item.title}</h3></a>
                            <p style="font-size: 12px; font-style: italic; margin-block: 4px;">${item.date}</p>
                            <p style="margin-top: 10px;">${item.snippet}</p>`;
      container.appendChild(div);
    });
  } catch (error) {
    console.error("Error fetching data:", error);
  }
}

async function fetchVoteHighlightData() {
  try {
    let name = document.getElementById("official-highlights-votes").dataset.name;
    let motions = JSON.parse(document.getElementById("official-highlights-votes").dataset.motions);
    let response = await fetch("in-the-news");
    let data = await response.json();

    let container = document.getElementById("official-highlights-votes");
    container.innerHTML = "";

    for (const [motionId, info] of Object.entries(data)) {

      const [vote, result, date] = motions[motionId];
      const voteColour = vote === "Yes"
        ? "green"
        : vote === "No"
          ? "red"
          : "grey";
      const resultColour = result.includes("Carried")
        ? "green"
        : result.includes("Lost")
          ? "red"
          : "grey";

      let div = document.createElement("div");
      div.innerHTML = `
        <h3><a href="https://secure.toronto.ca/council/agenda-item.do?item=${motionId}">${info.name}</a></h3>
        <p class="${voteColour}">Vote: ${vote}</p>
        <p class="${resultColour}">${result}</p>`
      div.className = "vote-item";
      info.articles.forEach(article => {
        div.insertAdjacentHTML("beforeend", `
          <div class="article-link">
            <img class="favicon" src=${article.favicon}>
            <a href="${article.link}" target="_blank">${article.title}</a>
          </div>`);
      });
      container.appendChild(div);

    }
  } catch (error) {
    console.error("Error fetching data:", error);
  }
}

function toggleCommittees() {
  const hiddenItems = document.querySelectorAll("#committee-expand .hidden-committee");
  const btn = document.getElementById("see-more-btn");
  const isHidden = hiddenItems[0].style.display === "" || hiddenItems[0].style.display === "none";

  hiddenItems.forEach(item => {
    item.style.display = isHidden ? "list-item" : "none";
  });

  btn.textContent = isHidden ? "See less" : "See more";
}

// hide on load
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("#committee-expand .hidden-committee").forEach(item => {
    item.style.display = "none";
  });
});

document.addEventListener("DOMContentLoaded", fetchNewsData);
document.addEventListener("DOMContentLoaded", fetchVoteHighlightData);
document.addEventListener("DOMContentLoaded", fetchHighlightData);
