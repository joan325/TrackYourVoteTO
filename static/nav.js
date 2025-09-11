fetch("/nav")
.then(res => res.text())
.then(text => {
    let oldelem = document.querySelector("script#replace_with_navbar");
    let newelem = document.createElement("div");
    newelem.innerHTML = text;
    oldelem.parentNode.replaceChild(newelem,oldelem);

    // Clear official
    let button = document.getElementById("remove-official");
    if (button) {
      button.addEventListener("click", (e) => {
        e.preventDefault();
        
        let url = button.href;

        fetch("/update-official", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ id: "None", photo: "/static/images/Default.png" })
        })
        .then(res => res.json())
        .then(data => {
        window.location.href = url;
        });
      });
    }
  });