<<<<<<< HEAD
$( function() {
    $( "#slider-vertical" ).slider({
      orientation: "vertical",
      range: "min",
      min: 0,
      max: 10,
      value: 5,
      slide: function( event, ui ) {
        $( "#amount" ).val( ui.value );
      }
    });
    $( "#amount" ).val( $( "#slider-vertical" ).slider( "value" ) );
 } );
=======
$(function () {
  $("#slider-vertical").slider({
    orientation: "vertical",
    range: "min",
    min: 0,
    max: 100,
    value: 60,
    slide: function (event, ui) {
      $("#amount").val(ui.value);
    }
  });
  $("#amount").val($("#slider-vertical").slider("value"));
});
>>>>>>> c6cc34181830060fb58979a6ab38dee825f84ad0
