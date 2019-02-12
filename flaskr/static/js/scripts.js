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