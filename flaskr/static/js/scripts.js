$(function () {
  var timestamp;
  $("#slider-vertical").slider({
    orientation: "vertical",
    range: "min",
    min: 0,
    max: 100,
    value: 60,
    slide: function (event, ui) {
      $("#amount").val(ui.value);
    },
    stop: function(event) {
      $("#current-time").val(event, ui);
    }
  });
  $("#amount").val($("#slider-vertical").slider("value"));
  $("#timestamp").val($("#slider-vertical").slider("timestamp"));
/* 
  $("#time").val($("#slider-vertical")).slider("time"));
    range: "min",
    stop: function( event, ui ) {player.getTimeStamp());}
  
  }); */
});