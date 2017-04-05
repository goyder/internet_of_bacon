$(function() {
    console.log(debug_mode);
    console.log('jquery is working!');
    createGraph();
});

function createGraph() {
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

    var parseTime = d3.timeParse("%Y-%m-%d %H:%M:%S");

    // Develop graph container
    var svg = d3.select("#graph_container").append("svg")
        .attr("width", frame_width)
        .attr("height", frame_height)
        .attr("class", "monitor");

    // Develop graph
    var g = svg.append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
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

    // Call the data
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
            .call(d3.axisBottom(x));

        g.append("text")
            .attr("class", "x-axis label")
            .attr("text-anchor", "middle")
            .attr("x", width/2)
            .attr("y", height +  40)
            .text("Date-time");

        g.append("g")
            .call(d3.axisLeft(y));

        g.append("g")
            .attr("transform", "translate(" + width + ",0)")
            .call(d3.axisRight(y2));

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

        g.append("path")
            .datum(data.filter(function(d) { return d.ID == "Humidity"; }))
            .attr("fill", "none")
            .attr("stroke", "red")
            .attr("d", line2);

        g.append("path")
            .datum(data.filter(function(d) { return d.ID == "Temperature"; }))
            .attr("fill", "none")
            .attr("stroke", "steelblue")
            .attr("d", line);

    })




}
