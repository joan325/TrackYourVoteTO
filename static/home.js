async function fetchData() {
    try {
        let response = await fetch('/data');
        let data = await response.json();

        let container = document.getElementById("news");
        container.innerHTML = "";

        data.forEach(item => {
            let div = document.createElement("div");
            div.innerHTML = `<a href="${item.link}" target="_blank"><h3>${item.title}</h3></a>
                            <p style="font-size: 12px; font-style: italic; padding-top: 0;">${item.date}</p>
                            <p>${item.snippet}</p>`;
            container.appendChild(div);
        });
    } catch (error) {
        console.error("Error fetching data:", error);
    }
}

document.addEventListener("DOMContentLoaded", fetchData);