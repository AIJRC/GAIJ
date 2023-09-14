const DATA_DIR = "../data/";

// Load subgraphs_list.json and populate the dropdown
d3.json(DATA_DIR + "subgraphs_list.json").then(function(subgraphs) {
    var dropdown = d3.select("#graphDropdown");
    subgraphs.forEach(function(graph) {
        dropdown.append("option")
            .attr("value", graph.path)
            .text(graph.industry + " (" + graph.num_nodes + " nodes)");
    });

    // Load the first graph by default
    loadGraphData(subgraphs[1].path);
});

// Event listener for the dropdown
d3.select("#graphDropdown").on("change", function() {
    var selectedPath = d3.select(this).property("value");
    loadGraphData(DATA_DIR + selectedPath);
});

function loadGraphData(path) {
    if (simulation) {
        simulation.stop();
    }
    
    // remove existing links and nodes
    svg.selectAll("*").remove();
    
    // load new graph data
    d3.json(path).then(function(_graph) {
        graph = _graph;
        initializeDisplay();
        initializeSimulation();
    });
}

var svg = d3.select("svg");
    // .call(d3.zoom().on("zoom", function (event) {
    //     svg.attr("transform", event.transform)
    // }))

var width = +svg.node().getBoundingClientRect().width,
    height = +svg.node().getBoundingClientRect().height;

// svg objects
var link, node;
// the data - an object with nodes and links
var graph;

//////////// FORCE SIMULATION ////////////

// force simulator
var simulation;

// set up the simulation and event to update locations after each tick
function initializeSimulation() {
  simulation = d3.forceSimulation();
  simulation.nodes(graph.nodes);
  initializeForces();
  simulation.on("tick", ticked);
}

// values for all forces
forceProperties = {
    center: {
        x: 0.5,
        y: 0.5
    },
    charge: {
        enabled: true,
        strength: -30,
        distanceMin: 1,
        distanceMax: 2000
    },
    collide: {
        enabled: true,
        strength: .7,
        iterations: 1,
        radius: 7
    },
    forceX: {
        enabled: true,
        strength: .2,
        x: .5
    },
    forceY: {
        enabled: true,
        strength: .2,
        y: .5
    },
    link: {
        enabled: true,
        distance: 30,
        iterations: 1
    }
}

// add forces to the simulation
function initializeForces() {
    // add forces and associate each with a name
    simulation
        .force("link", d3.forceLink())
        .force("charge", d3.forceManyBody())
        .force("collide", d3.forceCollide())
        .force("center", d3.forceCenter())
        .force("forceX", d3.forceX())
        .force("forceY", d3.forceY());
    // apply properties to each of the forces
    updateForces();
}

// apply new force properties
function updateForces() {
    if (!simulation) return;  // Check if simulation is defined.

    // get each force by name and update the properties
    simulation.force("center")
        .x(width * forceProperties.center.x)
        .y(height * forceProperties.center.y);
    simulation.force("charge")
        .strength(forceProperties.charge.strength * forceProperties.charge.enabled)
        .distanceMin(forceProperties.charge.distanceMin)
        .distanceMax(forceProperties.charge.distanceMax);
    simulation.force("collide")
        .strength(forceProperties.collide.strength * forceProperties.collide.enabled)
        .radius(forceProperties.collide.radius)
        .iterations(forceProperties.collide.iterations);
    simulation.force("forceX")
        .strength(forceProperties.forceX.strength * forceProperties.forceX.enabled)
        .x(width * forceProperties.forceX.x);
    simulation.force("forceY")
        .strength(forceProperties.forceY.strength * forceProperties.forceY.enabled)
        .y(height * forceProperties.forceY.y);
    simulation.force("link")
        .id(function(d) {return d.id;})
        .distance(forceProperties.link.distance)
        .iterations(forceProperties.link.iterations)
        .links(forceProperties.link.enabled ? graph.links : []);

    // updates ignored until this is run
    // restarts the simulation (important if simulation has already slowed down)
    simulation.alpha(1).restart();
}



//////////// DISPLAY ////////////

// generate the svg objects and force simulation
function initializeDisplay() {
    // set the data and properties of link lines
    
    const defs = svg.append("defs");
    defs.append("marker")
      .attr("id", "arrowhead") 
      .attr("viewBox", "-0 -5 10 10")
      .attr("refX", 15)
      .attr("refY", 0)
      .attr("orient", "auto")
      .attr("markerWidth", 10)
      .attr("markerHeight", 10)
      .attr("xoverflow", "visible")
      .append("svg:path")
      .attr("d", "M 0,-5 L 10 ,0 L 0,5")
      .attr("fill", "black");

    link = svg.append("g")
        .attr("class", "links")
    .selectAll("line")
    .data(graph.links)
    .enter()
    .append("line")
    .style("stroke", "black")
    .attr("marker-end", "url(#arrowhead)");
    link = svg.append("g")
        .attr("class", "links")
    .selectAll("path")
    .data(graph.links)
    .enter()
    .append("path")
    .attr('d', function(d) {
        var dx = d.target.x - d.source.x,
            dy = d.target.y - d.source.y,
            dr = Math.sqrt(dx * dx + dy * dy);
        return "M" + 
            d.source.x + "," + 
            d.source.y + "Q" + 
            (d.source.x + d.target.x)/2 + "," + 
            (d.source.y + d.target.y)/2 + " " + 
            d.target.x + "," + 
            d.target.y;
    })
    .style("stroke", "black")
    .attr("fill", "none")
    .attr("marker-end", "url(#arrowhead)");



    // set the data and properties of node circles
    node = svg.selectAll(".node")
        .data(graph.nodes, d => d.id)
        .enter()
        .append("g")
        .attr("class", "node")
        .call(d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)).on("click", click)
        // .on("end", dragended));
        .on("mouseleave", mouseLeave);

    circle = node.append("circle")
        .attr("r", forceProperties.collide.radius)
        .attr("class", "circle")
        .on("mouseenter", mouseEnter)
        .on("mouseleave", mouseLeave)
        .on("click", click)

    // .on("end", dragended));

    // node tooltip
    node.append("title")
        .text(function(d) { return d.id; });

    node.append("text")
        .style("class", "icon")
        .attr("font-family", "FontAwesome")
        .attr("dominant-baseline", "central")
        .attr("text-anchor", "middle")
        .attr("y", -25)
        .attr("font-size", 15)
        .attr("fill", "black")
        .attr("stroke-width", "0px")
        .text((d) => d.id)
        .style("visibility", "hidden");

    updateDisplay();
}

// update the display based on the forces (but not positions)
function updateDisplay() {
    node
        .attr("r", forceProperties.collide.radius)
        .attr("stroke", forceProperties.charge.strength > 0 ? "blue" : "red")
        .attr("stroke-width", forceProperties.charge.enabled==false ? 0 : Math.abs(forceProperties.charge.strength)/15);
    
    circle
        .attr("r", forceProperties.collide.radius)

    link
        // .attr("d", linkArc)
        .attr("stroke-width", forceProperties.link.enabled ? 1 : .5)
        .attr("opacity", forceProperties.link.enabled ? 1 : 0);

}

// update the display positions after each simulation tick
function ticked() {

    link
        .attr("d", linkArc)
        .attr("x1", function(d) { return d.source.x; })
        .attr("y1", function(d) { return d.source.y; })
        .attr("x2", function(d) { return d.target.x; })
        .attr("y2", function(d) { return d.target.y; });
        
    node
        // .attr("cx", function(d) { return d.x; })
        // .attr("cy", function(d) { return d.y; })
        .attr("transform", function (d) { return "translate(" + d.x + ", " + d.y + ")"; });

    d3.select('#alpha_value').style('flex-basis', (simulation.alpha()*100) + '%');

}



//////////// UI EVENTS ////////////


function dragstarted(event, d) {
    d3.selectAll(".hovered").classed("fixed", true);
    d3.select(this).select("text").style("visibility", "visible") 
    if (!event.active) simulation.alpha(.5).restart();
    d.fx = d.x;
    d.fy = d.y;
}

function dragged(event, d) {
    d3.select(this).classed(".fixed", true);
    d.fx = clamp(event.x, 0, width);
    d.fy = clamp(event.y, 0, height);
    simulation.alpha(.5).restart();
}

function dragended(event, d) {
    if (!event.active) simulation.alpha(1).restart();
    d3.select(this)
    d.fx = null;
    d.fy = null;
}

// update size-related forces
d3.select(window).on("resize", function(){
    width = +svg.node().getBoundingClientRect().width;
    height = +svg.node().getBoundingClientRect().height;
    updateForces();
});

function mouseEnter(event, d) {
    d3.select(this).classed("hovered", true)
    d3.select(this).transition().duration(100).attr("r", forceProperties.collide.radius * 2.5);
    var tooltip = document.getElementById("tooltip")
    tooltip.style.top = `${(8)}px`; //event.clientY - 150 + "px"
    tooltip.style.left = `${(180)}px`; //event.clientX - 95 + "px"
    tooltip.classList.add("active")

    document.getElementById("tooltip_id").innerHTML = d.id // + " classes: " + d3.select(this).attr("class")
}

function mouseLeave(d) {
    if (d3.select(this).classed("fixed") == false) {
        d3.select(this).classed("hovered", false);
    }
    d3.select(this).transition().duration(800).attr("r", forceProperties.collide.radius);

    document.getElementById("tooltip").classList.remove("active")
}

function clamp(x, lo, hi) {
    return x < lo ? lo : x > hi ? hi : x;
  }

function click(event, d) {
    delete d.fx;
    delete d.fy;
    d3.select(this).classed("fixed", false)
    d3.select(this).select("text").style("visibility", "hidden") 
    d3.select(this).transition().duration(800).attr("r", forceProperties.collide.radius);
    simulation.alpha(1).restart()

    document.getElementById('sidebar-name').textContent = d.id;
    document.getElementById('sidebar-industry').textContent = d.industry_name;
    document.getElementById('sidebar-address').textContent = d.address;
    document.getElementById('sidebar-opencorporates-link').href = "https://opencorporates.com/companies/no/" + d.number;
    document.getElementById('sidebar').style.display = 'block';
  }


function linkArc(d) {
    const r = Math.hypot(d.target.x - d.source.x, d.target.y - d.source.y);
        return `
        M${d.source.x},${d.source.y}
        A${r},${r} 0 0,1 ${d.target.x},${d.target.y}
    `;
}
// convenience function to update everything (run after UI input)
function updateAll() {
    updateForces();
    updateDisplay();
};
