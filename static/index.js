const formSubmit = document.getElementById("submit")
const checkForm = (form) => {
    if(form.checkValidity()) {
        const div = document.createElement("div");
        div.classList.add("loader");
        form.after(div);
        formSubmit.disabled = true;
        // formSubmit.submit();
    }
}