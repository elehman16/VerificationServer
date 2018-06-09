/**
* Displays the information in the tab when clicked on.
*
* @param evt represents what happend with the tab.
* @param name represents which tab to open.
*/
function openTab(evt, name) {
    var i, tabcontent, tablinks;
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }

    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }
    document.getElementById(name).style.display = "block";
    evt.currentTarget.className += " active";
}

/**
* Used to break down a Text into a readable format (see data-definition below).
*
* @param orig_tab represents the parent HTML element if it exists.
* @param text is of the following data definition:
* Text is one of:
*    - Array of Text
*    - ['title', 'paragraph']
*    - ['title', Text]
*/
function breakDownText(text, orig_tab) {
  var copy = orig_tab;
  if (text.length != 2 || Array.isArray(text[0])) { // there are multiple sections here if this is the case
    for (var i = 0; i < text.length; i++) {
      breakDownText(text[i], orig_tab); // break each of these larger sections down
    }                                  // this is likely the beginnining with all tab headers
  } else {
    if (orig_tab === undefined) { // If there is no title for this section, make one.
      var title = text[0];
      var tab = document.getElementById(title);
      var title_element = document.createElement("h3");
      title_element.innerHTML = title;
      tab.appendChild(title_element);
      orig_tab = tab;
    }

    if (Array.isArray(text[1])) { // If there is a sub-section under this section, break it down
      breakDownText(text[1], orig_tab);
    } else { // otherwise add to it
      if (copy !== undefined) {
        var title = text[0];
        var title_element = document.createElement("h4");
        title_element.innerHTML = title;
        orig_tab.appendChild(title_element);
      }

      var text_element = document.createElement("p");
      text_element.innerHTML = text[1];
      orig_tab.appendChild(text_element);
    }
  }

}

/**
* Get the list of doctor names.
*
*/
function getDoctorSelected() {
  var doctors_selected = document.getElementById("data-names");
  return doctors_selected.dataset.names.split(",");
}
