% include('layout/header.tpl', title='Page Title')
<div class='left map-container'>
    <div class='map' id='map'></div>
    % if locations:
        <p>{{locations}}</p>
    % end
</div>
<div class='left posts'>
% if videos:
    % for video in videos:
    <a class="embedly-card" data-card-chrome="0" href="{{video}}"></a>
    <script async src="//cdn.embedly.com/widgets/platform.js" charset="UTF-8"></script>
% end
</div>
<div class='left hashtags'>
% if hashtags:
    % for hashtag in hashtags:
    <a href='#'>{{hashtag}}</a>
% end
</div>
<script src='https://api.tiles.mapbox.com/mapbox.js/v2.1.4/mapbox.js'></script>
<script type="text/javascript" src="http://maps.stamen.com/js/tile.stamen.js?v1.3.0"></script>
<link href='https://api.tiles.mapbox.com/mapbox.js/v2.1.4/mapbox.css' rel='stylesheet' />
<script>
    var layer = new L.StamenTileLayer("toner");
    var map = new L.Map('map', {
        center: new L.LatLng(40.7127671,-74.0103888),
        zoom: 12
    });
    map.addLayer(layer);
</script>
% include('layout/footer.tpl')