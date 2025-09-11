let rowVisibility = [];

function showAllRows() {
  const table = document.getElementById("table");
  const tr = table.getElementsByTagName("tr");

  for (let i = 1; i < tr.length; i++) {
    rowVisibility[i] = true;
  }
}

function searchForQuery(query) {
  const table = document.getElementById("table");
  const tr = table.getElementsByTagName("tr");

  for (let i = 1; i < tr.length; i++) {
    let row = tr[i].getElementsByTagName("td");
    let found = false;

    for (let j = 0; j < row.length; j++) {
      let item = row[j].textContent;
      if (item.toLowerCase().includes(query.toLowerCase())) {
        found = true;
        break;
      }
    }
    if (!found) {
      rowVisibility[i] = false;
    }
  }
}

function updateRows() {
  const table = document.getElementById("table");
  const tr = table.getElementsByTagName("tr");

  showAllRows();

  searchForQuery(document.getElementById("searchQuery").value);

  let z = 1;
  for (let i = 1; i < tr.length; i++) {
    if (rowVisibility[i]) {
      tr[i].style.display = "table-row";
      if (z % 2 == 1) {
        tr[i].style.backgroundColor = "rgb(221, 221, 221)";
      } else {
        tr[i].style.backgroundColor = "rgb(255, 255, 255)";
      }
      z++;
    } else {
      tr[i].style.display = "none";
    }
  }
}

const searchTerm = document.getElementById("searchQuery");
searchTerm.addEventListener("change", (e) => {
  updateRows();
});

updateRows();

// Set official
const officialButtons = document.querySelectorAll(".set-official");
officialButtons.forEach(button => {
  button.addEventListener("click", (e) => {
    e.preventDefault();

    let row = button.closest("tr");
    let id = row.id;
    let photo = row.getElementsByTagName("img")[0].src;
    let url = button.href;

    fetch("/update-official", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ id: id, photo: photo })
    })
    .then(res => res.json())
    .then(data => {
      window.location.href = url;
    });
  });
});
