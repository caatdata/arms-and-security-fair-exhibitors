var mapId = "map";
var style= "caatdata/cl1ukq94a005514s2gb2r2sis";
var mapboxApiKey = __MAPBOX_API_KEY__;

var map;

var caatWhite = "#FFFFFF";
var caatBlue = "#1E1D3E";
var caatRed = "rgba(226,6,19,1)"; // #E20613
var caatRedT = "rgba(226,6,19,0)";
var caatGraphicBackground = "hsl(0,0,98)"; // #fafafa

var canvas = document.createElement('canvas');
var hasWebGL = !!(window.WebGLRenderingContext && (canvas.getContext('webgl') || canvas.getContext('experimental-webgl')));
console.assert(hasWebGL);

map = new mapboxgl.Map({
  preserveDrawingBuffer: true,
  container: mapId,
  accessToken: mapboxApiKey,
  style: "mapbox://styles/" + style,
  bounds: [
    [
      -180,
      -60,
    ],
    [
      180,
      70,
    ],
  ]
});

function mapPng() {
  return map.getCanvas().toDataURL();
}

var request = new XMLHttpRequest();

function obj(ll) {
  return {
    y: ll[0],
    x: ll[1]
  };
}

function filterGeoJson(result) {
  var data = JSON.parse(request.responseText);
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

}

request.onload = filterGeoJson;
request.open("get", __GEO_JSON_NAME__, true);
request.send();
