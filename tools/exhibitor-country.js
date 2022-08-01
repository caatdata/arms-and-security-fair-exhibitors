onMapLoad(function (data) {
  var srcFreq = {};

  var out = {
    "type": "FeatureCollection",
    "features": []
  };

  var datelineOffset = 15;
  for (var i = 0; i < data.length; i++) {
    var event = data[i];
    for (var j = 0; j < event.exhibitor.length; j++) {
      var exhibitor = event.exhibitor[j];
      if (typeof(srcFreq[exhibitor.latLon]) == "undefined") {
        srcFreq[exhibitor.latLon] = {
          "type": "Feature",
          "properties": {
            "freq": 0
          },
          "geometry": {
            "type": "Point",
            "coordinates": [
              exhibitor.latLon[1],
              exhibitor.latLon[0],
            ]
          }
        }
      }
      srcFreq[exhibitor.latLon].properties.freq += 1;
    }
  }

  out.features = Object.values(srcFreq);

  map.on('load', () => {
    map.setCenter([10, datelineOffset]);
    map.addSource('exhibitor', {
      type: 'geojson',
      data: out
    });

    var markerPath = "/marker-circle.png";

    // Symbol
    map.loadImage(
      markerPath,
      (error, image) => {
        if (error) throw error;
        map.addImage('custom-marker', image);
        // map.showCollisionBoxes = true;
        // Add a symbol layer
        map.addLayer({
          'id': 'points',
          'type': 'symbol',
          'source': 'exhibitor',
          'layout': {
            'icon-image': 'custom-marker',
            // 'icon-padding': 2,
            // 'text-padding': 2,
            "icon-allow-overlap": true,
            "icon-ignore-placement": true,
            "text-allow-overlap": true,
            "text-ignore-placement": true,
            'text-field': ['get', 'freq'],
            'text-font': ['Open Sans Semibold'],
            'text-offset': [0, 0],
            'text-anchor': 'center',
            'text-size': 15,
            'symbol-z-order': "source",
            "symbol-sort-key": ["to-number", ["get", "freq"]]
          }
        });
      }
    );
  });
});
