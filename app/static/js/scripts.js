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

function sendData2D(tstamp, v1, v2, vId) {
  let epoch = + new Date();
  if (tstamp > 0 && v1 !== null && v2 !== null && vId !== null) {
    $.post("/save2D", { "timestamp": tstamp, "value": v1, "value2": v2, "videoid": vId , "date": epoch})
      .done(function (data) {
        console.log(data);
      });
  }
  else {
    console.log("no sufficient information given");
  }
}
