console.log('in js');
baseURL = 'http://127.0.0.1:5000/';

//buildBubble('BB_940');
//buildPlots('BB_940');
//getMeta('BB_940');
var OTU_desc;

populateSelectBar();


function buildBubble(sample_id, flag) {

    Plotly.d3.json(baseURL + 'samples/'+sample_id, function(error, dat) {
        console.log('buildPlots(',sample_id,') + /samples/',sample_id);
        console.log(dat);
        var samples = dat.sample_values;
        var otu_ids = dat.otu_ids;

        descriptions = otu_ids.map(function(id) { return OTU_desc[id]})

        var bubble_dat = {
            x: otu_ids,
            y: samples,
            text: descriptions,
            mode: 'markers',
            type: 'scatter',
            marker: {
              size: samples,
              color: otu_ids,
              colorscale: 'Portland'
            }
        };

        var bubble_layout = {
            title: "Levels of Bacteria by IDs in "+sample_id,
            xaxis: {
                title: 'OTU ID #',
                },
            yaxis: {
              title: 'Prevalence',
            },
        }


        console.log('bubble_dat');
        console.log(bubble_dat);
        Plotly.purge('bubble')

        Plotly.newPlot('bubble',[bubble_dat], bubble_layout);

    }) 
}

function populateSelectBar() {
    $select = Plotly.d3.select('#selDataset');
    Plotly.d3.json(baseURL + 'otu', function(error,dat) {
        OTU_desc = dat
        console.log(dat)
    }) 

    Plotly.d3.json(baseURL + 'names', function(error, names) {
        console.log('populateSelectBar() + /names');
        names = names.sort();
        console.log(names);
        names.forEach(name => {
            $select.append('option').text(name);
        });
        sample_id = names[0]
        buildPlots(sample_id, true);
        buildBubble(sample_id, true);
        getMeta(sample_id);
    });

};

function buildPlots(sample_id, flag) {
    
    Plotly.d3.json(baseURL + 'samples/'+sample_id, function(error, dat) {
        console.log('buildPlots(',sample_id,') + /samples/',sample_id);
        console.log(dat);
        var samples = dat.sample_values;
        var otu_ids = dat.otu_ids;

        pie_samples = samples.slice(0,10);
        pie_otu_ids = otu_ids.slice(0,10);
        pie_dat = {
            values: pie_samples,
            labels: pie_otu_ids,
            showlegend: true,
            type: 'pie'
        };
        var pie_layout = {
            title: "Top Bacteria IDs in Sample " + sample_id
        }

        Plotly.purge('pie')
        Plotly.newPlot('pie',[pie_dat], pie_layout);

    });  

};

function getMeta(sample_id) {
    
    Plotly.d3.json(baseURL + 'metadata/'+sample_id, function(error, metaDat) {
        var innerHTML = "<p>";
        console.log('metadata(',sample_id,') + /metadata/',sample_id);
        console.log(metaDat);
        Object.keys(metaDat).forEach(stat => {
            innerHTML += `${stat}: ${metaDat[stat]}<br>`;
        });
        innerHTML += '</p>';
        Plotly.d3.select('#metaData').html(innerHTML);
    });
};

function optionChanged(sample_id) {
    console.log('optionChanged(' + sample_id + ')');

    buildPlots(sample_id, false);
    buildBubble(sample_id, false);
    getMeta(sample_id);
};