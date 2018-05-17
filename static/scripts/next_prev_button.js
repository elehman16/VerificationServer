// Set up the next/prev button
function findX(next_prev) {
  var current = parseInt(document.getElementById("artid").dataset.id);
  var ordering = eval("[" + document.getElementById("data-ordering").dataset.ordering + "]");
  var location = "";

  for (var i = 0; i < ordering.length; i++) {
    if (current == ordering[i] && ((i + next_prev) !== ordering.length) && ((i + next_prev) > -1)) {
      debugger;
      return ordering[i + next_prev];
    }
  }

  return "";
}

function next() {
  var next_loc = findX(1);
  if ("" !== next_loc) {
    //http://127.0.0.1:5000/annotate_full/
    window.location.replace("http://ec2-18-219-1-213.us-east-2.compute.amazonaws.com:8084/annotate_full/" + next_loc);
  }
}

function previous() {
  var prev_loc = findX(-1);
  if ("" !== prev_loc) {
    window.location.replace("http://ec2-18-219-1-213.us-east-2.compute.amazonaws.com:8084/annotate_full/" + prev_loc);
  }
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
