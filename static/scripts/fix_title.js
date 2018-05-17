// The goal of this script is to fix the title situation... If there is an
// apostrophe, we cannot open the text.

var elements = document.getElementsByClassName("tablinks");
var elem = Array.from(elements);
for (var i = 0; i < elem.length; i++) {
  var e = elem[i];
  if (e.innerHTML.indexOf("&#39") != -1 || e.innerHTML.indexOf("'") != -1) {
    // remove their content
    $(e).remove();
  }
}
