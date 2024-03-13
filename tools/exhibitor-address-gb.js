onMapLoad(function (data) {
  var out = {
    "type": "FeatureCollection",
    "features": []
  };

  var datelineOffset = 15;
  for (var i = 0; i < data.length; i++) {
    var event = data[i];
    for (var j = 0; j < event.exhibitor.length; j++) {
      var exhibitor = event.exhibitor[j];
      out.features.push({
        "type": "Feature",
        "geometry": {
          "type": "Point",
          "coordinates": [
            exhibitor.latLon[1],
            exhibitor.latLon[0],
          ]
        }
      });

    }
  }

  var markerPath = "/marker-dot.png";

  map.on('load', () => {
    map.fitBounds([
      [-18.0, 50.0],
      [-2.0, 59.0]
    ]);
    map.addSource('exhibitor', {
      type: 'geojson',
      lineMetrics: true,
      data: out
    });

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
            // 'text-field': ['get', 'freq'],
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
