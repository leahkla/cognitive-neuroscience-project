$(function () {
  $("#slider-vertical").slider({
    orientation: "vertical",
    range: "min",
    min: 0,
    max: 100,
    value: 60,
    timestamp: player.getTimeStamp(),
    slide: function (event, ui) {
      $("#amount").val(ui.value);
    },
    stop: function(event, ui) {
      $("#time").val(ui.timestamp);
    }
  });
  $("#amount").val($("#slider-vertical").slider("value"));
/* 
  $("#time").val($("#slider-vertical")).slider("time"));
    range: "min",
    stop: function( event, ui ) {player.getTimeStamp());}
  
  }); */
});