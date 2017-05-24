// = require_tree ./govuk

(function(){
  // stop everything being called twice if loaded with turbolinks and page load.
  var initialised = false;

  function accordions(){
    var accordionsAllOpen = false;

    $(".accordion__header").click(function(e){
        var body = $(e.currentTarget).parent().find(".accordion__body")
        $(e.currentTarget).find(".plus-minus-icon").toggleClass("open")
        $(body).toggle()
    })


    $(".accordion__body").hide()

    $("#accordion-all-control").click(function(){
    a= $(".plus-minus-icon").filter(function(_,icon) {
        return icon.classList.contains("open")
      })

      if(a.size() == 0){
        console.log("called")
        $(".plus-minus-icon").addClass("open")
        $("#accordion-all-control").text("Close all")
        $(".accordion__body").show()
      } else {
        $(".plus-minus-icon").removeClass("open")
        $("#accordion-all-control").text("Open all")
        $(".accordion__body").hide()
      }
    })
  }
  $(document).ready(accordions)
}())

// Stageprompt 2.0.1
//
// See: https://github.com/alphagov/stageprompt
//
// Stageprompt allows user journeys to be described and instrumented
// using data attributes.
//
// Setup (run this on document ready):
//
//   GOVUK.performance.stageprompt.setupForGoogleAnalytics();
//
// Usage:
//
//   Sending events on page load:
//
//     <div id="wrapper" class="service" data-journey="pay-register-birth-abroad:start">
//         [...]
//     </div>
//
//   Sending events on click:
//
//     <a class="help-button" href="#" data-journey-click="stage:help:info">See more info...</a>

;(function (global) {
  'use strict'

  var $ = global.jQuery
  var GOVUK = global.GOVUK || {}

  GOVUK.performance = GOVUK.performance || {}

  GOVUK.performance.stageprompt = (function () {
    var setup, setupForGoogleAnalytics, splitAction

    splitAction = function (action) {
      var parts = action.split(':')
      if (parts.length <= 3) return parts
      return [parts.shift(), parts.shift(), parts.join(':')]
    }

    setup = function (analyticsCallback) {
      var journeyStage = $('[data-journey]').attr('data-journey')
      var journeyHelpers = $('[data-journey-click]')

      if (journeyStage) {
        analyticsCallback.apply(null, splitAction(journeyStage))
      }

      journeyHelpers.on('click', function (event) {
        analyticsCallback.apply(null, splitAction($(this).data('journey-click')))
      })
    }

    setupForGoogleAnalytics = function () {
      setup(GOVUK.performance.sendGoogleAnalyticsEvent)
    }

    return {
      setup: setup,
      setupForGoogleAnalytics: setupForGoogleAnalytics
    }
  }())

  GOVUK.performance.sendGoogleAnalyticsEvent = function (category, event, label) {
    global._gaq.push(['_trackEvent', category, event, label, undefined, true])
  }

  global.GOVUK = GOVUK
})(window)