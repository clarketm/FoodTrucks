var React = require('react');

var Intro = React.createClass({
    render() {
        return (
        <div className="intro">
            <h3>About</h3>
            <p>The app is built with Flask on the backend and Elasticsearch is the engine powering the search.</p>
            <p>The frontend is hand-crafted with React and the beautiful maps are courtesy of Mapbox.</p>
            <p>Lastly, the data for the food trucks is made available in public domain by <a href="https://data.kingcounty.gov/Health/mobile-food-unit-risk-cat-1/vnp4-wfma">King County Data</a></p>
        </div>
      )
    }
});

module.exports = Intro;
