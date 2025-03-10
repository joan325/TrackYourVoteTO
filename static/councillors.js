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

const fullRows = document.getElementsByTagName("tr");
Array.from(fullRows).slice(1).forEach(item => {
    item.addEventListener("mouseenter", function() {
        const fullName = item.getElementsByClassName("fullName")[0];
        if (fullName) {
            let button = document.createElement("a");
            button.textContent = "View voting history";
            button.setAttribute("href", "/motions-2022-2026/" + item.id);
            button.id = "votes_link";
            fullName.appendChild(button);
        }
    });

    item.addEventListener("mouseleave", function() {
        const button = item.querySelector("#votes_link");
        if (button) {
            button.remove();
        }
    });
});


updateRows();