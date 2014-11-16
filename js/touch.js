(function(window) {
  function addTouchEvent(el, touchName, fingers, callback) {
    var eventName = 'touch' + touchName + fingers.toString();
    if (el._swipeEvents) {
      el._swipeEvents += ' ' + eventName;
    } else {
      el._swipeEvents = eventName;
    }
    addEvent(el, eventName, callback);
  }

  function removeTouchEvent(el, touchName, fingers) {
    var eventName = 'touch' + touchName + fingers.toString();
    if (el._swipeEvents) {
      el._swipeEvents = el._swipeEvents.replace(new RegExp('(?:^|\s)' + eventName + '(?!\S)', 'g'), ' ');
      removeEvent(el, eventName);
    }
  }

  function onTouch(el) {
    var touchInfo = {
          start: {x: 0, y: 0},
          timeStamp: 0,
          tapCount: 0,
          fingers: 0
        };

    addEvent(
      el, 'touchstart',
      (function(touchInfo){
        return function (e) {
          var touches = e.changedTouches,
              i, maxItem;
          touchInfo.start.x = [];
          touchInfo.start.y = [];
          touchInfo.timeStamp = new Date().getTime();
          touchInfo.fingers = e.changedTouches.length;
          for (i = 0, maxItem = touches.length; i < maxItem; i++) {
            touchInfo.start.x.push(touches[i].clientX);
            touchInfo.start.y.push(touches[i].clientY);
          }
        };
      })(touchInfo)
    );

    addEvent(
      el, 'touchmove',
      (function(touchInfo){
        return function (e) {
          if (e.changedTouches.length != touchInfo.fingers) {
            touchInfo.fingers = 0;
          }
        };
      })(touchInfo)
    );

    addEvent(
      el, 'touchcancel',
      (function(touchInfo) {
        return function(e) {touchInfo.fingers = 0;};
      })(touchInfo)
    );

    addEvent(
      el, 'touchend',
      (function(touchInfo, swipeCallback) {
        return function(e) {
          var touches = e.changedTouches,
              fingers = (touches.length == touchInfo.fingers) ? touchInfo.fingers : 0,
              events = ['tap', 'swipeleft', 'swiperight', 'swipeup', 'swipedown'],
              detail = {
                detail: {
                  distX: [],
                  distY: [],
                  handled: false,
                  sourceTarget: e.target,
                  duration: new Date().getTime() - touchInfo.timeStamp
                },
                cancelable: true
              },
              cancelled = true,
              i, maxItem, touchevent, targetEvents;

          // Loop through the element's touch events to find the first
          // one that handles the current touch event.
          if (fingers) {
            for (i = 0, maxItem = touches.length; i < maxItem; i++) {
              detail.detail.distX.push(touches[i].clientX - touchInfo.start.x[i]);
              detail.detail.distY.push(touches[i].clientY - touchInfo.start.y[i]);
            }
            cancelled = true;
            targetEvents = e.currentTarget._swipeEvents.split(' ');
            for (i = 0, maxItem = targetEvents.length; i < maxItem && cancelled; i++) {
              touchevent = new CustomEvent(targetEvents[i], detail);
              e.currentTarget.dispatchEvent(touchevent);
              cancelled = touchevent.defaultPrevented || !touchevent.handled;
            }
          }
        };
      })(touchInfo)
    );
  }

  window.onSwipe = function(el, direction, callback, duration, threshold, restraint, fingers) {
    var constraints = {
          threshold: threshold || 150,
          restraint: restraint || 50,
          duration: duration || 300
        },
        eventName;

    if (isUndef(fingers)) {
      fingers = 1;
    }

    if(/^(left|right|up|down)$/.test(direction) === false || fingers < 0 || fingers > 5) {
      return;
    }

    if (!el._swipeEvents)
    {
      onTouch(el);
    }

    eventName = 'swipe' + direction;

    removeTouchEvent(el, eventName, fingers);
    addTouchEvent(
      el, eventName, fingers,
      (function (callback, constraints, eventName){
        return function (e) {
          var direction = 'none',
              detail = e.detail,
              distX, distY, isHorizSwipe, isVertSwipe, i, maxItem, tempDir;
          e.handled = true;
          if (detail.duration < constraints.duration) {
            for (i = 0, maxItem = detail.distX.length; i < maxItem; i++) {
              tempDir = null;
              distX = detail.distX[i];
              distY = detail.distY[i];
              isHorizSwipe = (
                Math.abs(distX) >= constraints.threshold &&
                Math.abs(distY) < constraints.restraint
              );
              isVertSwipe = (
                Math.abs(distY) >= constraints.threshold &&
                Math.abs(distX) < constraints.restraint
              );
              if (isHorizSwipe) {
                tempDir = (distX < 0) ? 'left' : 'right';
              } else if (isVertSwipe) {
                tempDir = (distY < 0) ? 'up' : 'down';
              } else {
                tempDir = 'none';
              }

              // Resolve direction
              direction = (i === 0 || tempDir == direction) ? tempDir : 'none';

              // If direction is None, stop checking directions.
              if (direction == 'none') {
                break;
              }
            }
          }
          if ('swipe' + direction == eventName) {
            callback(e);
          } else {
            e.preventDefault();
          }
        };
      })(callback || function(e){}, constraints, eventName)
    );
  };

  window.onTap = function(el, callback, duration, threshold, fingers) {
    var constraints = {
          threshold: threshold || 2,
          duration: duration || 300
        };

    if (isUndef(fingers)) {
      fingers = 1;
    }

    if (!el._swipeEvents)
    {
      onTouch(el);
    }

    eventName = 'tap';

    removeTouchEvent(el, eventName, fingers);
    addTouchEvent(
      el, eventName, fingers,
      (function (callback, constraints){
        return function (e) {
          var direction = 'none',
              detail = e.detail,
              isTap = false,
              distX, distY, i, maxItem;
          e.handled = true;
          if (detail.duration < constraints.duration) {
            for (i = 0, maxItem = detail.distX.length; i < maxItem; i++) {
              distX = detail.distX[i];
              distY = detail.distY[i];
              isTap = (
                Math.abs(distX) <= constraints.threshold,
                Math.abs(distY) <= constraints.threshold
              );

              if (!isTap)
              {
                break;
              }
            }
          }
          if (isTap) {
            callback(e);
          } else {
            e.preventDefault();
          }
        };
      })(callback || function(e){}, constraints)
    );
  };

  function removeTouch(el) {
    removeEvent(el, 'touchstart');
    removeEvent(el, 'touchmove');
    removeEvent(el, 'touchcancel');
    removeEvent(el, 'touchend');
  }

  window.removeSwipe = function(el, direction, fingers) {
    if(/^(left|right|up|down)$/.test(direction)) {
      removeTouchEvent(el, 'swipe' + direction, fingers);
      if (el._swipeEvents && el._swipeEvents.replace(/ /g,'') === '') {
        removeTouch(el);
      }
    }
  };

  window.removeTap = function(el, fingers) {
    removeTouchEvent(el, 'tap', fingers);
    if (el._swipeEvents && el._swipeEvents.replace(/ /g,'') === '') {
      removeTouch(el);
    }
  };

})(window);
