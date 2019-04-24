'use strict';

/* Filters */

angular.module('customFilters', [])
.filter('dateInMillis', function() {
  return function(dateString) {
    return Date.parse(dateString);
  };
})
.filter('trustUrl', function ($sce) {
  return function(url) {
    return $sce.trustAsResourceUrl(url);
  };
});;
