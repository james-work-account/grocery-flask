const formSubmit = $("#submit")
const form = $('form')

const ws_scheme = window.location.protocol == "https:" ? "wss://" : "ws://";
const url = `${ws_scheme}${document.domain}:${location.port}/socket`
const socket = io.connect(url)

socket.on('result', function(msg) {
    $('.results').append(`<h2>${msg.shop_name}</h2>` + msg.result);
});

socket.on('connection successful', function(msg) {
    console.log("connection successful")
});

socket.on('searching start', function(msg) {
    $(".results").empty();
    const div = document.createElement("div");
    div.classList.add("loader");
    form.after(div);
    return false;
});

socket.on('searching stop', function(msg) {
    Array.from(document.querySelectorAll(".loader")).forEach(loader => {
        loader.remove();
    });
    $('form *').prop('disabled', false);
    return false;
});

$('form').submit(function(event) {
    event.preventDefault()
    socket.emit('search', {data: $("#product").val()});
    $('form *').prop('disabled', true);
    return false;
});