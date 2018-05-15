// Load google charts
google.charts.load('current', {'packages':['corechart']});
google.charts.setOnLoadCallback(drawChart);

// Draw the chart and set the chart values
function drawChart() {
  var arr = document.getElementById("data-pie").dataset.pie.split(',').slice();

  var doct_answer = [];
  while(arr.length) doct_answer.push(arr.splice(0,2));
  for (var i = 1; i < doct_answer.length; i++) {
    doct_answer[i][1] = parseInt(doct_answer[i][1]);
  }

  var data = google.visualization.arrayToDataTable(doct_answer);

  // Optional; add a title and set the width and height of the chart
  var options = {'title':'Doctor Response', 'width':550, 'height':400};

  // Display the chart inside the <div> element with id="piechart"
  var chart = new google.visualization.PieChart(document.getElementById('piechart'));
  chart.draw(data, options);
}
