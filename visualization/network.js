const svg = d3.select("svg");
let width = +svg.node().getBoundingClientRect().width;
let height = +svg.node().getBoundingClientRect().height;
let link, node, graph, simulation;

d3.json("../data/subgraphs_list.json").then(subgraphs => {
    const dropdown = d3.select("#graphDropdown");
    dropdown.selectAll("option")
        .data(subgraphs)
        .enter().append("option")
        .attr("value", d => d.path)
        .text(d => `${d.top_suspects} (${d.num_nodes} nodes)`);
});

d3.select("#graphDropdown").on("change", function() {
    const selectedPath = d3.select(this).property("value");
    loadGraphData(selectedPath);
});

function loadGraphData(path) {
    if (simulation) simulation.stop();
    svg.selectAll("*").remove();
    d3.json(path).then(_graph => {
        graph = _graph;
        initializeDisplay();
        initializeSimulation();
    });
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

function initializeSimulation() {
    simulation = d3.forceSimulation(graph.nodes)
        .force("link", d3.forceLink())
        .force("charge", d3.forceManyBody())
        .force("collide", d3.forceCollide())
        .force("center", d3.forceCenter())
        .force("forceX", d3.forceX())
        .force("forceY", d3.forceY())
        .on("tick", ticked);
    updateForces();
}

// apply new force properties
function updateForces() {
	if (!simulation) return; // Check if simulation is defined.

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
		.id(function(d) {
			return d.id;
		})
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

	link = svg.append("g").attr("class", "links").selectAll("path")
		.data(graph.links).enter().append("path")
		.attr('d', function(d) {
			var dx = d.target.x - d.source.x,
				dy = d.target.y - d.source.y,
				dr = Math.sqrt(dx * dx + dy * dy);
			return "M" +
				d.source.x + "," +
				d.source.y + "Q" +
				(d.source.x + d.target.x) / 2 + "," +
				(d.source.y + d.target.y) / 2 + " " +
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
		.on("mouseleave", mouseLeave);

	circle = node.append("circle")
		.attr("r", forceProperties.collide.radius)
		.attr("class", function(d) {
			return d.suspect ? "circle suspect" : "circle";
		})
		.on("mouseenter", mouseEnter)
		.on("mouseleave", mouseLeave)
		.on("click", click)

	node.append("title")
		.text(function(d) {
			return d.id;
		});

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
		.attr("stroke-width", forceProperties.charge.enabled == false ? 0 : Math.abs(forceProperties.charge.strength) / 15);

	circle
		.attr("r", forceProperties.collide.radius)

	link
		// .attr("d", linkArc)
		.attr("stroke-width", forceProperties.link.enabled ? 1 : .5)
		.attr("opacity", forceProperties.link.enabled ? 1 : 0);

}

// update the display positions after each simulation tick
function ticked() {
    link.attr("d", linkArc);
    node.attr("transform", d => `translate(${d.x}, ${d.y})`);
    d3.select('#alpha_value').style('flex-basis', `${simulation.alpha() * 100}%`);
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

	updateSidebar(d);
}

d3.select(window).on("resize", function() {
	width = +svg.node().getBoundingClientRect().width;
	height = +svg.node().getBoundingClientRect().height;
	updateForces();
});

function mouseEnter(event, d) {
	d3.select(this).classed("hovered", true)
	d3.select(this).transition().duration(100).attr("r", forceProperties.collide.radius * 1.5);
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
	d3.select(this).transition().duration(100).attr("r", forceProperties.collide.radius);

	document.getElementById("tooltip").classList.remove("active")
}

function clamp(x, lo, hi) {
	return Math.max(lo, Math.min(x, hi));
}

function updateSidebar(d) {
    document.getElementById('sidebar-name').textContent = d.id;
    document.getElementById('sidebar-industry').textContent = d.industry_name;
    document.getElementById('sidebar-opencorporates-link').href = "https://opencorporates.com/companies/no/" + d.number;

	const sourceButton = document.getElementById('sidebar-source-btn');
    sourceButton.onclick = function() {
        fetchTextForID(d.number);
    };

    document.getElementById('sidebar').style.display = 'block';
}

function click(event, d) {
	delete d.fx;
	delete d.fy;
	d3.select(this).classed("fixed", false)
	d3.select(this).select("text").style("visibility", "hidden")
	d3.select(this).transition().duration(800).attr("r", forceProperties.collide.radius);
	simulation.alpha(1).restart()

	updateSidebar(d);
}

function linkArc(d) {
	const r = Math.hypot(d.target.x - d.source.x, d.target.y - d.source.y);
	return `
        M${d.source.x},${d.source.y}
        A${r},${r} 0 0,1 ${d.target.x},${d.target.y}
    `;
}

function updateAll() {
    updateForces();
    updateDisplay();
};

function fetchTextForID(id) {
    fetch(`../data/txts/${id}_arso_2020.csv.txt`)
        .then(response => response.text())
        .then(data => {
            // Use a regular expression to replace instances of the ID with a highlighted version
            const highlightedText = data.replace(new RegExp(id, 'g'), `<span class="highlight">${id}</span>`);
            
            const modal = document.getElementById('myModal');
            const modalText = document.getElementById('modal-text-content');
            
            modalText.innerHTML = highlightedText;  // Use innerHTML since we're adding HTML tags for highlighting
            modal.style.display = "block";
        })
        .catch(error => {
            console.error('There was an error fetching the text:', error);
        });
}

// When the user clicks on <span> (x), close the modal
document.getElementsByClassName("close")[0].onclick = function() {
  document.getElementById('myModal').style.display = "none";
}

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
  if (event.target == document.getElementById('myModal')) {
    document.getElementById('myModal').style.display = "none";
  }
}
