
$(document).ready(function () {

    for (i = 0; i <= 20; i++) {
        $("#frame pre:eq(" + i + ")").delay(i * 50).animate({ opacity: 1 }, 100);
    }
    for (i = 0; i <= 20; i++) {
        $("#logo pre:eq(" + i + ")").delay(1000+ i * 50).animate({ opacity: 1 }, 100);
    }
    $('#welcome pre').delay(2000).animate({ "opacity": 1 }, 100 );
    $('#menu pre').delay(2200).animate({ "opacity": 1 }, 100);


    $(document).keypress(function (event) {
        if (event.which == 49) {
            window.location.href = "fake-tweet.html";
        }
        if (event.which == 50) {
            window.location.href = "../";
        }
    });

});