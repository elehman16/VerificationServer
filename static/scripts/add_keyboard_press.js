$(document).keydown(function(e) {
    switch(e.which) {
        case 37: // left
          break;

        case 38: // up
          previous();
          break;

        case 39: // right

          break;

        case 40: // down
          next();
          break;

        default:
          return; // exit this handler for other keys
    }

    e.preventDefault(); // prevent the default action (scroll / move caret)
});
