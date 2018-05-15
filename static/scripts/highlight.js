
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

// split multiple sentences into an array of sentences
function split(str) {
  var indices = [];
  for(var i=0; i<str.length;i++) {
      if (str[i] === ".") indices.push(i);
  }

  for (var i = 0; i < indices.length; i++) {
    var idx = indices[i];
    if (idx == str.length - 1) {
      return [str.substring(0, idx)];
    }

    // End of sentence?
    if (str[(idx + 1)] == " ") {
      var before = str.substring(0, idx);
      var after = str.substring(idx + 1);
      var tmp = split(after);
      tmp.splice(0, 0, before);
      return tmp;
    }
  }


  return [str];
}

// is str1 a substring of str2
function isSubstring(str1, str2) {
  return str2.indexOf(str1) !== -1;
}

function unnamed(doctors) {
    var data = {};
    var sentences = new Set();
    for (var i = 0; i < doctors.length; i++) {
      var doctor = doctors[i];
      var doct_name = doctor[0];
      var split_array = split(doctor[1]);
      // for each sentence
      split_array.forEach(function(elem) {
        var has_added = false;

        // for each setence seen thus far
        sentences.forEach(function(str) {
          if (elem == str) {
            data[str].append(doctor_name);
          } else if (isSubstring(elem, str)) {
            var store_names = data[str] || [];
            var new_elem = str.split(elem);
            // for each element in the split up string
            new_elem.forEach(function(e) {
              data[e] = store_names.splice(0);
              sentences.add(e);
            });

            // remove the old string and add in the new string
            data[str] = null;
            var tmp = store_names.splice(0);
            tmp.append(doctor_name);
            data[elem] = tmp;
            sentences.remove(str);
            sentences.add(elem);
            break;
          } else if (isSubstring(str, elem)) {
            new_elem = elem.split(str);

            // add the non-substring part into the map, and the dict
            new_elem.forEach(function(e) {
              var list_names = data[e] || [];
              list_names.append(doctor_name);
              data[e] = list_names;
              sentences.add(e);
            });

            var tmp = store_names.splice(0);
            tmp.append(doctor_name);
            data[str] = tmp;
            has_added = true;
            break;
          }
        });

        if (!(has_added)) {
          data[elem] = [doct_name];
        }
      });
    }

    return data;
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
