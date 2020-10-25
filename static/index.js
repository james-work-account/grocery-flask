const formSubmit = $("#submit");
const form = $("form");
const searchPrompt = $("#search-prompt");

const ws_scheme = window.location.protocol == "https:" ? "wss://" : "ws://";
const url = `${ws_scheme}${document.domain}:${location.port}/socket`;
const socket = io.connect(url);

socket.on("result", function (msg) {
  $(".results").append(`<h2>${msg.shop_name}</h2>` + msg.result);
  $("#results-found").html(msg.shop_number);
});

socket.on("connection successful", function (msg) {
  console.log("connection successful");
});

socket.on("searching start", function (msg) {
  $(".results").empty();
  const div = document.createElement("div");
  div.classList.add("loader");
  form.after(div);
  if ($("#searching-text").length === 0) {
    const searchingText = `<h2 id="searching-text">Search complete: <strong><span id="results-found">0</span>/<span id="total-results">${msg.search_length}</span></strong></h2>`;
    form.after($(searchingText));
  }
  searchPrompt.addClass("display-none");
  return false;
});

socket.on("searching stop", function (msg) {
  $(".loader").remove();
  $("#searching-text").remove();
  searchPrompt.removeClass("display-none");
  $("form *").prop("disabled", false);
  return false;
});

$("form").submit(function (event) {
  event.preventDefault();
  socket.emit("search", { data: $("#product").val() });
  $("form *").prop("disabled", true);
  return false;
});
