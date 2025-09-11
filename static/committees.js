// Accordions
var acc = document.getElementsByClassName("accordion");
var i;

for (i = 0; i < acc.length; i++) {
  acc[i].addEventListener("click", function () {
    this.classList.toggle("active");

    var panel = this.nextElementSibling;
    if (panel.style.display === "block") {
      panel.style.display = "none";
    } else {
      panel.style.display = "block";
    }
  });
}

// Search
let itemVisibility = [];

function showAll() {
  const container = document.getElementById("all-committees");
  const items = container.getElementsByTagName("li");

  for (let i = 0; i < items.length; i++) {
    itemVisibility[i] = true;
  }
}

function searchForQuery(query) {
  const container = document.getElementById("all-committees");
  const items = container.getElementsByTagName("li");

  for (let i = 0; i < items.length; i++) {
    if (!(items[i].textContent.toLowerCase().includes(query.toLowerCase()))) {
      itemVisibility[i] = false;
    }
  }
}

function updateRows() {
  const container = document.getElementById("all-committees");
  const items = container.getElementsByTagName("li");

  showAll();

  searchForQuery(document.getElementById("searchQuery").value);

  for (let i = 0; i < items.length; i++) {
    if (itemVisibility[i]) {
      items[i].style.display = "list-item";
    } else {
      items[i].style.display = "none";
    }
  }
}

const searchTerm = document.getElementById("searchQuery");
searchTerm.addEventListener("change", (e) => {
  updateRows();
  var panel = document.getElementById("all-committees").parentElement;
  panel.style.display = "block";
  panel.previousElementSibling.classList.add("active");
});

updateRows();
