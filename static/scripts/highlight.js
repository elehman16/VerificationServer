
// Check if A is a substring of B
function aContainsB (a, b) {
    return a.includes(b); // false; //a.indexOf(b) >= 0;
}

// Capitalize the first letter of the string.
function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

// Find the element in the list (elements) with no id.
function findNoID(elements) {
  for (var i = 0; i < elements.length; i++) {
    if (elements[i].id === "") {
      return elements[i];
    }
  }

  return -1;
}

function getLastVal(item) {
  var last = item.classList.value;
  var last_val = parseInt(last.substring(last.length - 1));
  return last_val;
}

/*
* Return the tags with class "highlighted1."
*/
function getHighlighted() {
  var highlighted = document.getElementsByClassName("highlight1");
  var copied = [];

  // copy it to a NON mutable list.
  for (var i = 0; i < highlighted.length; i++) {
    copied.push(highlighted[i]);
  }

  return copied;
}

// Highlight the given text with a given value (for darkness).
function highlight(text, value) {
   $('body').mark(text, {
    "element": "span",
    "className": "highlight" + value,
    "separateWordSearch": false,
    "ignorePunctuation": true,
    "diacritics": true,
    "acrossElements": true,
    "limiters": [".", ",", "!"],
    "exclude": ["Statistics"]
  });
}


// reset by highlighting everything
function reset(doct_reason) {
  for (var i = 0; i < doct_reason.length; i++) {
    highlight(doct_reason[i][1]);
  }
}

// Highlight for everyone
function highlight_all(doct_reason, can_highlight) {
  reset(doct_reason);
  for (var i = 0; i < doct_reason.length; i++) {
    var name = doct_reason[i][0];
    if (can_highlight[name]) {
      highlight(doct_reason[i][1], 1);
    }
  }
}
