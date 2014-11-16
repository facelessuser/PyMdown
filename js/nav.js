(function() {
    function initNav() {
      // Cache selectors for faster performance.
      var win = window,
          doc = document,
          toc = doc.querySelectorAll(".toc")[0],
          content = doc.querySelectorAll(".content")[0],
          menu = doc.querySelectorAll(".menu")[0],
          md = doc.querySelectorAll(".markdown-body")[0],
          showToc, hideToc;

      if (toc) {
        // Move toc from markdown to the content div
        content.insertBefore(toc, content.firstChild.nextSibling);
        content.sticky = false;

        // Show navbar
        showToc = function(e) {
          addClass(menu, 'hidden');
          addClass(content, 'navbar');
        }

        // Hide navbar on leaving
        hideToc = function(e) {
          removeClass(menu, 'hidden');
          removeClass(content, 'navbar');
        }

        swipeHideToc = function(e) {
          if (/(?:^|\s)navbar(?!\S)/.test(content.className) && !isChildOf(toc, e.detail.sourceTarget)) {
            hideToc();
          } else {
            e.preventDefault();
          }
        }

        // Setup events
        addEvent(menu, 'click', showToc);
        addEvent(toc, 'mouseleave', hideToc);
        if ("ontouchstart" in doc.documentElement) {
          onSwipe(content, 'right', showToc);
          onSwipe(content, 'left', swipeHideToc);
          onTap(content, swipeHideToc);
        }

        addEvent(
          win, 'scroll',
          function (ev) {
            // Mark content as sticky so that nav buttons stick to top of viewport
            var windowTop = (win.pageYOffset || doc.scrollTop) - (doc.clientTop || 0);
            var divTop = md.offsetTop;
            var showMenu = windowTop > divTop;
            if (!content.sticky && showMenu) {
              addClass(content, 'sticky');
              content.sticky = true;
            }
            else if (content.sticky && !showMenu) {
              removeClass(content, 'sticky');
              content.sticky = false;
            }
          }
        );
      } else {
        addClass(menu, 'hidden');
      }
    }

    onReady(initNav);
})();
