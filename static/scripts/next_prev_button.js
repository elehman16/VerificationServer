// Set up the next/prev button
function findX(next_prev) {
  var current = "{{ artid }}";
  var ordering = document.getElementById("data-ordering").dataset.ordering;
  var location = "";

  for (var i = 0; i < ordering.length; i++) {
    if (current == ordering[i]) {

      return ordering[i + next_prev];
    }
  }

  return "";
}

function next() {
  var next_loc = findX(1);
  window.location.replace("http://127.0.0.1:5000/annotate_full/" + next_loc);
}

function previous() {
  var prev_loc = findX(-1);
  window.location.replace("http://127.0.0.1:5000/annotate_full/" + prev_loc);
}

// This script is going to blur out the id for this page
var element = document.getElementById(document.getElementById("artid").dataset.id);
element.classList += "isDisabled";

var current = document.getElementById("artid").dataset.id;
var ordering = document.getElementById("data-ordering").dataset.ordering;

// disable the next previous buttons if we are first or last
if (ordering.length > 0 && current == ordering[0]) {
  element = document.getElementById("previous-but");
  element.classList += "isDisabled";
  element.style.visibility = 'hidden';
}

if (ordering.length > 0 && current == ordering[ordering.length - 1]) {
  element = document.getElementById("next-but");
  element.classList += "isDisabled";
  element.style.visibility = 'hidden';
}
