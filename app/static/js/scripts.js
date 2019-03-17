function sendData(tstamp, v, vname) {
  $.post("/save", { timestamp: tstamp, value: v, videoname: vname })
    .done(function (data) {
      console.log(data);
    });
}

$(function () {
  var timestamp;
  var slider_value;
  $("#slider-vertical").slider({
    orientation: "vertical",
    range: "min",
    min: 0,
    max: 100,
    value: 50,
    slide: function (event, ui) {
      $("#amount").val(ui.value);
      slider_value = ui.value;
    },
    stop: function (event) {
      player.getCurrentTime().then(responseVal => {
        player.getVideoUrl().then(responseUrl => {
          console.log(responseVal);
          console.log(responseUrl);
          sendData(responseVal, slider_value, responseUrl);
        });
      });
    }
  });
  $("#amount").val($("#slider-vertical").slider("value"));
  //$("#timestamp").val($("#slider-vertical").slider("timestamp"));
  /*
    $("#time").val($("#slider-vertical")).slider("time"));
      range: "min",
      stop: function( event, ui ) {player.getTimeStamp());}

    }); */
});
