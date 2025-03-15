import Utils from './modules/utils.js';
import WarpModal from './modules/modal.js';
import {TabulatorFull as Tabulator} from 'tabulator-tables';
import "./css/tabulator/tabulator_materialize.scss";
import Chart from 'chart.js/auto'


function downloadStatistics(statistics) {
    var url = window.warpGlobals.URLs['getStatistics'];

    Utils.xhr.get(url, {toastOnSuccess:false})
    .then( function(v) {
      const data = v.response.data;

        // echo(v.response);
      new Chart(
        document.getElementById('myChart'),
        {
          type: 'bar',
          data: {
            labels: data.map(row => row.date),
            datasets: [
              {
                label: 'Bookings per day',
                data: data.map(row => row.count)
              }
            ]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false
          }
        }
      );
    
    })
}


document.addEventListener("DOMContentLoaded", function(e) {
    const statistics = document.getElementById("statistics");
    downloadStatistics(statistics);
});
