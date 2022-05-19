var mapId = "map";
var style= "caatdata/cl1ukq94a005514s2gb2r2sis";
var mapboxApiKey = __MAPBOX_API_KEY__;

var map;

var caatWhite = "#FFFFFF";
var caatBlue = "#1E1D3E";
var caatRed = "rgba(226,6,19,1)";
var caatRedT = "rgba(226,6,19,0)";

var canvas = document.createElement('canvas');
var hasWebGL = !!(window.WebGLRenderingContext && (canvas.getContext('webgl') || canvas.getContext('experimental-webgl')));
console.log(hasWebGL);
console.assert(hasWebGL);
console.log(mapboxgl);

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
  console.log(map.getCanvas().toDataURL());
  return map.getCanvas().toDataURL();
}

map.on('load', () => {
  map.setPaintProperty("admin-0-boundary-disputed", 'line-color', caatWhite);
  map.setPaintProperty("admin-0-boundary", 'line-color', caatWhite);
  map.setPaintProperty("admin-0-boundary", 'line-width', .5);
  map.setPaintProperty("country-label", 'text-color', caatWhite);
  map.setPaintProperty("land", 'background-color', caatBlue);
  map.setCenter([10, 15]);
  map.addSource('exhibitor', {
    type: 'geojson',
    data: __GEO_JSON_NAME__
  });
  map.addLayer(
    {
      id: 'exhibitor-heat',
      type: 'heatmap',
      source: 'exhibitor',
      maxzoom: 15,
      paint: {
        // increase weight as diameter breast height increases
        'heatmap-weight': 1,
        // increase intensity as zoom level increases
        'heatmap-intensity': .1,
        // assign color values be applied to points depending on their density
        'heatmap-color': [
          'interpolate',
          [
            'linear'
          ],
          [
            'heatmap-density'
          ],
          0,
          caatRedT,
          0.1,
          caatRed,
          0.9,
          caatRed,
          1.0,
          caatWhite
        ],
        // increase radius as zoom increases
        'heatmap-radius': {
          stops: [
            [11, 15],
            [15, 20]
          ]
        },
        // decrease opacity to transition into the circle layer
        'heatmap-opacity': {
          default: 1,
          stops: [
            [14, 1],
            [15, 0]
          ]
        }
      }
    },
    'country-label'
  );
});
