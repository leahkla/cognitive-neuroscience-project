function sendData(tstamp, v, vId) {
  let epoch = + new Date();
  if (tstamp > 0 && v !== null && vId !== null) {
    $.post("/save", { timestamp: tstamp, value: v, videoid: vId , date: epoch})
      .done(function (data) {
        console.log(data);
      });
  }
  else {
    console.log("no sufficient information given");
  }
}