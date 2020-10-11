window.addEventListener("load", () => {
    document.getElementById("submit")
        .addEventListener("click", () => {
            const form = document.querySelector("form")
            if(form.checkValidity()) {
                const div = document.createElement("div");
                div.classList.add("loader");
                form.after(div);
            }
        })
})