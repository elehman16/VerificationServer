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
  var data = {};
  var ans = document.getElementById("answers").getElementsByTagName("input");
  var pv = document.getElementById("prompt-answer").getElementsByTagName("input");
  var num_annotators = 0;
  for (var i = 0; i < ans.length; i += 4) {
    data["Annotator " + num_annotators] = [ans[i].checked, ans[i + 2].checked];
    num_annotators++;
  }

  data["Prompt Validity"] = pv[0].checked;
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
                    "PromptID": document.getElementById("id").innerHTML,
                    "XML": document.getElementById("pmc").innerHTML,
                    "Label": JSON.stringify(get_data()),
                    "Outcome": document.getElementById("outcome").innerText,
                    "Intervention": document.getElementById("intervention").innerText,
                    "Comparator": document.getElementById("comparator").innerText});

}
