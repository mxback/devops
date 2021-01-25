/**
* Theme: Velonic Admin Template
* Author: Coderthemes
* Module/App: Dashboard Application
*/

!function($) {
    "use strict";

    var Dashboard = function() {
        this.$body = $("body")
    };

    //initializing various charts and components
    Dashboard.prototype.init = function() {
        /**
        * Morris charts
        */

         
        //Line chart
        Morris.Area({
            element: 'morris-area-example',
            lineWidth: 0,
            data: [
                { y: '01', a: 75},
                { y: '02', a: 50} ,
                { y: '03', a: 60},
                { y: '04', a: 75},
                { y: '05', a: 50},
                { y: '06', a: 95},
                { y: '07', a: 50},
                { y: '08', a: 75},
                { y: '09', a: 20}
            ],
            xkey: 'y',
            ykeys: ['a'],
            labels: ['活跃用户数'],
            resize: true,
            pointSize: 0,
            smooth: true,
            fillOpacity: 0.7,
            hideHover: 'auto',
            gridLineColor: '#eef0f2',
            lineColors: ['#ebc142']
        });

        //Bar chart
        Morris.Bar({
            element: 'morris-bar-example',
            data: [
                    { y: 'Day1', a: 75,  b: 65 , c: 20 },
                    { y: 'Day2', a: 50,  b: 40 , c: 50 },
                    { y: 'Day3', a: 75,  b: 65 , c: 95 },
                    { y: 'Day4', a: 50,  b: 40 , c: 22 },
                    { y: 'Day5', a: 75,  b: 65 , c: 56 }
            ],
            xkey: 'y',
            ykeys: ['a', 'b', 'c'],
            labels: ['Series A', 'Series B', 'Series C'],
            gridLineColor: '#eef0f2',
            barSizeRatio: 0.5,
            numLines: 6,
            barGap: 6,
            resize: true,
            hideHover: 'auto',
            barColors: ['#ebc142', '#03a9f4', '#009688']
        });


        //Chat application -> You can initialize/add chat application in any page.
        $.ChatApp.init();
    },
    //init dashboard
    $.Dashboard = new Dashboard, $.Dashboard.Constructor = Dashboard
    
}(window.jQuery),

//initializing dashboad
function($) {
    "use strict";
    $.Dashboard.init()
}(window.jQuery);



