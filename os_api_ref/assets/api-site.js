(function() {
    // the list of expanded element ids
    var expanded = [];
    // whether we should sync expand changes with the location
    // url. We need to make this false during large scale
    // operations because we're using the history API, which is
    // expensive. So a bulk expand turns this off, expands
    // everything, turns it back on, then does a history sync.
    var should_sync = true;

    $(document).ready(function() {
        // Change the text on the expando buttons when
        // appropriate. This also add or removes them to the list of
        // expanded sections, and then syncs that list to the history
        // after such a change.
        $('.api-detail')
            .on('hide.bs.collapse', function(e) {
                processButton(this, 'detail');
                var index = expanded.indexOf(this.id);
                if (index > -1) {
                    expanded.splice(index, 1);
                }
                sync_expanded();
            })
            .on('show.bs.collapse', function(e) {
                processButton(this, 'close');
                expanded.push(this.id);
                sync_expanded();
            });

        // Expand the world. Wires up the expand all button, it turns
        // off the sync while it is running to save the costs with the
        // history API.
        var expandAllActive = true;
        $('#expand-all').click(function () {
            should_sync = false;
            if (expandAllActive) {
                expandAllActive = false;
                $('.api-detail').collapse('show');
                $('#expand-all').attr('data-toggle', '');
                $(this).text('Hide All');
            } else {
                expandAllActive = true;
                $('.api-detail').collapse('hide');
                $('#expand-all').attr('data-toggle', 'collapse');
                $(this).text('Show All');
            }
            should_sync = true;
            sync_expanded();
        });

        // if there is an expanded parameter passed in a url, we run
        // through and expand all the appropriate things.
        if (window.location.search.substring(1).indexOf("expanded") > -1) {
            should_sync = false;
            var parts = window.location.search.substring(1).split('&');
            for (var i = 0; i < parts.length; i++) {
                var keyval = parts[i].split('=');
                if (keyval[0] == "expanded" && keyval[1]) {
                    var expanded_ids = keyval[1].split(',');
                    for (var j = 0; j < expanded_ids.length; j++) {
                        $('#' + expanded_ids[j]).collapse('show');
                    }
                }
            }
            should_sync = true;
            // This is needed because the hash *might* be inside a
            // collapsed section.
            //
            // NOTE(sdague): this doesn't quite seem to work while
            // we're changing the rest of the document.
            $(document.body).scrollTop($(window.location.hash).offset().top);
        }

        // Wire up microversion selector
        $('.mv_selector').on('click', function(e) {
            var version = e.currentTarget.innerHTML;
            // flip what is active
            $(this).addClass('active').siblings().removeClass('active');
            if (version == "All") {
                reset_microversion();
            } else {
                set_microversion(version);
            }
        });
    });
    /**
     * Helper function for setting the text, styles for expandos
     */
    function processButton(button, text) {
        $('#' + $(button).attr('id') + '-btn').text(text)
            .toggleClass('btn-info')
            .toggleClass('btn-default');
    }

    // Take the expanded array and push it into history. Because
    // sphinx is building css appropriate ids, they should not have
    // any special characters we need to encode. So we can simply join
    // them into a comma separated list.
    function sync_expanded() {
        if (should_sync) {
            var url = UpdateQueryString('expanded', expanded.join(','));
            history.pushState('', 'new expand', url);
        }
    }


    // Generically update the query string for a url. Credit to
    // http://stackoverflow.com/questions/5999118/add-or-update-query-string-parameter
    // for making this properly generic.
    function UpdateQueryString(key, value, url) {
        if (!url) url = window.location.href;
        var re = new RegExp("([?&])" + key + "=.*?(&|#|$)(.*)", "gi"),
            hash;

        if (re.test(url)) {
            if (typeof value !== 'undefined' && value !== null)
                return url.replace(re, '$1' + key + "=" + value + '$2$3');
            else {
                hash = url.split('#');
                url = hash[0].replace(re, '$1$3').replace(/(&|\?)$/, '');
                if (typeof hash[1] !== 'undefined' && hash[1] !== null)
                    url += '#' + hash[1];
                return url;
            }
        }
        else {
            if (typeof value !== 'undefined' && value !== null) {
                var separator = url.indexOf('?') !== -1 ? '&' : '?';
                hash = url.split('#');
                url = hash[0] + separator + key + '=' + value;
                if (typeof hash[1] !== 'undefined' && hash[1] !== null)
                    url += '#' + hash[1];
                return url;
            }
            else
                return url;
        }
    }

    // Set the Y value of the microversion to turn on / off visibility
    // of components.
    function set_microversion(number) {
        var major = number.split(".")[0];
        var micro = number.split(".")[1];
        for (var i = os_min_mv; i <= os_max_mv; i++) {
            var max_class = ".rp_max_ver_" + major + "_" + i;
            var min_class = ".rp_min_ver_" + major + "_" + i;
            if (i < micro) {
                $(max_class).hide(400);
                $(min_class).show(400);
            } else if (i >= micro) {
                $(min_class).hide(400);
                $(max_class).show(400);
            }
        }
    }

    function reset_microversion() {
        $('[class^=rp_min_ver]').show(400);
        $('[class^=rp_max_ver]').show(400);
    }


    $(document).ready(function(){
        $('#mv_select').combobox({appendId: '-visable'});
        $('#mv_select').on('change', function() {
            var version = this.value;
            if (version == "") {
                reset_microversion();
            } else {
                set_microversion(version);
            }
        });
    });


})();
