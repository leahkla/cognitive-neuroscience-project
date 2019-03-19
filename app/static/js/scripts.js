function sendData(tstamp, v, vId) {
  $.post("/save", { timestamp: tstamp, value: v, videoid: vId })
    .done(function (data) {
      console.log(data);
    });
}