$(function() {

  $(".sketchfab-connect-watch").on("change keyup", function() {
      console.log("yo");
      var url = $(".sketchfab-connect-button")[0].getAttribute("href");
      var next_url = "/?create=1&instagram_username="+$("#instagram_username").val() + "&imgfab_layout=" +$("#imgfab_layout").val() + "#start";
      url = url.replace(/next=.*/, "next="+encodeURIComponent(next_url));
      $(".sketchfab-connect-button")[0].setAttribute("href", url);
  });

  $("#go_create").on("click", function() {
      create_gallery();
  });

  var create_gallery = function() {

    var params = {
      "layout": $("#imgfab_layout").val(),
      "brand": "instamuseum"
    };

    if ($("#facebook_albums").val()) {
      params["source_name"] = "FacebookAlbum";
      params["source_data"] = {
        "album": $("#facebook_albums").val()
      }
    } else {

      if (!$("#instagram_username").val()) {
          return alert("Please enter an Instagram username!");
      }

      params["source_name"] = "InstagramFeed";
      params["source_data"] = {
        "username": $("#instagram_username").val()
      }
    }

    $("#model_link").hide();
    $("#go_create").hide();
    $("#model_loading").show();

    $.ajax({
      url: "/create_job",
      data: {
        "path": "process.Create3dGallery",
        "params": JSON.stringify(params)
      },
      method:"POST",
      dataType: "json",
      success: function(data) {
        var job_id = data.job_id;

        poll_for_model(job_id);

        // Trigger some fake processing events to make the user wait a bit.
        setTimeout(function() {
          $(".model_loading_status").html("Downloading images from Instagram...");
        }, 5000);

        setTimeout(function() {
          $(".model_loading_status").html("Building 3D model...");
        }, 20000);

        setTimeout(function() {
          $(".model_loading_status").html("Exporting Blender file...");
        }, 40000);

        setTimeout(function() {
          $(".model_loading_status").html("Uploading to Sketchfab...");
        }, 60000);

        setTimeout(function() {
          $(".model_loading_status").html("Waiting for Sketchfab to process the model...");
        }, 90000);

      }
    });

    // Remove parameters from the URL
    if (history && history.pushState) {
      setTimeout(function() {
          history.pushState({}, "Instamuseum", "/");
      }, 2000);

    }

  };

  var poll_for_model = function(job_id) {
    $.getJSON("/get_job?job_id="+job_id, function(data) {
      if (data.status == "success") {

        $("#model_embed").html(
          '<br/><iframe width="640" height="480" src="'+data.result.model_url+'/embed?autostart=1" frameborder="0" allowfullscreen mozallowfullscreen="true" webkitallowfullscreen="true" onmousewheel=""></iframe><br/><br/>'
          );

        $(".model_share").html('<iframe src="https://www.facebook.com/plugins/share_button.php?href='+encodeURIComponent(data.result.model_url)+'&layout=button_count&mobile_iframe=false&width=87&height=20&appId" width="87" height="20" style="border:none;overflow:hidden" scrolling="no" frameborder="0" allowTransparency="true"></iframe><br/>');

        $(".model_link_a").html(data.result.model_url);
        $(".model_link_a").attr("href", data.result.model_url);
        $("#model_link").show();
        $("#model_loading").hide();

      } else if (data.status == "failed") {
        $("#model_loading").hide();
        alert("Sorry, there was an error creating your model. Are you sure that Instagram account exists?");
      } else {
        setTimeout(function() {
          poll_for_model(job_id)
        }, 5000);
      }
    });
  }

});