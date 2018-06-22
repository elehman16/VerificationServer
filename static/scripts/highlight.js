
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
    if (str[(idx + 1)] == " " && str.length > idx + 2 && str[idx + 2] !== str[idx + 2].toLowerCase()) {

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

function data_dict_highlighting(doctors) {
    var data = {};
    var sentences = new Set();
    // for each doctor
    for (var i = 0; i < doctors.length; i++) {
      var doctor = doctors[i];
      var doct_name = doctor[0];
      var split_array = split(doctor[1]);

      // for each sentence
      split_array.some(function(elem) {
        var has_added = false;
        elem = elem.trim(" ");

        var loop_arr = Array.from(sentences).slice();

        // for each setence seen thus far
        loop_arr.some(function(str) {
          str = str.trim(" ");
          if (elem === str) {
            data[str].push(doct_name);
            has_added = true;
            return ;
          } else if (isSubstring(elem, str) && elem.length > 1) {
            var store_names = (data[str] || []).slice();
            var new_elem = str.split(elem);
            // for each element in the split up string
            new_elem.forEach(function(e) {
              if (e.length > 1) {
                data[e] = store_names.slice();
                sentences.add(e);
              }
            });

            // remove the old string and add in the new string
            data[str] = null;
            var tmp = store_names.slice();
            tmp.push(doct_name);
            data[elem] = tmp;
            sentences.delete(str);
            sentences.add(elem);
            has_added = true;
            return ;
          } else if (isSubstring(str, elem) && str.length > 1) {
            var store_names = (data[str] || []).slice();
            var new_elem = elem.split(str);

            // add the non-substring part into the map, and the dict
            new_elem.forEach(function(e) {
              e = e.trim(" ");
              // ensure that the length is reasonable
              // ensure that the split string hasn't been highlighted
              if (e.length > 1 && !(e in data)) {
                var list_names = data[e] || [];
                list_names.push(doct_name);
                data[e] = list_names;
                sentences.add(e);
              }
            });

            var tmp = store_names.slice();
            tmp.push(doct_name);
            data[str] = tmp;
            has_added = true;
            return;
          }

        });

        if (!(has_added)) {
          data[elem] = [doct_name];
          sentences.add(elem);
        }
      });
    }

    return [data, sentences];
}

// Highlight the given text with a given value (for darkness).
function highlight(text, value, names) {
   $('body').mark(text, {
    "element": "mark",
    "className": value,
    "separateWordSearch": false,
    "ignorePunctuation": true,
    "diacritics": true,
    "acrossElements": true,
    "each": function(node) {
        node.title = names;
        node.dataset.toggle = "tooltip";
        node.dataset.placement = "top";
    },
    "limiters": [".", ",", "!"],
    "exclude": ["statistic_content", ".ignore"]
  });
}

// reset by removing all highlighting instances
function reset() {
  for (var i = 1; i < 5; i++) {
    var h = Array.from(document.getElementsByClassName("highlight" + i));
    var h_ans = Array.from(document.getElementsByClassName("highlight_answer" + i));
    h.forEach(function(e) {
      $(e).contents().unwrap();
    });

    h_ans.forEach(function(e) {
      $(e).contents().unwrap();
    });
  }
}


// resets the answer and gets rid of any highlighting.
function reset_answer() {
  var e = document.getElementById("answer-key");
  var original_text = "";
  var children = e.children;
  while (e.children.length !== 0) {
    var c = e.children[0];
    original_text += c.innerText;
    e.removeChild(c);
    if (e.children.length != 0) {
      original_text += " ";
    }
  }

  e.innerHTML = original_text;
}

// Redo the highlighting
function redo() {
  // get data and reshape it
  var arr = document.getElementById("data-doct-reason").dataset.doct_reason.split("!!!");
  var newArr = [];
  while(arr.length) newArr.push(arr.splice(0, 2));

  // remove/add data from front
  var doct_selected = getDoctorSelected();
  for (var key in doct_selected) {
    if (doct_selected[key]) {
      document.getElementById("ans_" + key).style.display = "block";
      document.getElementById("res_" + key).style.display = "block";
    } else {
      document.getElementById("ans_" + key).style.display = "none";
      document.getElementById("res_" + key).style.display = "none";
    }
  }

  highlight_all(newArr, doct_selected);
  reset_answer(); // reset the answer key
}

// Highlight for everyone
function highlight_all(doct_reason, can_highlight) {
  reset();
  doct_reason = doct_reason.slice();

  // get the answer and put it into our list
  var ans = document.getElementById("answer-key").innerText;
  doct_reason.push(["Annotator 1", ans]);

  var tmp = data_dict_highlighting(doct_reason);
  var data = tmp[0];
  var set = tmp[1];

  // for each section of text that needs to be highlighted.
  set.forEach(function(elem) {
    var doct_hl = data[elem];
    // determine if we can highlight
    for (var key in can_highlight) {
      // if we can't highlight, then remove that name
      if (!(can_highlight[key])) {
        var index = doct_hl.indexOf(key);
        if (index > -1) {
          doct_hl.splice(index, 1);
        }
      }
    }

    // if there is nothing to highlight... don't even try...
    if (doct_hl.length !== 0) {
      if (doct_hl.indexOf("Annotator 1") !== -1) {
        highlight(elem, "highlight_answer" + doct_hl.length, doct_hl.join(', '));
      } else {
        highlight(elem, "highlight" + doct_hl.length, doct_hl);
      }
    }
  });

  // activates all tooltips
  $(function () {
    $('[data-toggle="tooltip"]').tooltip({
      container: 'body'
    })
  });
}
