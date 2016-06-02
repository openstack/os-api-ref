(function() {

    $(document).ready(function() {
        // Change the text on the expando buttons when appropriate
        $('.api-detail')
            .on('hide.bs.collapse', function(e) {
                processButton(this, 'detail');
            })
            .on('show.bs.collapse', function(e) {
                processButton(this, 'close');
            });

        var expandAllActive = true;
        // Expand the world
        $('#expand-all').click(function () {
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
            }});

        // if ?expand_all is in the query string, then expand all
        // sections. This is useful for linking to nested elements, which
        // only work if that element is expanded.
        if (window.location.search.substring(1).indexOf("expand_all") > -1) {
            $('#expand-all').click();
        }

    });
    /**
     * Helper function for setting the text, styles for expandos
     */
    function processButton(button, text) {
        $('#' + $(button).attr('id') + '-btn').text(text)
            .toggleClass('btn-info')
            .toggleClass('btn-default');
    }
})();
