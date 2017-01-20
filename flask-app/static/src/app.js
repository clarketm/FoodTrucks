var React = require('react');
var ReactDOM = require('react-dom');
var Sidebar = require('./components/Sidebar');

// setting up mapbox
mapboxgl.accessToken = 'pk.eyJ1IjoiY2xhcmtldG0iLCJhIjoiY2l5NWRhOHVrMDA0bDJxcXA4ZHQ2anV4NyJ9.PAjkExk8fi1I6PzF8rmdQw';

var map = new mapboxgl.Map({
    container: 'map',
    style: 'mapbox://styles/clarketm/ciy5dbm4k002e2st2m2jkns6q',
    center: [-122.2015, 47.6101],
    zoom: 15
});

ReactDOM.render(
    <Sidebar map={map} />,
    document.getElementById("sidebar")
);

function formatHTMLforMarker(props) {
    var { name, hours, address } = props;
    var html = "<div class=\"marker-title\">" + name + "</div>" + 
        "<h4>Operating Hours</h4>" + 
        "<span>" + hours + "</span>" +
        "<h4>Address</h4>" + 
        "<span>"+ address + "</span>";
    return html;
};

// setup popup display on the marker
map.on('click', function (e) {
    map.featuresAt(e.point, {layer: 'trucks', radius: 10, includeGeometry: true}, function (err, features) {
        if (err || !features.length)
            return;

        var feature = features[0];

        new mapboxgl.Popup()
            .setLngLat(feature.geometry.coordinates)
            .setHTML(formatHTMLforMarker(feature.properties))
            .addTo(map);
    });
});

map.on('click', function (e) {
    map.featuresAt(e.point, {layer: 'trucks-highlight', radius: 10, includeGeometry: true}, function (err, features) {
        if (err || !features.length)
            return;

        var feature = features[0];

        new mapboxgl.Popup()
            .setLngLat(feature.geometry.coordinates)
            .setHTML(formatHTMLforMarker(feature.properties))
            .addTo(map);
    });
});
