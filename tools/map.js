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

function onMapLoad(callback) {
  var request = new XMLHttpRequest();
  request.onload = function() {
    var data = JSON.parse(request.responseText);
    callback(data);
  };
  request.open("get", __GEO_JSON_NAME__, true);
  request.send();
}
