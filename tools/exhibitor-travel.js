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
      var generator = new arc.GreatCircle(
        {
          x: event.eventLatLon[1],
          y: event.eventLatLon[0],
        },
        {
          x: exhibitor.latLon[1],
          y: exhibitor.latLon[0],
        }
      );
      var arcGeo = generator.Arc(20, {
        offset: datelineOffset
      });
      for (var k = 0; k < arcGeo.geometries.length; k++) {
        var feature = {
          "type": "Feature",
          "properties": {
            "eventName": event.name,
            "exhibitorName": exhibitor.name,
            "distance": generator.g,
          },
          "geometry": {
            "type": "LineString",
            "coordinates": arcGeo.geometries[k].coords
          }
        }
        out.features.push(feature);
      }
    }
  }

  out.features.sort(function (a, b) {
    return a.properties.distance - b.properties.distance;
  });

  map.on('load', () => {
    map.setCenter([10, datelineOffset]);
    map.addSource('exhibitor', {
      type: 'geojson',
      lineMetrics: true,
      data: out
    });
    map.addLayer(
      {
        id: 'travel',
        type: 'line',
        source: 'exhibitor',
        layout: {
          'line-join': 'round',
          'line-cap': 'round'
        },
        paint: {
          'line-opacity': 1,
          'line-width': 1,
          'line-gradient': [
            'interpolate',
            [
              'linear'
            ],
            [
              'line-progress'
            ],
            0.3,
            caatRed,
            0.7,
            caatBlue
          ]
        }

      },
      'country-label'
    );
  });
});
