async function fetchNewsData() {
  try {
    let response = await fetch("/data");
    let data = await response.json();

    let container = document.getElementById("news");
    container.innerHTML = "";

    data.forEach((item) => {
      let div = document.createElement("div");
      let motionsHtml = "";
      
      if (item.motion_referenced && item.motion_ids && item.motion_ids.length > 0) {
        motionsHtml = `<div style="margin-top: 10px; display: flex; flex-wrap: wrap; gap: 6px;">`;
        
        item.motion_ids.forEach(motionId => {
          motionsHtml += `<span style="display: inline-block; padding: 4px 8px; background: #e4e4e4; color: #236192; border-radius: 12px; font-size: 11px; font-weight: 500; margin-top: -5px; margin-bottom: 1em;">
                            <a href="https://secure.toronto.ca/council/agenda-item.do?item=${motionId}" target="_blank" style="color: #236192; text-decoration: none;">
                              ${motionId}
                            </a>
                          </span>`;
        });
        
        motionsHtml += `</div>`;
      }
      
      div.innerHTML = `<img src="${item.favicon}" style="display: inline; width: 1em; height: 1em; margin-bottom: 0;">
                            <a href="${item.link}" target="_blank"><h3 style="margin-bottom: 0; display: inline;">${item.title}</h3></a>
                            <p style="font-size: 12px; font-style: italic; margin-block: 4px;">${item.date}</p>
                            <p>${item.snippet}</p>
                            ${motionsHtml}`;
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
      
      if (info.comment) {
        div.insertAdjacentHTML("beforeend", `
          <div style="margin-top: 10px; text-align: center;">
            <button onclick="toggleComment(this)" style="background:rgb(255, 255, 255); border: 1px solid #ccc; padding: 4px 8px; border-radius: 4px; cursor: pointer; font-size: 12px; color: #666;">
              Councillor Comment
            </button>
            <div class="comment-content" style="display: none; margin-top: 8px; padding: 8px; background: #f9f9f9; border-left: 3px solid #236192; font-style: italic;">
              ${info.comment}
            </div>
          </div>`);
      }
      
      container.appendChild(div);

    }
  } catch (error) {
    console.error("Error fetching data:", error);
  }
}

function toggleComment(button) {
  const commentContent = button.nextElementSibling;
  const isHidden = commentContent.style.display === "none" || commentContent.style.display === "";
  
  commentContent.style.display = isHidden ? "block" : "none";
  button.textContent = isHidden ? "Hide Comment" : "Councillor Comment";
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
