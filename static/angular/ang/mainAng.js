'use strict';

angular.module('mud', ['angularFlaskServices','ngRoute','ngSanitize'])
	.run(function($rootScope, $templateCache) {
		 $rootScope.$on('$routeChangeStart', function(event, next, current) {
         if (typeof(current) !== 'undefined'){
             $templateCache.remove(current.templateUrl);
         }
     });

		 $rootScope.navigateOut = function(url) {
        window.location = url;
     };
	})
	.config(['$routeProvider', '$locationProvider', '$interpolateProvider', '$httpProvider', '$sceDelegateProvider',
		function($routeProvider, $locationProvider, $interpolateProvider,$httpProvider,$sceDelegateProvider) {
		$routeProvider
		.when('/', {
			templateUrl: '/static/partials/index.html',
			controller: indexController
		})
		.when('/dungeon/:cat1', {
			templateUrl: '/static/partials/mud.html',
			controller: mudController
		})
    $interpolateProvider.startSymbol('{a');
    $interpolateProvider.endSymbol('a}');
		$locationProvider.html5Mode({
		  enabled: true,
		  requireBase: false
		});
		$httpProvider.defaults.headers.get = {};
		$httpProvider.defaults.headers.get['Cache-Control'] = 'no-cache';
    $httpProvider.defaults.headers.get['Pragma'] = 'no-cache';
	}])
	.directive('onFinishRender', function ($timeout) {
	  return {
	      restrict: 'A',
	      link: function (scope, element, attr) {
	          if (scope.$last === true) {
	              $timeout(function () {
	                  scope.$emit(attr.onFinishRender);
	              });
	          }
	      }
	  }
	})
	.directive("jdenticonValue", function() {
    return {
      restrict: "A",
      link: function(scope, el, attrs){
        jdenticon.update(el[0], attrs.jdenticonValue);
      }
    };
  });
