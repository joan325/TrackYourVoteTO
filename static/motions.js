let rowVisibility = [];

function showAllRows() {
  const table = document.getElementById("table");
  const tr = table.getElementsByTagName("tr");

  for (let i = 1; i < tr.length; i++) {
    rowVisibility[i] = true;
  }
}

function searchDate(dates) {
  const table = document.getElementById("table");
  const tr = table.getElementsByTagName("tr");

  for (let i = 1; i < tr.length; i++) {
    let td_date = new Date(tr[i].getElementsByTagName("td")[2].textContent);

    if (td_date) {
      if (td_date > dates[1] || td_date < dates[0]) {
        rowVisibility[i] = false;
      }
    }
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

const motionsCal = flatpickr("#calendar", {
  enableTime: false,
  dateFormat: "Y-m-d",
  minDate: "2022-11-23",
  maxDate: "today",
  mode: "range",
  inline: true,

  onValueUpdate: function () {
    updateRows();
  },
});

function updateRows() {
  const table = document.getElementById("table");
  const tr = table.getElementsByTagName("tr");
  const calendar = document.querySelector("div.flatpickr-calendar");

  showAllRows();

  if (dateChecked) {
    calendar.style.display = "block";
    searchDate(motionsCal.selectedDates);
  } else {
    calendar.style.display = "none";
  }

  if (searchQueryChecked) {
    searchForQuery(document.getElementById("searchQuery").value);
  }

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

var searchQueryChecked = false;
const viewBySearchQuery = document.getElementById("bySearchQuery");
viewBySearchQuery.addEventListener("change", (e) => {
  searchQueryChecked = !searchQueryChecked;
  updateRows();
});

const searchTerm = document.getElementById("searchQuery");
searchTerm.addEventListener("change", (e) => {
  updateRows();
});

var dateChecked = false;
const viewByDate = document.getElementById("byDate");
viewByDate.addEventListener("change", (e) => {
  dateChecked = !dateChecked;
  updateRows();
});

updateRows();

let button = document.getElementById("set-official");
    if (button) {
      button.addEventListener("click", (e) => {
        e.preventDefault();
        
        let url = button.href;
        let id = button.className;
        let photo = button.previousElementSibling.src;

        fetch("/update-official", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ id: id, photo: photo })
        })
        .then(res => res.json())
        .then(data => {
        window.location.href = url;
        });
      });
    }
