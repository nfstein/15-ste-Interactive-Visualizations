# import necessary libraries
import pandas as pd

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import (
    Flask,
    render_template,
    jsonify)

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///DataSets/belly_button_biodiversity.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to the table
OTU = Base.classes.otu
Samples = Base.classes.samples
Samples_Metadata = Base.classes.samples_metadata

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


# Query the database and send the jsonified results
@app.route("/names")
def names():
    """List of sample names.

    Returns a list of sample names in the format
    [
        "BB_940",
        "BB_941",
        "BB_943",
        "BB_944",
        "BB_945",
        "BB_946",
        "BB_947",
        ...
    ]

    """
    samples_object = session.query(Samples).first()

    sampleNames = []
    for key in [key for key in vars(samples_object)][1:]:
        if key != 'otu_id':
            sampleNames.append(key)

    return jsonify(sampleNames)

@app.route("/otu")
def otu():
    """List of OTU descriptions.

    Returns a list of OTU descriptions in the following format

    [
        "Archaea;Euryarchaeota;Halobacteria;Halobacteriales;Halobacteriaceae;Halococcus",
        "Archaea;Euryarchaeota;Halobacteria;Halobacteriales;Halobacteriaceae;Halococcus",
        "Bacteria",
        "Bacteria",
        "Bacteria",
        ...
    ]
    """

    OTU_objects = session.query(OTU).all()

    taxonomic_units = [OTU.lowest_taxonomic_unit_found for OTU in OTU_objects]

    return jsonify(taxonomic_units)

@app.route('/metadata/<sample>')
def metadata(sample):
    """MetaData for a given sample.

    Args: Sample in the format: `BB_940`

    Returns a json dictionary of sample metadata in the format

    {
        AGE: 24,
        BBTYPE: "I",
        ETHNICITY: "Caucasian",
        GENDER: "F",
        LOCATION: "Beaufort/NC",
        SAMPLEID: 940
    }
    """
    sample_num = sample.split('_')[1]

    sample_metadata = session.query(Samples_Metadata).filter(Samples_Metadata.SAMPLEID == sample_num).first()
    
    return jsonify({
    'AGE': sample_metadata.AGE,
    'BBTYPE': sample_metadata.BBTYPE,
    'ETHNICITY': sample_metadata.ETHNICITY,
    'GENDER': sample_metadata.GENDER,
    'LOCATION': sample_metadata.LOCATION,
    'SAMPLEID': sample_metadata.SAMPLEID
    })

@app.route('/wfreq/<sample>')
def wfreq(sample):
    """Weekly Washing Frequency as a number.

    Args: Sample in the format: `BB_940`

    Returns an integer value for the weekly washing frequency `WFREQ`
    """
    sample_num = sample.split('_')[1]
    sample_metadata = session.query(Samples_Metadata).filter(Samples_Metadata.SAMPLEID == sample_num).first()
    sample_metadata.WFREQ
    return jsonify(sample_metadata.WFREQ)

@app.route('/samples/<sample_id>')
def sample_data(sample_id):
    """OTU IDs and Sample Values for a given sample.

    Sort your Pandas DataFrame (OTU ID and Sample Value)
    in Descending Order by Sample Value

    Return a list of dictionaries containing sorted lists  for `otu_ids`
    and `sample_values`

    [
        {
            otu_ids: [
                1166,
                2858,
                481,
                ...
            ],
            sample_values: [
                163,
                126,
                113,
                ...
            ]
        }
    ]
    """
    sample_values = []
    otu_ids = []
    samples = session.query(Samples.otu_id,sample_id).order_by(sample_id)
    for sample in samples.all():
        otu_ids.append(sample[0])
        sample_values.append(sample[1])
    otu_ids.reverse()
    sample_values.reverse()

    data = {
        'sample_values': sample_values,
        'otu_ids': otu_ids
        }

    return jsonify(data)


# create route that renders index.html template
@app.route("/")
def home():
    print('in /')
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
