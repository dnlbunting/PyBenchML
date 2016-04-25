
var commitList = [];
var commitData = [];
var commitDict = {};
var fileList = []                   



d3.json("/commitviewinit", function (error, json) { // Database call that returns a list of commit hashes
    if (error) return console.warn(error);
	commitList = json.commitList;
	fileList = json.fileList;
	
	// Draws the inital chartContainer with all commits/BMs enabled
	drawCommitCharts(commitList, fileList);
	
	// Builds the Commit side bar	
	d3.select("#commitlist")
	    .selectAll(".commitlist-item")
		.data(commitList)
	  .enter()
		.append("button")
		.attr("type", "button")
		.attr("commit", function (d){ return d;})
		.attr("id", function (d,i){ return "commitbutton"+i;} )
		.attr("data-toggle", "button")
		.attr("aria-pressed", "true")
		.classed("list-group-item", true)
		.classed("btn", true)
		.classed("btn-primary", true)
		.classed("active", true)
		.classed("commitlist-item", true)
		.html(function(d){return "dd/mm/yy/ hh:mm " + d.slice(0,6);})
	
	// Builds the Files side bar	
	d3.select("#filelist")
	    .selectAll(".filelist-item")
		.data(fileList)
	  .enter()
		.append("button")
		.attr("type", "button")
		.attr("file", function (d){ return d;})
		.attr("id", function (d,i){ return "filebutton"+i;} )
		.attr("data-toggle", "button")
		.attr("aria-pressed", "true")
		.classed("list-group-item", true)
		.classed("btn", true)
		.classed("btn-primary", true)
		.classed("active", true)
		.classed("filelist-item", true)
		.html(function(d){return d;})
	
	// Redraws whole of chartContainer when charts are added/removed
	d3.selectAll(".commitlist-item").on('click', function (event) {
			
			old = d3.select(this).attr("aria-pressed");
			d3.select(this).attr("aria-pressed", old === 'true' ? 'false' : 'true');
		
			commitList = []
			d3.selectAll(".commitlist-item")
				.each( function(d,i){
						if (d3.select(this).attr("aria-pressed") === 'true') {
							commitList.push(d3.select(this).attr("commit"))}} );

			d3.select(".chartContainer").selectAll('*').remove(); // Clears the old graphs
			drawCommitCharts(commitList, fileList);
			
			// Makes the bodyContatiner rescale to match the body which rescales automatically
			d3.select(".bodyContainer").style("height", d3.select('body').style('height'));
		});

		// Redraws whole of chartContainer when charts are added/removed
		d3.selectAll(".filelist-item").on('click', function (event) {
			
				old = d3.select(this).attr("aria-pressed");
				d3.select(this).attr("aria-pressed", old === 'true' ? 'false' : 'true');
		
				fileList = []
				d3.selectAll(".filelist-item")
					.each( function(d,i){
							if (d3.select(this).attr("aria-pressed") === 'true') {
								fileList.push(d3.select(this).attr("file"))}} );

				d3.select(".chartContainer").selectAll('*').remove(); // Clears the old graphs
				drawCommitCharts(commitList, fileList);
			
				// Makes the bodyContatiner rescale to match the body which rescales automatically
				d3.select(".bodyContainer").style("height", d3.select('body').style('height'));
			});
		  

});		
	
	
function drawCommitCharts(commitList, fileList) {
	console.warn(commitList);	
	console.warn(fileList);	
	
	d3.json("/dbquery")
	    .header("Content-Type", "application/json")
	    .post(JSON.stringify({"commit": commitList , "file": fileList}), function(error, data) {
	     
		commitData = d3.nest()
				 	   .key(function (d) {return d.commit;})
					   .entries(data)
		console.warn(commitData)
			d3.select(".chartContainer")
	    	.selectAll("svg")
		    .data(commitData, function (d){ return d.key;})
		  .enter()
		    .append("svg")
			.attr("class", "chart")		// Create containers for each commit graph using the list
			.data(commitData, function (d,i){ return d.key;}) // Now that we have the full commitData list populated we can just do a single data join
			.call(chart().acc(function(d){return d3.mean(d.times);}) );
		
		});
}

  
 d3.select(window).on('resize', function(event) {
	
	d3.selectAll(".chart").selectAll('*').remove() // Clears the old graphs	
	d3.selectAll(".chart") 						// Now that we have the full commitData list populated we can just do a single data join
	.data(commitData, function (d){ return d.key;}) 
	.call(chart().acc(function(d){return d3.mean(d.times);}) )

    
});

function chart() {
  var width = 720, // default width
      height = 80; // default height
	  acc = function (d){return d;}; //identity accessor 

  function my(selection) {
    selection.each(function(data, i) {
     // generate chart here; `d` is the data and `this` is the element
	 // generate chart here, using `width` and `height`
	data = data.values
	width = parseFloat(d3.select(this).style("width"))
	height = parseFloat(d3.select(this).style("height"))
		
	var margin = {top: 50, right: 30, bottom: 50, left: 50},
	    w = width - margin.left - margin.right,
	    h = height - margin.top - margin.bottom;
	var barWidth = w/data.length
		
	var y = d3.scale.linear()
	    .domain([0,d3.max(data.map(acc))])
	    .range([0, h]);	
		
	var x = d3.scale.ordinal()
	    .domain(data.map(function(d){return d.benchmark}))
		.rangeRoundBands([0, w], .1);
		
	var c =  d3.scale.category10()
			.domain(data.map(function(d){return d.benchmark;}))
 	var graph = d3.select(this)
	   .attr("width", w + margin.left + margin.right)
 	   .attr("height", h + margin.top + margin.bottom)
 	 .append("g")
 	   .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
		
	var bar = graph.selectAll("g")
		.data(data)
	  .enter().append("g")
		.attr("transform", function(d,i){return "translate("+i*barWidth+",0)";});
		
		bar.append("rect")
		.attr("width", barWidth-1)
		.attr("height", function(d){return y(acc(d));})
		.attr("y", function(d) {return h-y(acc(d));})
		.style("fill", function(d){return c(d.benchmark);});
		
	var yAxis =  d3.svg.axis()
		.scale(y.range([h,0]))
		.orient("left");
	
	graph.append('g')
		.attr("class", "y axis")
		.call(yAxis);		
		
	var xAxis = d3.svg.axis()
		.scale(x)
		.orient("bottom");

	graph.append('g')
		.attr("class", "x axis")
		.attr("transform", "translate(0,"+h+")")
		.call(xAxis);
	
	graph.append("text")
		.attr("transform", "translate("+w/2 +",-10)")
		.text("Commit " + data[0].commit.slice(0,6))
		.style("text-anchor", "middle")
		.style("font-size", "18");		
			
    });
  }

  my.acc = function(value) {
    if (!arguments.length) return acc;
    acc = value;
    return my;
  };
  

  return my;
}
