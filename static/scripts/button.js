/**
* A button that enables the submit button on click.
*/
function enable_submit() {
  if (all_checked()) {
    document.getElementById("submit-but").disabled = false;
  }
}

/**
* Gets the data from the inputs and puts them into a dictionary.
*/
function get_data() {
  var ans = document.getElementById("answers").getElementsByTagName("input");
  var names = document.getElementById("data-names").dataset.names.split(",");
  names.splice(0, 0, "Annotator 1"); // insert into the beginning of the array

  var data = {};
  var pv = document.getElementById("prompt-answer").getElementsByTagName("input");
  data["Prompt Validity"] = pv[0].checked;

  var who = 0; // each person has 4 inputs associated with it
  var names_count = 0;
  for (var i = 0; i < ans.length; i += 2) {
    if (who == 0) {
      data[names[names_count] + " answer"] = ans[i].checked;
    }

    if (who == 1) {
      data[names[names_count] + " reasoning"] = ans[i].checked;
    }

    who += 1;
    if (who == 2) {
      who = 0;
      names_count += 1
    }
  }

  return data;
}

// Determines if all pairs are checked off.
function all_checked() {
  var ans = document.getElementById("answers").getElementsByTagName("input");
  var pmt = document.getElementById("prompt-answer").getElementsByTagName("input");
  var all_checked = (pmt[0].checked || pmt[1].checked);
  for (var i = 0; i < ans.length; i += 2) {
    all_checked = all_checked && (ans[i].checked || ans[i + 1].checked);
  }

  return all_checked;
}

/**
* The submission button.
*/
function submit_final() {
  post("/submit/", {"userid": document.getElementById("userid").innerHTML,
                    "Doctors Reviewed": document.getElementById("data-names").dataset.names,
                    "PromptID": document.getElementById("artid").innerHTML,
                    "XML": document.getElementById("pmc").innerHTML,
                    "Label": JSON.stringify(get_data()),
                    "Outcome": document.getElementById("outcome").innerText,
                    "Intervention": document.getElementById("intervention").innerText,
                    "Comparator": document.getElementById("comparator").innerText});

}
