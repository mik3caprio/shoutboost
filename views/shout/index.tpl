% include('layout/header.tpl', title='Page Title')
% if videos:
    <h1>hi</h1>
   <!-- <embedly code src={{each_video}}</> -->
% else:
   <!-- <h1>No videos</h1> -->
% end


    <div class="container">
         	<div class="container-map">
                <div class="block-map"></div>
            </div>
            <div class="container-posts">
                <div class="block"></div>
                <div class="block"></div>
                <div class="block"></div>
                <div class="block"></div>
            </div>
            <div class="container-hashtags">
                 <div class="block-2"></div>
                <div class="block-2"></div>
                <div class="block-2"></div>
                <div class="block-2"></div>
                <div class="block-2"></div>
                <div class="block-2"></div>
                <div class="block-2"></div>
            </div>
    </div>

% include('layout/footer.tpl')
