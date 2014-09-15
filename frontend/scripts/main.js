console.log('\'Allo \'Allo!');
"use strict";

var crow = {

  Front: {
    init: function () {
            var e = this;
            e.resfunct();
            e.mySlides();
            e.changeBg();
            e.gmap();
        },

        resfunct: function () {

          $(window).on('resize', function () {
            var viewportWidth = $(window).width();
            var viewportHeight = $(window).height(); 
            if (viewportWidth <= 1200 ) {
              $('.group-1').css('height',"auto"); 
              $(".container-inner").css("position","static");  
            }
            if (viewportWidth > 1200) {
              var parent = $('.group-1');  
              $(".container-inner").css("position","absolute");   
              parent.css('height', window.innerHeight);
            }
            if (viewportWidth > 1200 && viewportHeight <= 800 ) {
              $(".container-inner").css('bottom', "43px");  
            }
            else{
              $(".container-inner").css('bottom', "100px"); 
            }              
           }).resize();
              
       },
       gmap: function () {
          function init_map() {
            var var_location = new google.maps.LatLng(10.253934, 123.809859);
     
            var var_mapoptions = {
              center: var_location,
              zoom: 14
            };
     
            var var_marker = new google.maps.Marker({
                position: var_location,
                map: var_map,
                title:"Venice"});
     
            var var_map = new google.maps.Map(document.getElementById("map-container"),
                var_mapoptions);
     
            var_marker.setMap(var_map);    
     
          }
     
          google.maps.event.addDomListener(window, 'load', init_map);
      
       },
       mySlides: function(){
            $('#mySlide').slick({
              arrows: false,
              infinite: true,
              speed: 500,
              fade: true,
              autoplay: true,
              autoplaySpeed: 5000,
              pauseOnHover: false,
              cssEase: 'linear'
            });     
       },
       changeBg: function () {

          $(document).scroll(function () {
              var x = $(this).scrollTop(),
                  home = $('#home'),
                  portfolio = $('#portfolio');

              if (x >= home.offset().top && x < (home.offset().top + home.height())) {
                  $('.l-header,.navbar-collapse.in').css("background-color", "#fff");
                  $('.navbar-nav li a').css("color","#302e2e");
                  $('.navbar-nav li a').removeClass("c-white");
                  $('.navbar-nav li a').addClass("c-black");
                  $('.nav-toggle').removeClass("c-white");
                  $('.nav-toggle').addClass("c-black");                  
                  if (!Modernizr.svg) {
                    $(".navbar-brand img[src$='images/logo.png']")
                      .attr("src", "images/logo.png");
                  }
                  else{
                     $('.navbar-brand img').attr("src","images/logo.svg");
                  }
          
              }
              if (x >= portfolio.offset().top && x < (portfolio.offset().top + portfolio.height() + 79)) {
                  $('.l-header,.navbar-collapse.in').css("background-color", "#181818");
                  $('.navbar-nav li a').css("color","#ffffff");
                  $('.navbar-nav li a').removeClass("c-black");
                  $('.navbar-nav li a').addClass("c-white");                  
                  $('.nav-toggle').removeClass("c-black");
                  $('.nav-toggle').addClass("c-white"); 
                  
                  if (!Modernizr.svg) {
                    $(".navbar-brand img[src$='images/logo-inverse.svg']")
                      .attr("src", "images/logo-inverse.png");
                  } 
                  if (!Modernizr.svg) {
                    $(".navbar-brand img[src$='images/logo-inverse.png']")
                      .attr("src", "images/logo.png");
                  }
                  else{
                     $('.navbar-brand img').attr("src","images/logo-inverse.svg");
                  }                                   
              }
          });        
       }      
  }
}




