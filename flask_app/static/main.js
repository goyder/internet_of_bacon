$(function() {
    console.log(debug_mode);
    console.log('jquery is working!');
    createGraph();

});

/* Further work to be done:
Strip out this file into settings, a creation call, and update calls. - Done
Add a date-time picker. - Done
Add a button that allows us to edit the date-times. - Kinda done
Set date limits based on what data is in the database.
*/

// Retrieve start and end dates
var parseTime = d3.timeParse("%Y-%m-%d %H:%M:%S");
var earliest_datetime   = parseTime($("#earliest_date")[0].innerText),
    latest_datetime     = parseTime($("#latest_date")[0].innerText);

jQuery('#datetime-selector').datetimepicker({
    format:         "Y-m-d H:i:s",
    formatDate:     "Y-m-d",
    minDate:        earliest_datetime,
    maxDate:        latest_datetime,
    inline:         true,
    defaultDate:    new Date(latest_datetime.getTime()),
    onGenerate:     function() {
        $("#datetime-selector")[0].value = latest_datetime;
    }
});

// Set frame limits for graph
var frame_width     = 600,
    frame_height    = 480,
    format          = d3.format(",d"),
    margin          = {top: 20, right: 70, bottom: 50, left: 70},
    width           = frame_width - margin.right - margin.left,
    height          = frame_height - margin.top - margin.bottom;

if (debug_mode) {
    var data_source = "/test_data"
} else {
    var data_source = "/data"
}


// Develop legend
var color_hash = { 0 : ["Temperature (C)", "steelblue"],
                   1 : ["Humidity (%)", "red"]
                   }

var x = d3.scaleTime()
    .rangeRound([0, width]);
var y = d3.scaleLinear()
    .rangeRound([height, 0]); // Note that height goes first
var y2 = d3.scaleLinear()
    .rangeRound([height, 0]);
var line = d3.line()
    .x(function(d) { return x(d.Datetime); })
    .y(function(d) { return y(d.Value); });
var line2 = d3.line()
    .x(function(d) { return x(d.Datetime); })
    .y(function(d) { return y2(d.Value); });


function createGraph() {

    // Develop graph container
    var svg = d3.select("#graph_container").append("svg")
        .attr("width", frame_width)
        .attr("height", frame_height)
        .attr("class", "monitor");

    // Develop graph
    var g = svg.append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    // Develop legend
	var legend = svg.append("g")
	  .attr("class", "legend")
	  .attr("x", width - 65)
	  .attr("y", 50)
	  .attr("height", 100)
	  .attr("width", 100);

	legend.selectAll('g').data([1,2])
      .enter()
      .append('g')
      .each(function(d, i) {
        var g = d3.select(this);
        g.append("rect")
          .attr("x", width - 65)
          .attr("y", i*25 + 19)
          .attr("width", 10)
          .attr("height", 10)
          .style("fill", color_hash[String(i)][1]);

        g.append("text")
          .attr("x", width - 50)
          .attr("y", i * 25 + 30)
          .attr("height",30)
          .attr("width",100)
          .style("fill", color_hash[String(i)][1])
          .text(color_hash[String(i)][0]);
      });

    // Develop axis labels
    g.append("text")
        .attr("class", "y-axis label")
        .attr("text-anchor", "middle")
        .attr("transform", "rotate(-90)")
        .attr("x", -height/2)
        .attr("y", width + 40)
        .text("Humidity (%)");

    g.append("text")
        .attr("class", "y-axis label")
        .attr("text-anchor", "middle")
        .attr("transform", "rotate(-90)")
        .attr("x", -height/2)
        .attr("y", -40)
        .text("Temperature (deg C)");

    g.append("text")
        .attr("class", "x-axis label")
        .attr("text-anchor", "middle")
        .attr("x", width/2)
        .attr("y", height +  40)
        .text("Date-time");

    // Call the data - initially
    d3.csv(
    data_source,
    function(d) {
        d.Datetime = parseTime(d.Datetime);
        d.Value = +d.Value;
        return d;
        },
    function(error, data) {
        if (error) throw error;

        x.domain(d3.extent(data, function(d) { return d.Datetime; }));
        y.domain(d3.extent(data, function(d) {
            if (d.ID == "Temperature")
                {return d.Value; } else
                {return null;}
            }));
        y2.domain(d3.extent(data, function(d) {
            if (d.ID == "Humidity")
                {return d.Value; } else
                {return null; }
            }));

        g.append("g")
            .attr("transform", "translate(0," + height + ")")
            .attr("id", "x-axis")
            .call(d3.axisBottom(x));

        g.append("g")
            .attr("id", "left-y-axis")
            .call(d3.axisLeft(y));

        g.append("g")
            .attr("transform", "translate(" + width + ",0)")
            .attr("id", "right-y-axis")
            .call(d3.axisRight(y2));

        g.append("path")
            .datum(data.filter(function(d) { return d.ID == "Humidity"; }))
            .attr("fill", "none")
            .attr("stroke", "red")
            .attr("id", "humidity-line")
            .attr("d", line2);

        g.append("path")
            .datum(data.filter(function(d) { return d.ID == "Temperature"; }))
            .attr("fill", "none")
            .attr("stroke", "steelblue")
            .attr("id", "temperature-line")
            .attr("d", line);
    })
};

function update_data() {

    // Retrieve the two dates to be used
    var reference_datetime = new Date($("#datetime-selector").datetimepicker('getValue'));

    // Select the lookback period
    var lookback = $("#lookback-selector")[0].value
    var lookback_dict = {
        "1 hour":   1000*60*60,
        "6 hours":  1000*60*60*6,
        "1 day":    1000*60*60*24,
        "3 days":   1000*60*60*24*3,
        "1 week":   1000*60*60*24*7
    }
    var earlier_datetime = new Date(reference_datetime.getTime() - lookback_dict[lookback]);
    reference_datetime = dateFormat(reference_datetime, "yyyy-mm-dd+HH:MM:ss");
    earlier_datetime = dateFormat(earlier_datetime, "yyyy-mm-dd+HH:MM:ss");
    console.log(reference_datetime, earlier_datetime);

    // Call the data
    d3.csv(
    "data?start_datetime="+earlier_datetime+"&end_datetime="+reference_datetime,
    function(d) {
        d.Datetime = parseTime(d.Datetime);
        d.Value = +d.Value;
        return d;
    },

    function(error, data) {
        if (error) throw error;

        var g = d3.select("#graph_container").transition();

        // Data needs to be treated
        x.domain(d3.extent(data, function(d) { return d.Datetime; }));
        y.domain(d3.extent(data, function(d) {
            if (d.ID == "Temperature")
                {return d.Value; } else
                {return null;}
            }));
        y2.domain(d3.extent(data, function(d) {
            if (d.ID == "Humidity")
                {return d.Value; } else
                {return null; }
            }));

        // Regenerate lines and axes
        g.select("#right-y-axis")
            .duration(500)
            .call(d3.axisRight(y2));

        g.select("#left-y-axis")
            .duration(500)
            .call(d3.axisLeft(y));

        g.select("#x-axis")
            .duration(500)
            .call(d3.axisBottom(x));

        g.select("#humidity-line")
            .attr("d", line2(data.filter(function(d) { return d.ID == "Humidity"})));

        g.select("#temperature-line")
            .attr("d", line(data.filter(function(d) { return d.ID == "Temperature"})));
    })
};
